from router import HybridRouter, RoutingDecision, CLARIFY, DIRECT


class StubRouter:
    """A second-opinion router that returns a fixed decision, so hybrid policy is tested on its own."""
    name = "stub"

    def __init__(self, route, confidence, candidates, abstained=False):
        self._d = dict(route=route, confidence=confidence, candidates=candidates, abstained=abstained)

    def route(self, query):
        return RoutingDecision(router=self.name, reason="stub", **self._d)


def test_hybrid_takes_rule_fast_path_on_clear_query(hybrid):
    d = hybrid.route("What is 245 * 18?")
    assert d.route == "calculator" and d.router == "hybrid(rules)"


def test_hybrid_uses_embeddings_when_rules_conflict(hybrid):
    d = hybrid.route("Is it raining today?")
    assert d.route == "weather"
    assert d.router in ("hybrid(embeddings)", "hybrid(agree)")


def test_hybrid_respects_rule_veto(hybrid):
    d = hybrid.route("What is the derivative of x squared?")
    assert d.route == DIRECT and d.router == "hybrid(veto)"


def test_hybrid_clarifies_when_a_tool_leads_but_neither_router_is_confident(rules):
    # rules abstain on this query; the stub is a weak vote for a tool
    second = StubRouter("calculator", 0.55, [("calculator", 0.3), ("web_search", 0.26), ("direct", 0.14)])
    d = HybridRouter(rules, second).route("How much is it?")
    assert d.route == CLARIFY and d.router == "hybrid(clarify)"


def test_hybrid_answers_directly_when_no_router_has_signal(rules):
    second = StubRouter("direct", 0.44, [("direct", 0.2), ("weather", 0.1)], abstained=True)
    d = HybridRouter(rules, second).route("Tell me a fun fact about octopuses")
    assert d.route == DIRECT and d.router == "hybrid(fallback)" and d.confidence <= 0.5


def test_hybrid_answers_directly_when_direct_leads_a_weak_vote(rules):
    second = StubRouter("direct", 0.45, [("direct", 0.35), ("web_search", 0.31)])
    d = HybridRouter(rules, second).route("What's the capital of Australia?")
    assert d.route == DIRECT and d.router == "hybrid(fallback)"


def test_hybrid_can_fall_back_to_direct_instead(rules):
    second = StubRouter("calculator", 0.55, [("calculator", 0.3), ("web_search", 0.26)])
    d = HybridRouter(rules, second, on_ambiguous=DIRECT).route("How much is it?")
    assert d.route == DIRECT and d.router == "hybrid(fallback)"


def test_hybrid_lets_a_strong_second_opinion_override_a_weak_rule(rules):
    # "Is it raining today?" gives rules weather at 0.65, below the fast path
    second = StubRouter("web_search", 0.9, [("web_search", 0.5), ("weather", 0.2)])
    d = HybridRouter(rules, second).route("Is it raining today?")
    assert d.route == "web_search" and d.router == "hybrid(stub)"


def test_hybrid_end_to_end_with_real_routers(hybrid):
    assert hybrid.route("How much is it?").route in (CLARIFY, DIRECT)     # ambiguous either way
    assert hybrid.route("Tell me a fun fact about octopuses").route == DIRECT
