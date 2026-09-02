from router.tools import calculator, weather, web_search, extract_expression


def test_calculator_handles_spec_example():
    assert calculator("What is 245 * 18?").text == "245 * 18 = 4410"


def test_calculator_handles_words_and_percent():
    assert calculator("Calculate 15% of 80").text.endswith("= 12")
    assert calculator("What is the square root of 144?").text.endswith("= 12")
    assert calculator("twelve plus 3").status == "ok" or calculator("12 plus 3").text.endswith("= 15")


def test_calculator_rejects_code():
    assert calculator('__import__("os").system("ls")').status == "error"
    assert calculator("2 ** 99999").status == "error"
    assert extract_expression("hello there") is None


def test_calculator_reports_error_when_no_expression():
    assert calculator("How many seconds are in a day?").status == "error"


def test_weather_extracts_location_or_asks():
    assert "Singapore" in weather("What is the weather in Singapore today?").text
    assert weather("how hot is it in dubai").text.startswith("Weather in Dubai")
    assert weather("What's the weather?").status == "needs_input"


def test_weather_unknown_city_is_deterministic():
    assert weather("Weather in Zanzibar").text == weather("Weather in Zanzibar").text


def test_web_search_returns_snippet():
    assert web_search("Who won the latest Formula 1 race?").status == "ok"


def test_calculator_caps_result_magnitude():
    assert calculator("(2**999)**999").status == "error"
    assert calculator("2**64").text.endswith("= 18446744073709551616")


def test_calculator_returns_errors_not_exceptions_on_odd_results():
    assert calculator("(-8) ** 0.5").status == "error"          # complex
    assert calculator("1" + "+1" * 2000).status == "error"       # too long for the parser
    assert calculator("9" * 400 + " * 2").status == "error"      # oversized literal


def test_calculator_handles_verb_object_phrasings():
    assert calculator("Multiply 12 by 12").text.endswith("= 144")
    assert calculator("Subtract 40 from 100").text.endswith("= 60")
