def test_rules_route_spec_examples(rules):
    assert rules.route("What is 245 * 18?").route == "calculator"
    assert rules.route("Who won the latest Formula 1 race?").route == "web_search"
    assert rules.route("Explain gradient descent.").route == "direct"
    assert rules.route("Is it raining in New York right now?").route == "weather"


def test_rules_confidence_drops_when_two_routes_fire(rules):
    d = rules.route("Is it raining today?")   # weather_word and time_now both fire
    assert d.route == "weather" and d.confidence < 0.8
    assert "runner-up" in d.reason


def test_rules_veto_is_reported(rules):
    d = rules.route("Write a haiku about rain")
    assert d.route == "direct" and "weather" in d.vetoed


def test_rules_exclusion_vetoes_route(rules):
    d = rules.route("Explain how weather forecasting models work")
    assert d.route == "direct"
    assert dict(d.candidates)["weather"] == 0.0


def test_rules_no_signal_defaults_to_direct_with_low_confidence(rules):
    d = rules.route("How many seconds are in a day?")
    assert d.route == "direct" and d.confidence == 0.5


def test_rules_are_fast(rules):
    assert rules.route("What is 245 * 18?").latency_ms < 5


def test_rules_stay_fast_on_long_digit_runs(rules):
    assert rules.route("9" * 20000).latency_ms < 50
