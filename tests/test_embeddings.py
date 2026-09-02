def test_embeddings_route_spec_examples(embeddings):
    assert embeddings.route("What is 245 * 18?").route == "calculator"
    assert embeddings.route("What is the weather in Singapore today?").route == "weather"
    assert embeddings.route("Who won the latest Formula 1 race?").route == "web_search"
    assert embeddings.route("Explain gradient descent.").route == "direct"


def test_embeddings_generalise_to_paraphrase(embeddings):
    assert embeddings.route("Write a poem about the sea").route == "direct"   # the nearest prototype uses "ocean"


def test_embeddings_cap_confidence_far_from_examples(embeddings):
    d = embeddings.route("zxqv blorp fnord")
    assert d.confidence <= 0.5 and d.abstained and "no route has close examples" in d.reason


def test_single_route_registry_does_not_crash():
    from router import ToolRegistry, RouteSpec, EmbeddingRouter, RuleRouter, HybridRouter
    reg = ToolRegistry().register(RouteSpec(name="direct", description="a general answer",
                                            examples=["Explain something", "Write a poem"]))
    hybrid = HybridRouter(RuleRouter(reg), EmbeddingRouter(reg))
    assert hybrid.route("zxqv blorp").route == "direct"


def test_embeddings_decision_is_structured(embeddings):
    d = embeddings.route("What is 245 * 18?").to_dict()
    assert set(d) >= {"route", "confidence", "reason", "router", "candidates", "latency_ms"}
    assert 0 <= d["confidence"] <= 1
