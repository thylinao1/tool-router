from pathlib import Path

import pytest

from router import ClassifierRouter, HybridRouter, DIRECT

TRAIN = Path(__file__).resolve().parents[1] / "eval" / "train.jsonl"
pytestmark = pytest.mark.skipif(not TRAIN.exists(), reason="eval/train.jsonl not present")


@pytest.fixture(scope="session")
def classifier(registry, embeddings):
    return ClassifierRouter(registry, TRAIN, encoder=embeddings.model)


def test_classifier_routes_spec_examples(classifier):
    assert classifier.route("What is 245 * 18?").route == "calculator"
    assert classifier.route("What is the weather in Singapore today?").route == "weather"
    assert classifier.route("Who won the latest Formula 1 race?").route == "web_search"
    assert classifier.route("Explain gradient descent.").route == DIRECT


def test_classifier_confidence_is_a_probability(classifier):
    d = classifier.route("What is 245 * 18?")
    assert 0 <= d.confidence <= 1
    assert abs(sum(p for _, p in d.candidates) - 1) < 1e-6


def test_classifier_abstains_on_nonsense(classifier):
    d = classifier.route("zxqv blorp fnord")
    assert d.abstained and d.confidence < classifier.min_confidence


def test_hybrid_accepts_classifier_as_second_opinion(rules, classifier):
    h = HybridRouter(rules, classifier, name="hybrid-clf")
    d = h.route("Why do cats purr?")
    assert d.route == DIRECT and d.router.startswith("hybrid-clf(")
