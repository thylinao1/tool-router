from router import split_compound_query, route_with_steps


def test_splits_two_requests():
    assert split_compound_query("What's the weather in Tokyo and what is 12 * 7?") == \
        ["What's the weather in Tokyo", "what is 12 * 7"]


def test_keeps_single_request_with_and():
    q = "What is the difference between TCP and UDP?"
    assert split_compound_query(q) == [q]


def test_splitter_is_fast_on_long_whitespace():
    import time
    t = time.perf_counter()
    split_compound_query("what" + " " * 20000 + "and")
    assert time.perf_counter() - t < 0.05


def test_routes_each_step(hybrid):
    routes = [d.route for d in route_with_steps(hybrid, "Calculate 45 * 3 and then explain what a prime number is")]
    assert routes == ["calculator", "direct"]
