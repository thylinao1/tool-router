"""Multi-step routing: split a compound request into parts and route each part.

The splitter is conservative by design. It only splits on conjunctions when
every resulting part reads like a request on its own (starts with a question or
command word, or contains arithmetic). "TCP and UDP" therefore stays together,
while "weather in Tokyo and what is 12 * 7" becomes two steps.

Dependent steps are supported for numeric references only. When a later step
refers to "it", "that" or "the result" in an arithmetic context, the number
produced by the previous step's answer is substituted before routing:
"search for the Bitcoin price and multiply it by 0.5" runs the search, takes
the first number from its answer, and routes "multiply 60000 by 0.5" to the
calculator. If the previous answer contains no number the step is reported as
unresolved instead of guessed.
"""

from __future__ import annotations

import re

from .schema import RoutingDecision

_SPLIT_RE = re.compile(r"(?:,\s*)?\b(?:and then|and also|and|then|also)\b\s*|;\s*", re.I)
_REQUEST_START = re.compile(
    r"^(what|what's|whats|who|who's|when|where|which|how|is|are|do|does|did|can|could|will|would|"
    r"should|calculate|compute|tell|find|search|look|convert|give|check|explain|describe|write|"
    r"summarize|translate|show|get|list|define|add|multiply|divide|subtract|halve|double|triple|"
    r"square|take|please)\b", re.I)
# references to the previous step's result; determiner phrases come first so the noun is consumed too
_REFERENCE = re.compile(
    r"\b(the result|the answer|the total|(?:that|this) (?:number|amount|price|value|figure|result)|it|that|this)\b", re.I)
# arithmetic vocabulary, or an operator next to a digit (a bare hyphen inside "t-shirt" does not count)
_ARITHMETIC_CONTEXT = re.compile(
    r"\b(multiply|multiplied|divide|divided|add|subtract|plus|minus|times|half|halve|double|triple|"
    r"square|squared|percent|% of)\b|\d\s*[-+*/^]|[-+*/^]\s*\d", re.I)
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?(?:[eE][-+]?\d+)?")
_ARITHMETIC = re.compile(r"\d\s*[-+*/x×÷^]\s*\d")
MAX_STEPS = 4


def looks_like_request(part: str) -> bool:
    part = part.strip()
    return bool(part) and (bool(_REQUEST_START.match(part)) or bool(_ARITHMETIC.search(part)))


def split_compound_query(query: str) -> list[str]:
    parts = [p.strip(" ,?.") for p in _SPLIT_RE.split(query)]
    parts = [p for p in parts if p]
    if 1 < len(parts) <= MAX_STEPS and all(looks_like_request(p) for p in parts):
        return parts
    return [query]


def extract_number(text: str):
    """The number a previous answer produced: the value after '=' if present, else the first number."""
    m = re.search(r"=\s*(" + _NUMBER.pattern + ")", text)
    value = m.group(1) if m else (_NUMBER.search(text) or [None])[0]
    if value is None:
        return None
    value = value.replace(",", "")
    if "e" in value.lower():   # exponent notation: write it out so the calculator and the reader see the same number
        value = format(float(value), "f").rstrip("0").rstrip(".") or "0"
    return value


def resolve_reference(step: str, previous_answer):
    """Substitute the previous step's number for a reference (see _REFERENCE) in an arithmetic step.

    Returns (text, status, value) with status "none" (nothing to resolve), "resolved"
    (value substituted) or "unresolved" (a reference in arithmetic context, but the
    previous answer contains no number).
    """
    if previous_answer is None or not _ARITHMETIC_CONTEXT.search(step):
        return step, "none", None
    ref = _REFERENCE.search(step)
    if not ref:
        return step, "none", None
    value = extract_number(previous_answer)
    if value is None:
        return step, "unresolved", None
    return step[:ref.start()] + value + step[ref.end():], "resolved", value


def route_with_steps(router, query: str) -> list[RoutingDecision]:
    return [router.route(step) for step in split_compound_query(query)]
