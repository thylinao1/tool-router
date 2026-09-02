"""Ask the assistant one question and print the structured routing decision plus the answer.

  python cli.py "What is 245 * 18?"
  python cli.py --router rules "Who won the latest Formula 1 race?"
  python cli.py --decision-only "Write a haiku about rain"
"""

import argparse
import json

from router import (build_default_registry, RuleRouter, EmbeddingRouter, ClassifierRouter, HybridRouter,
                    Assistant, get_llm, route_with_steps)


def build_router(name: str, registry, on_ambiguous: str = "clarify"):
    rules = RuleRouter(registry)
    if name == "rules":
        return rules
    embeddings = EmbeddingRouter(registry)
    if name == "embeddings":
        return embeddings
    if name in ("classifier", "hybrid-clf"):
        classifier = ClassifierRouter(registry, encoder=embeddings.model)
        if name == "classifier":
            return classifier
        return HybridRouter(rules, classifier, on_ambiguous=on_ambiguous, name="hybrid-clf")
    return HybridRouter(rules, embeddings, on_ambiguous=on_ambiguous)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--router", choices=["rules", "embeddings", "classifier", "hybrid", "hybrid-clf"], default="hybrid")
    ap.add_argument("--on-ambiguous", choices=["clarify", "direct"], default="clarify",
                    help="hybrid only: ask the user, or answer directly, when no route is confident")
    ap.add_argument("--decision-only", action="store_true", help="route without executing tools or the LLM")
    ap.add_argument("--no-llm", action="store_true", help="use the mock LLM even if Ollama is running")
    args = ap.parse_args()

    registry = build_default_registry()
    router = build_router(args.router, registry, args.on_ambiguous)
    if args.decision_only:
        decisions = route_with_steps(router, args.query)
        print(json.dumps([d.to_dict() for d in decisions], indent=2, ensure_ascii=False))
        return
    llm = get_llm("mock" if args.no_llm else "ollama")
    print(json.dumps(Assistant(router, registry, llm).handle(args.query), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
