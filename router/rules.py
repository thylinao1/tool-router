"""Rule router: weighted regex rules per route, combined with noisy-OR.

Score(route) = 1 - prod(1 - w_i) over matched rules, so several weak matches
add up but never exceed 1. An exclusion match sets the score to 0.
Confidence = top score minus half the runner-up score, so two routes that both
fire produce a low confidence rather than an arbitrary choice between them.
"""

from __future__ import annotations

import re
import time

from .schema import RoutingDecision, DIRECT
from .tools import ToolRegistry

NO_SIGNAL_CONFIDENCE = 0.5   # nothing matched: default to direct, but say so


class RuleRouter:
    name = "rules"

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry
        self._rules = {
            spec.name: [(n, re.compile(p, re.I), w) for n, p, w in spec.patterns]
            for spec in registry
        }
        self._exclusions = {
            spec.name: [(n, re.compile(p, re.I)) for n, p in spec.exclusions]
            for spec in registry
        }

    def scores(self, query: str) -> tuple[dict[str, float], dict[str, list[str]]]:
        scores: dict[str, float] = {}
        matched: dict[str, list[str]] = {}
        for route, rules in self._rules.items():
            hits = [(n, w) for n, rx, w in rules if rx.search(query)]
            vetoed = [n for n, rx in self._exclusions[route] if rx.search(query)]
            if vetoed:
                scores[route] = 0.0
                matched[route] = [f"vetoed by {v}" for v in vetoed]
                continue
            miss = 1.0
            for _, w in hits:
                miss *= 1.0 - w
            scores[route] = 1.0 - miss
            matched[route] = [n for n, _ in hits]
        return scores, matched

    def route(self, query: str) -> RoutingDecision:
        t0 = time.perf_counter()
        scores, matched = self.scores(query)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        top_route, top = ranked[0]
        second = ranked[1][1] if len(ranked) > 1 else 0.0

        vetoed = [r for r, hits in matched.items() if any(h.startswith("vetoed") for h in hits)]
        if top == 0.0:
            reason = "no rule matched any route; defaulting to a direct answer"
            if vetoed:
                reason += f" (vetoed: {', '.join(vetoed)})"
            decision = RoutingDecision(
                route=DIRECT, confidence=NO_SIGNAL_CONFIDENCE, router=self.name,
                reason=reason, candidates=ranked, vetoed=vetoed, abstained=True,
            )
        else:
            confidence = max(0.0, min(1.0, top - 0.5 * second))
            reason = f"matched {', '.join(matched[top_route])} for {top_route} (score {top:.2f})"
            if second > 0:
                reason += f"; runner-up {ranked[1][0]} scored {second:.2f}"
            if vetoed:
                reason += f"; vetoed {', '.join(vetoed)}"
            decision = RoutingDecision(
                route=top_route, confidence=confidence, router=self.name,
                reason=reason, candidates=ranked, vetoed=vetoed,
            )
        decision.latency_ms = (time.perf_counter() - t0) * 1000
        return decision
