"""Hybrid router: rules on the fast path, a second router (embeddings by default,
or the classifier) as the tie-breaker, and an explicit clarify decision when
neither is confident. The second router only needs route(), and its decisions
must carry candidates and the abstained flag.

Decision procedure (each step returns if it applies):
  1. rules confident (>= rule_accept)                -> rule decision, no embedding call
  2. embeddings picked a route a rule vetoed         -> rule decision (a veto overrides the embedding choice)
  3. embeddings abstained (no close examples)        -> rule decision if rules had signal, else ambiguous
  4. rules abstained (nothing matched)               -> embedding decision if >= embed_accept, else ambiguous
  5. both have signal and agree                      -> that route, mean confidence
  6. both have signal and disagree                   -> embeddings only if >= strong_accept, else ambiguous
  ambiguous -> "clarify" when the leading candidate is a tool and at least one router had
               signal; otherwise a low-confidence "direct" answer (always "direct" when
               on_ambiguous="direct")
"""

from __future__ import annotations

import time

from .schema import RoutingDecision, DIRECT, CLARIFY
from .rules import RuleRouter


class HybridRouter:
    name = "hybrid"

    def __init__(self, rules: RuleRouter, second,
                 rule_accept: float = 0.8, embed_accept: float = 0.6,
                 strong_accept: float = 0.8, on_ambiguous: str = CLARIFY, name: str = "hybrid") -> None:
        if on_ambiguous not in (CLARIFY, DIRECT):
            raise ValueError("on_ambiguous must be 'clarify' or 'direct'")
        self.name = name
        self.rules = rules
        self.second = second
        self.rule_accept = rule_accept
        self.embed_accept = embed_accept
        self.strong_accept = strong_accept
        self.on_ambiguous = on_ambiguous

    def _tag(self, decision: RoutingDecision, path: str, note: str = "") -> RoutingDecision:
        decision.router = f"{self.name}({path})"
        if note:
            decision.reason = f"{note}; {decision.reason}"
        return decision

    def _ambiguous(self, r: RoutingDecision, e: RoutingDecision) -> RoutingDecision:
        if len(e.candidates) < 2:   # a registry with one route cannot be ambiguous
            return self._tag(r, "rules", "only one route registered")
        top, second = e.candidates[0][0], e.candidates[1][0]
        detail = (f"rules chose {r.route} ({r.confidence:.2f}), embeddings chose {e.route} "
                  f"({e.confidence:.2f}); top candidates {top} and {second} are too close")
        # Ask only when the leading candidate is a tool, since a wrong tool call has the higher cost.
        # Otherwise answer directly at low confidence.
        both_abstained = r.abstained and e.abstained
        if self.on_ambiguous == DIRECT or both_abstained or top == DIRECT:
            why = ("neither router had any signal" if both_abstained else
                   "leading candidate is already direct" if top == DIRECT else "on_ambiguous=direct")
            return RoutingDecision(route=DIRECT, confidence=min(e.confidence, 0.5), router=f"{self.name}(fallback)",
                                   candidates=e.candidates, vetoed=r.vetoed, abstained=both_abstained,
                                   reason=f"ambiguous, answering directly ({why}): {detail}")
        return RoutingDecision(route=CLARIFY, confidence=e.confidence, router=f"{self.name}(clarify)",
                               candidates=e.candidates, vetoed=r.vetoed, reason=detail)

    def _decide(self, query: str) -> RoutingDecision:
        r = self.rules.route(query)
        if not r.abstained and r.confidence >= self.rule_accept:
            return self._tag(r, "rules")

        e = self.second.route(query)
        if e.route in r.vetoed:
            return self._tag(r, "veto", f"embeddings chose {e.route} but a rule vetoed it")
        if e.abstained:
            if not r.abstained:
                return self._tag(r, "rules-after-abstain", "embeddings abstained")
            return self._ambiguous(r, e)
        if r.abstained:
            if e.confidence >= self.embed_accept:
                return self._tag(e, self.second.name, "rules had no signal")
            return self._ambiguous(r, e)
        if r.route == e.route:
            return RoutingDecision(
                route=e.route, confidence=(r.confidence + e.confidence) / 2, router=f"{self.name}(agree)",
                candidates=e.candidates, vetoed=r.vetoed,
                reason=f"rules ({r.confidence:.2f}) and embeddings ({e.confidence:.2f}) both chose {e.route}")
        if e.confidence >= self.strong_accept:
            return self._tag(e, self.second.name, f"overrides rules ({r.route} {r.confidence:.2f})")
        return self._ambiguous(r, e)

    def route(self, query: str) -> RoutingDecision:
        t0 = time.perf_counter()
        decision = self._decide(query)
        decision.latency_ms = (time.perf_counter() - t0) * 1000
        return decision
