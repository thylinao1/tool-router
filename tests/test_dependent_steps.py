from router import Assistant, MockLLM
from router.multistep import extract_number, resolve_reference
from router.tools import calculator


def test_extract_number_prefers_value_after_equals():
    assert extract_number("245 * 18 = 4410") == "4410"
    assert extract_number("Weather in Tokyo: 26°C, partly cloudy") == "26"
    assert extract_number("Bitcoin is trading at about 60,000 USD") == "60000"
    assert extract_number("no digits here") is None


def test_resolve_reference_only_in_arithmetic_context():
    assert resolve_reference("multiply it by 0.5", "about 60,000 USD") == ("multiply 60000 by 0.5", "resolved", "60000")
    assert resolve_reference("is it warm enough for shorts", "26°C") == ("is it warm enough for shorts", "none", None)
    assert resolve_reference("add 10 to that", "a joke with no numbers") == ("add 10 to that", "unresolved", None)
    assert resolve_reference("multiply it by 2", None) == ("multiply it by 2", "none", None)


def test_calculator_handles_chained_phrasings():
    assert calculator("add 10 to 4410").text.endswith("= 4420")
    assert calculator("what is half of 41").text.endswith("= 20.5")
    assert calculator("double 21").text.endswith("= 42")
    assert calculator("halve 4410").text.endswith("= 2205")
    assert calculator("divide 42 by 2").text.endswith("= 21")
    assert calculator("square -3").text.endswith("= 9")


def test_calculator_handles_negative_chained_values():
    assert calculator("multiply -7 by 2").text.endswith("= -14")
    assert calculator("add 4 to -7").text.endswith("= -3")
    assert calculator("subtract 3 from -3").text.endswith("= -6")
    assert calculator("-7").status == "error"          # a bare literal is not a calculation


def test_calculator_prints_small_results_in_fixed_notation():
    assert calculator("3 / 200000").text.endswith("= 0.000015")
    assert extract_number("3 / 200000 = 0.000015") == "0.000015"
    assert extract_number("x = 1.5e-05") == "0.000015"


def test_reference_context_ignores_hyphenated_words():
    assert resolve_reference("is it t-shirt weather", "26°C")[1] == "none"
    assert resolve_reference("is it family-friendly", "26°C")[1] == "none"
    assert resolve_reference("what is it * 2", "26°C")[1] == "resolved"


def test_determiner_phrases_are_consumed():
    assert resolve_reference("multiply that price by 2", "about 60,000 USD")[0] == "multiply 60000 by 2"


def test_dependent_request_chains_the_value(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("Search for the Bitcoin price and multiply it by 0.5")
    assert out["routes"] == ["web_search", "calculator"]
    dep = out["steps"][1]["dependency"]
    assert dep["status"] == "resolved" and dep["value"] == extract_number(out["steps"][0]["answer"])
    assert out["steps"][1]["answer"].endswith(f"= {int(float(dep['value']) * 0.5)}")


def test_search_step_digit_is_not_taken_as_the_result(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("Search for the price of Bitcoin in 2024 and multiply it by 0.5")
    assert out["steps"][1]["dependency"]["value"] == "60000" and "30000" in out["answer"]


def test_negative_chained_value_is_evaluated(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What is 3 - 10 and then multiply it by 2")
    assert out["steps"][1]["dependency"]["value"] == "-7" and out["answer"].endswith("= -14")


def test_dependent_request_on_calculator_result(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What is 245 * 18 and then add 10 to that")
    assert out["routes"] == ["calculator", "calculator"]
    assert out["steps"][1]["dependency"]["value"] == "4410" and "4420" in out["answer"]


def test_unresolvable_reference_is_reported_not_guessed(hybrid, registry):
    class WordyLLM(MockLLM):
        def generate(self, prompt, system=""):
            return "A joke with no numbers in it."
    out = Assistant(hybrid, registry, WordyLLM()).handle("Tell me a joke and multiply it by 2")
    assert out["routes"] == ["direct", "unresolved"]
    assert out["steps"][1]["dependency"]["status"] == "unresolved"
    assert "did not produce a number" in out["answer"]


def test_plain_pronoun_is_not_substituted(hybrid, registry):
    out = Assistant(hybrid, registry, MockLLM()).handle("What's the weather in Tokyo and is it warm enough for shorts?")
    assert out["steps"][1]["dependency"] is None
