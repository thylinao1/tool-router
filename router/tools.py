"""Route registry and the three mocked tools.

A RouteSpec carries everything every router needs to know about a route:
  * examples  -> used by the embedding router as labelled prototypes
  * patterns  -> used by the rule router (name, regex, weight)
  * exclusions-> regexes that veto the route in the rule router
  * handler   -> callable that executes the tool (None for the direct route)

Adding a tool means registering one more RouteSpec. No router code changes.
"""

from __future__ import annotations

import ast
import hashlib
import math
import operator
import re
from dataclasses import dataclass, field
from typing import Callable, Optional

from .schema import DIRECT


@dataclass
class ToolResult:
    status: str           # "ok" | "error" | "needs_input"
    text: str


@dataclass
class RouteSpec:
    name: str
    description: str      # noun phrase used in clarification questions, e.g. "a calculation"
    examples: list[str]
    patterns: list[tuple[str, str, float]] = field(default_factory=list)   # (rule_name, regex, weight)
    exclusions: list[tuple[str, str]] = field(default_factory=list)        # (rule_name, regex)
    handler: Optional[Callable[[str], ToolResult]] = None

    @property
    def is_tool(self) -> bool:
        return self.handler is not None


class ToolRegistry:
    def __init__(self) -> None:
        self._routes: dict[str, RouteSpec] = {}

    def register(self, spec: RouteSpec) -> "ToolRegistry":
        if spec.name in self._routes:
            raise ValueError(f"route {spec.name!r} is already registered")
        if not spec.examples:
            raise ValueError(f"route {spec.name!r} needs at least one example utterance")
        self._routes[spec.name] = spec
        return self

    def get(self, name: str) -> RouteSpec:
        return self._routes[name]

    def names(self) -> list[str]:
        return list(self._routes)

    def tool_names(self) -> list[str]:
        return [n for n, s in self._routes.items() if s.is_tool]

    def __iter__(self):
        return iter(self._routes.values())


# --------------------------------------------------------------------------
# calculator (real, sandboxed arithmetic; only its scope is limited)
# --------------------------------------------------------------------------

_WORD_OPS = [
    (r"\bmultiply\s+(\d+(?:\.\d+)?)\s+by\s+", r"\1*"),
    (r"\bsubtract\s+(\d+(?:\.\d+)?)\s+from\s+(\d+(?:\.\d+)?)", r"\2-\1"),
    (r"\bsquare root of\s*", "sqrt("),
    (r"\bsqrt\s+(?=\d)", "sqrt("),
    (r"\bto the power of\b", "**"),
    (r"\^", "**"),
    (r"\bsquared\b", "**2"),
    (r"\bcubed\b", "**3"),
    (r"\b(times|multiplied by)\b|×", "*"),
    (r"(?<=\d)\s*x\s*(?=\d)", "*"),
    (r"\bplus\b", "+"),
    (r"\bminus\b", "-"),
    (r"\bdivided by\b|÷", "/"),
    (r"(?<!\d)(\d+(?:\.\d+)?)\s*(?:%|percent)\s+of\s+", r"\1/100*"),
    (r"(?<=\d)\s*(%|percent)", "/100"),
    (r",(?=\d{3})", ""),   # 1,000 -> 1000
]

_ALLOWED_BINOPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_ALLOWED_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_ALLOWED_FUNCS = {"sqrt": math.sqrt}
_MAX_POW = 1000
_MAX_MAGNITUDE = 1e100
_MAX_EXPR_CHARS = 200


def extract_expression(query: str) -> Optional[str]:
    """Turn '15% of 80' or 'square root of 144' into a plain arithmetic string."""
    text = query.lower()
    for pattern, repl in _WORD_OPS:
        text = re.sub(pattern, repl, text)
    runs = re.findall(r"(?:sqrt\(|[\d.+\-*/()\s])+", text)
    runs = [r.strip() for r in runs if re.search(r"\d", r)]
    if not runs:
        return None
    expr = max(runs, key=lambda r: sum(c.isdigit() for c in r))
    expr = expr.strip(" .+*/")
    expr += ")" * (expr.count("(") - expr.count(")"))
    return expr or None


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        left, right = _safe_eval(node.left), _safe_eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > _MAX_POW:
            raise ValueError("exponent too large")
        value = _ALLOWED_BINOPS[type(node.op)](left, right)
        if abs(value) > _MAX_MAGNITUDE:
            raise ValueError("result too large")
        return value
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return _ALLOWED_UNARY[type(node.op)](_safe_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCS:
        return _ALLOWED_FUNCS[node.func.id](*[_safe_eval(a) for a in node.args])
    raise ValueError(f"unsupported syntax: {ast.dump(node)[:40]}")


def calculator(query: str) -> ToolResult:
    expr = extract_expression(query)
    if not expr or not re.search(r"[+\-*/(]", expr):
        return ToolResult("error", "no arithmetic expression found")
    if len(expr) > _MAX_EXPR_CHARS:
        return ToolResult("error", f"expression longer than {_MAX_EXPR_CHARS} characters")
    try:
        value = _safe_eval(ast.parse(expr, mode="eval"))
        if isinstance(value, complex):
            raise ValueError("no real result")
        shown = int(value) if float(value).is_integer() else round(value, 6)
    except (ValueError, SyntaxError, ZeroDivisionError, TypeError, OverflowError,
            RecursionError, MemoryError) as exc:
        return ToolResult("error", f"could not evaluate {expr!r}: {exc}")
    return ToolResult("ok", f"{expr} = {shown}")


# --------------------------------------------------------------------------
# weather (mocked)
# --------------------------------------------------------------------------

_CITY_WEATHER = {
    "singapore": (31, "thunderstorms", 78), "london": (17, "overcast", 70),
    "tokyo": (26, "partly cloudy", 60), "new york": (22, "clear", 45),
    "paris": (19, "light rain", 72), "dubai": (41, "sunny", 18),
    "sydney": (15, "windy", 55), "vancouver": (14, "drizzle", 80),
    "hong kong": (29, "humid", 82), "berlin": (16, "cloudy", 65),
}
_LOCATION_RE = re.compile(r"\b(?:in|at|for|around|near)\s+([A-Z][\w.'-]*(?:\s+[A-Z][\w.'-]*)*)")
_CONDITIONS = ["sunny", "cloudy", "light rain", "clear", "foggy", "windy"]


def extract_location(query: str) -> Optional[str]:
    m = _LOCATION_RE.search(query)
    if m:
        return m.group(1).strip()
    low = query.lower()
    for city in _CITY_WEATHER:
        if re.search(rf"\b{re.escape(city)}\b", low):
            return city.title()
    return None


def weather(query: str) -> ToolResult:
    location = extract_location(query)
    if not location:
        return ToolResult("needs_input", "Which location would you like the weather for?")
    key = location.lower()
    if key in _CITY_WEATHER:
        temp, cond, hum = _CITY_WEATHER[key]
    else:  # deterministic pseudo-data so unknown places still get a stable answer
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        temp, cond, hum = 5 + h % 30, _CONDITIONS[h % len(_CONDITIONS)], 30 + h % 60
    return ToolResult("ok", f"Weather in {location}: {temp}°C, {cond}, humidity {hum}% (mock data)")


# --------------------------------------------------------------------------
# web_search (mocked)
# --------------------------------------------------------------------------

_CANNED_RESULTS = [
    (r"formula 1|\bf1\b|grand prix", "Formula 1: the most recent Grand Prix was won by the driver starting from pole; full results on formula1.com."),
    (r"bitcoin|ethereum|crypto|btc|eth", "Crypto prices move by the minute; the live quote is on coinmarketcap.com."),
    (r"openai|anthropic|google|microsoft|spacex", "Latest company news: see the newsroom and recent press coverage."),
    (r"president|prime minister|ceo|mayor", "Current officeholder: see the official government or company site for the up-to-date name."),
    (r"usd|sgd|eur|exchange rate|convert", "Live exchange rates are published by xe.com and your bank."),
]


def web_search(query: str) -> ToolResult:
    low = query.lower()
    for pattern, snippet in _CANNED_RESULTS:
        if re.search(pattern, low):
            return ToolResult("ok", f"Top result for {query!r} (mock search): {snippet}")
    return ToolResult("ok", f"Top result for {query!r} (mock search): no canned snippet; a real engine would return live pages here.")


# --------------------------------------------------------------------------
# default registry
# --------------------------------------------------------------------------

def build_default_registry() -> ToolRegistry:
    reg = ToolRegistry()

    reg.register(RouteSpec(
        name="calculator",
        description="a calculation",
        examples=[
            "What is 17 times 23?",
            "Calculate 1024 divided by 8",
            "How much is 3.5 plus 2.25?",
            "Compute 2 to the power of 10",
            "What's 20 percent of 350?",
            "Square root of 625",
            "(45 + 55) * 3",
            "What is 999 minus 123?",
            "Work out 128 / 4 + 6",
            "What does 9 squared equal?",
            "Multiply 12 by 12",
            "Subtract 40 from 100",
            "How many minutes are in three days?",
            "What is a quarter of two hundred?",
        ],
        patterns=[
            ("arithmetic_expression", r"(?<!\d)\d+(?:\.\d+)?\s*[-+*/x×÷^%]\s*\d", 0.95),
            ("math_verb", r"\b(calculate|compute|sum of|product of|square root|sqrt|percent of|% of|times|plus|minus|divided by|multiplied by|to the power)\b", 0.7),
            ("what_is_number", r"\b(what('| i)s|how much is)\s+\d", 0.6),
        ],
        exclusions=[
            ("conceptual_math", r"\b(derivative|integral|prove|theorem|explain|how (do|to|can) (i |you )?calculate|formula for)\b"),
        ],
        handler=calculator,
    ))

    reg.register(RouteSpec(
        name="weather",
        description="a weather report for a location",
        examples=[
            "What's the weather like in Tokyo right now?",
            "Is it going to rain in London tomorrow?",
            "Do I need an umbrella in Seattle today?",
            "How cold is it in Moscow?",
            "Give me the forecast for Paris this weekend",
            "Current temperature in Dubai",
            "Will it snow in Toronto tonight?",
            "Is it sunny in Sydney at the moment?",
            "How humid is it in Bangkok today?",
            "Is it chilly outside in Berlin this morning?",
            "Any storms expected in Miami this week?",
            "Weather report for Hong Kong",
            "Is it going to rain tomorrow?",
            "What's the forecast for this weekend?",
            "Do I need a jacket today?",
            "How hot will it get this afternoon?",
        ],
        patterns=[
            ("weather_word", r"\b(weather|forecast|temperature|rain(ing|y)?|snow(ing)?|humid(ity)?|sunny|cloudy|windy|storms?|umbrella|how (hot|cold|warm|chilly))\b", 0.85),
        ],
        exclusions=[
            ("not_a_place", r"\b(boiling|melting|sun|star|oven|cpu|gpu|body temperature|fever|mars|moon|jupiter|venus)\b"),
            ("about_weather_science", r"\b(explain|how (do|does) .*(work|forecast)|models?)\b"),
            ("creative_writing", r"\b(write|compose|poem|haiku|story|essay|song)\b"),
            ("unit_conversion", r"\b(celsius|fahrenheit|kelvin)\b.*\b(in|to|into)\s+(celsius|fahrenheit|kelvin)\b"),
        ],
        handler=weather,
    ))

    reg.register(RouteSpec(
        name="web_search",
        description="a web search for current information",
        examples=[
            "Who won the NBA finals this year?",
            "What's the latest news about SpaceX?",
            "Current price of Bitcoin",
            "Who is the current CEO of Microsoft?",
            "What happened in the election yesterday?",
            "Search for reviews of the newest iPhone",
            "When is the next Marvel movie coming out?",
            "Latest Premier League standings",
            "What is the exchange rate between USD and EUR today?",
            "Find recent articles about quantum computing breakthroughs",
            "Which team is leading the World Cup qualifiers?",
            "Look up today's headlines",
            "Best rated restaurants near Times Square",
            "Are there any train delays in Amsterdam today?",
            "What events are on in Melbourne this weekend?",
        ],
        patterns=[
            ("recency", r"\b(latest|current(ly)?|recent|news|headlines|breaking)\b", 0.7),
            ("time_now", r"\b(today'?s?|tonight|yesterday|this (week|month|year)|right now)\b", 0.4),
            ("who_won", r"\bwho (won|is winning|is the (current|new))\b", 0.8),
            ("market", r"\b(price|stock|exchange rate|worth|score|standings)\b", 0.6),
            ("search_verb", r"\b(search|look up|google|find (out|me)|find recent)\b", 0.8),
            ("officeholder", r"\b(president|prime minister|ceo|champion|mayor)\b", 0.5),
        ],
        handler=web_search,
    ))

    reg.register(RouteSpec(
        name=DIRECT,
        description="a general answer from the model",
        examples=[
            "Explain how neural networks learn",
            "What is the difference between a list and a tuple in Python?",
            "Write a short poem about the ocean",
            "Summarize the plot of Romeo and Juliet",
            "How does photosynthesis work?",
            "Give me tips for a job interview",
            "What does the term 'idempotent' mean?",
            "Translate 'good morning' into Spanish",
            "Why is the sky blue?",
            "Write a Python function that reverses a string",
            "What are the pros and cons of remote work?",
            "Tell me a joke about programmers",
            "Hi there",
            "Who wrote Pride and Prejudice?",
            "What is the largest planet in the solar system?",
            "How many continents are there?",
            "What year did World War II end?",
            "What is the population of Brazil?",
            "Recommend things to do in Lisbon",
            "What language do they speak in Switzerland?",
        ],
        patterns=[
            ("explain", r"\b(explain|describe|what does .* mean|how (does|do) .* work|why (do|does|is|are)|difference between|define|definition of|tell me about|summarize)\b", 0.7),
            ("creative", r"\b(write|compose|draft|poem|haiku|story|essay|joke|email)\b", 0.8),
            ("code", r"\b(python|javascript|code|function|regex|sql)\b", 0.6),
            ("advice", r"\b(should i|recommend|opinion|better than|pros and cons|tips)\b", 0.6),
            ("language_task", r"\b(translate|rewrite|proofread|paraphrase)\b", 0.8),
            ("greeting", r"^\s*(hi|hello|hey|thanks|thank you)\b", 0.9),
        ],
        handler=None,
    ))
    return reg
