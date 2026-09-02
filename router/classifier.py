"""Classifier router: logistic regression over the same sentence embeddings.

Training data is eval/train.jsonl (one {"query", "route"} object per line) plus
the registry example utterances. The query embedding is the same MiniLM vector
the embedding router uses; the difference is that a linear model is fitted to
labelled queries instead of comparing against prototypes directly.

Confidence is the predicted probability of the top route. If that probability
is below min_confidence the decision is marked abstained, so the hybrid can
treat this router exactly as it treats the embedding router.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .schema import RoutingDecision
from .tools import ToolRegistry
from .embeddings import DEFAULT_MODEL, load_encoder

DEFAULT_TRAIN = Path(__file__).resolve().parents[1] / "eval" / "train.jsonl"


def load_training(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    for r in rows:
        if "query" not in r or "route" not in r:
            raise ValueError(f"training row needs 'query' and 'route': {r}")
    return rows


class ClassifierRouter:
    name = "classifier"

    def __init__(self, registry: ToolRegistry, training_path: Path = DEFAULT_TRAIN, encoder=None,
                 model_name: str = DEFAULT_MODEL, min_confidence: float = 0.5, C: float = 1.0) -> None:
        from sklearn.linear_model import LogisticRegression

        if encoder is None:
            encoder = load_encoder(model_name)
        self.registry = registry
        self.encoder = encoder
        self.min_confidence = min_confidence

        texts, labels = [], []
        for row in load_training(training_path):
            if row["route"] not in registry.names():
                raise ValueError(f"training row has unknown route {row['route']!r}: {row['query']!r}")
            texts.append(row["query"])
            labels.append(row["route"])
        for spec in registry:
            texts.extend(spec.examples)
            labels.extend([spec.name] * len(spec.examples))
        self.n_train = len(texts)

        X = self.encoder.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        self.clf = LogisticRegression(C=C, max_iter=2000, class_weight="balanced").fit(X, labels)

    def route(self, query: str) -> RoutingDecision:
        t0 = time.perf_counter()
        x = self.encoder.encode([query], normalize_embeddings=True, convert_to_numpy=True)
        probs = self.clf.predict_proba(x)[0]
        ranked = sorted(zip(self.clf.classes_, probs), key=lambda kv: kv[1], reverse=True)
        top_route, top = ranked[0]
        abstained = bool(top < self.min_confidence)
        reason = f"logistic regression over the sentence embedding ({self.n_train} training queries): p({top_route}) = {top:.2f}"
        if len(ranked) > 1:
            reason += f", p({ranked[1][0]}) = {ranked[1][1]:.2f}"
        if abstained:
            reason += f"; below min_confidence {self.min_confidence}, abstaining"
        decision = RoutingDecision(
            route=str(top_route), confidence=float(top), router=self.name, reason=reason,
            candidates=[(str(r), float(p)) for r, p in ranked], abstained=abstained,
        )
        decision.latency_ms = (time.perf_counter() - t0) * 1000
        return decision
