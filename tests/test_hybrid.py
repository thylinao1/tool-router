from router import HybridRouter, CLARIFY, DIRECT


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


def test_hybrid_clarifies_when_a_tool_leads_but_neither_router_is_confident(hybrid):
    d = hybrid.route("How much is it?")
    assert d.route == CLARIFY
    assert d.candidates[0][0] != DIRECT and len(d.candidates) >= 2


def test_hybrid_answers_directly_when_no_router_has_signal(hybrid):
    d = hybrid.route("Tell me a fun fact about octopuses")
    assert d.route == DIRECT and d.confidence <= 0.5


def test_hybrid_can_fall_back_to_direct_instead(rules, embeddings):
    d = HybridRouter(rules, embeddings, on_ambiguous=DIRECT).route("How much is it?")
    assert d.route == DIRECT and d.router == "hybrid(fallback)"
