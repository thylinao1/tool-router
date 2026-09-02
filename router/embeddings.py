"""Embedding router: nearest labelled examples with a small sentence encoder.

Each route's example utterances are encoded once. A query is scored against a
route by the mean cosine similarity of its top-k nearest examples of that route
(k=3 reduces the influence of a single unusually similar prototype). Route scores go through a softmax with a
low temperature; the winner's probability is the confidence. Two routes with
similar scores therefore yield a confidence near 0.5, which is what the hybrid
uses to detect ambiguity. Softmax only sees relative gaps, so a second check
caps confidence when no route has close examples: if even the best route's
top-3 mean cosine is below min_similarity, the router abstains. A query that
looks like nothing we have seen should not be confident about anything.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import numpy as np

from .schema import RoutingDecision
from .tools import ToolRegistry

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
_CACHE_DIR = Path.home() / ".cache" / "huggingface" / "hub" / "models--sentence-transformers--all-MiniLM-L6-v2"


def load_encoder(model_name: str = DEFAULT_MODEL):
    """Load the sentence encoder; once cached, skip the Hub check so start-up is silent and offline."""
    if model_name == DEFAULT_MODEL and _CACHE_DIR.exists():
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name, device="cpu")


class EmbeddingRouter:
    name = "embeddings"

    def __init__(self, registry: ToolRegistry, model_name: str = DEFAULT_MODEL,
                 temperature: float = 0.08, top_k: int = 3,
                 min_similarity: float = 0.3, far_cap: float = 0.5) -> None:
        self.registry = registry
        self.temperature = temperature
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.far_cap = far_cap
        self.model = load_encoder(model_name)

        self.labels: list[str] = []
        self.texts: list[str] = []
        for spec in registry:
            for ex in spec.examples:
                self.labels.append(spec.name)
                self.texts.append(ex)
        self.matrix = self.model.encode(self.texts, normalize_embeddings=True, convert_to_numpy=True)
        self._label_arr = np.array(self.labels)

    def scores(self, query: str) -> tuple[dict[str, float], dict[str, str]]:
        q = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
        sims = self.matrix @ q
        scores, nearest = {}, {}
        for route in self.registry.names():
            idx = np.where(self._label_arr == route)[0]
            route_sims = sims[idx]
            top = np.sort(route_sims)[::-1][: self.top_k]
            scores[route] = float(top.mean())
            nearest[route] = self.texts[idx[int(route_sims.argmax())]]
        return scores, nearest

    def route(self, query: str) -> RoutingDecision:
        t0 = time.perf_counter()
        scores, nearest = self.scores(query)
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        logits = np.array([s for _, s in ranked]) / self.temperature
        probs = np.exp(logits - logits.max())
        probs /= probs.sum()
        top_route, top = ranked[0]
        confidence = float(probs[0])
        reason = f"nearest example {nearest[top_route]!r}, top-3 mean cosine {top:.2f}"
        if len(ranked) > 1:
            reason += f"; margin over {ranked[1][0]} is {top - ranked[1][1]:.2f}"
        abstained = top < self.min_similarity
        if abstained:
            confidence = min(confidence, self.far_cap)
            reason += f"; no route has close examples (top-3 mean {top:.2f} < {self.min_similarity}), abstaining"
        decision = RoutingDecision(
            route=top_route, confidence=confidence, router=self.name,
            reason=reason, candidates=ranked, abstained=abstained,
        )
        decision.latency_ms = (time.perf_counter() - t0) * 1000
        return decision
