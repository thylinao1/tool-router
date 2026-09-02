"""Multi-step routing: split a compound request into parts and route each part.

The splitter is conservative by design. It only splits on conjunctions when
every resulting part reads like a request on its own (starts with a question or
command word, or contains arithmetic). "TCP and UDP" therefore stays together,
while "weather in Tokyo and what is 12 * 7" becomes two steps.
"""

from __future__ import annotations

import re

from .schema import RoutingDecision

_SPLIT_RE = re.compile(r"(?:,\s*)?\b(?:and then|and also|and|then|also)\b\s*|;\s*", re.I)
_REQUEST_START = re.compile(
    r"^(what|what's|whats|who|who's|when|where|which|how|is|are|do|does|did|can|could|will|would|"
    r"should|calculate|compute|tell|find|search|look|convert|give|check|explain|describe|write|"
    r"summarize|translate|show|get|list|define|add|multiply|divide|subtract|please)\b", re.I)
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


def route_with_steps(router, query: str) -> list[RoutingDecision]:
    return [router.route(step) for step in split_compound_query(query)]
