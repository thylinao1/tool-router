"""The structured routing decision every router returns."""

from dataclasses import dataclass, field, asdict

DIRECT = "direct"      # answer with the LLM, no tool
CLARIFY = "clarify"    # ask the user which of the top candidates they meant


@dataclass
class RoutingDecision:
    route: str                       # tool name, "direct", or "clarify"
    confidence: float                # 0..1, meaning depends on the router (see README)
    reason: str                      # human-readable explanation of the decision
    router: str                      # which router (or hybrid path) produced it
    candidates: list = field(default_factory=list)   # [(route, score)] best first
    vetoed: list = field(default_factory=list)       # routes ruled out by an exclusion rule
    abstained: bool = False          # the router had no real signal for this query
    latency_ms: float = 0.0          # time spent inside the router

    def to_dict(self) -> dict:
        d = asdict(self)
        d["confidence"] = round(self.confidence, 3)
        d["latency_ms"] = round(self.latency_ms, 3)
        d["candidates"] = [(r, round(s, 3)) for r, s in self.candidates]
        return d
