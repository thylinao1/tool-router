import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from router import build_default_registry, RuleRouter, EmbeddingRouter, HybridRouter


@pytest.fixture(scope="session")
def registry():
    return build_default_registry()


@pytest.fixture(scope="session")
def rules(registry):
    return RuleRouter(registry)


@pytest.fixture(scope="session")
def embeddings(registry):
    return EmbeddingRouter(registry)


@pytest.fixture(scope="session")
def hybrid(rules, embeddings):
    return HybridRouter(rules, embeddings)
