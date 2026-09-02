from router import Assistant, MockLLM


def test_tool_route_executes_tool(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What is 245 * 18?")
    assert out["routes"] == ["calculator"] and "4410" in out["answer"]
    assert out["latency_ms"]["llm"] == 0


def test_tool_error_falls_back_to_llm(rules, registry):
    # the rules route "calculate ... sum of" to the calculator; the tool finds no digits and returns an error
    out = Assistant(rules, registry, MockLLM()).handle("Calculate the sum of all primes below ten")
    assert out["routes"] == ["calculator"]
    assert out["fallback"] and out["answer"].startswith("(calculator could not handle this")


def test_weather_without_location_asks(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What's the weather?")
    assert out["routes"] == ["weather"] and out["steps"][0]["asked_by"] == "tool"
    assert "location" in out["answer"].lower()


def test_router_clarification_is_recorded(rules, registry):
    from router import HybridRouter, RoutingDecision

    class Stub:
        name = "stub"
        def route(self, q):
            return RoutingDecision(route="calculator", confidence=0.55, router="stub", reason="stub",
                                   candidates=[("calculator", 0.3), ("web_search", 0.26)])
    out = Assistant(HybridRouter(rules, Stub()), registry, MockLLM()).handle("How much is it?")
    assert out["routes"] == ["clarify"] and out["steps"][0]["asked_by"] == "router"
    assert "a calculation" in out["answer"] and "a web search" in out["answer"]


def test_overlong_query_is_refused_quickly(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("1" * 20000)
    assert out["routes"] == [] and "500" in out["answer"] and out["latency_ms"]["total"] < 50


def test_multistep_answers_both(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What's the weather in Tokyo and what is 12 * 7?")
    assert out["routes"] == ["weather", "calculator"] and "84" in out["answer"]
