"""Bonus requirement: add a tool without touching any router code."""
import re

from router import (build_default_registry, RouteSpec, ToolResult, RuleRouter, EmbeddingRouter,
                    HybridRouter, Assistant, MockLLM)

_KM_TO_MILES = 0.621371


def unit_converter(query: str) -> ToolResult:
    m = re.search(r"(\d+(?:\.\d+)?)\s*(km|kilometers?)\s+(?:to|in)\s+miles", query, re.I)
    if not m:
        return ToolResult("error", "only km to miles is supported")
    return ToolResult("ok", f"{m.group(1)} km = {float(m.group(1)) * _KM_TO_MILES:.2f} miles")


def test_new_tool_is_routable_by_every_router():
    registry = build_default_registry().register(RouteSpec(
        name="unit_converter",
        description="a unit conversion",
        examples=["Convert 10 kilometers to miles", "How many miles is 42 km?",
                  "Turn 3 feet into centimeters", "What is 70 fahrenheit in celsius?",
                  "Convert 2 pounds to kilograms"],
        patterns=[("convert_units", r"\b(convert|how many)\b.*\b(km|kilomet|miles?|feet|cm|pounds?|kg|celsius|fahrenheit)\b", 0.9)],
        handler=unit_converter,
    ))
    rules, emb = RuleRouter(registry), EmbeddingRouter(registry)
    hybrid = HybridRouter(rules, emb)
    q = "Convert 5 km to miles"
    assert rules.route(q).route == "unit_converter"
    assert emb.route(q).route == "unit_converter"
    assert hybrid.route(q).route == "unit_converter"
    assert "3.11 miles" in Assistant(hybrid, registry, MockLLM()).handle(q)["answer"]
