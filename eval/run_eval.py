"""Evaluate the three routers on eval/dataset.jsonl and write results/.

Usage:  python -m eval.run_eval [--no-llm] [--runs N] [--dataset PATH] [--out DIR]

Metrics (all rates use the full dataset size N as the denominator):
  accuracy_lenient      predicted route is in the item's acceptable set
  accuracy_strict       predicted route equals the item's primary expected route
  incorrect_tool_rate   a tool was chosen, a different route was expected, and the chosen tool is not acceptable
  unnecessary_tool_rate a tool was chosen where a direct answer was expected
  missed_tool_rate      direct or clarify was chosen where a tool was expected
  clarify_rate          fraction of decisions that asked for clarification
  abstain_rate          fraction of decisions where the router reported no real signal
Latency is measured per query with perf_counter after one warm-up call; the run count is recorded.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from router import (build_default_registry, RuleRouter, EmbeddingRouter, HybridRouter,
                    route_with_steps, Assistant, get_llm, MockLLM, DIRECT, CLARIFY)

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "eval" / "dataset.jsonl"
RESULTS = ROOT / "results"
EXAMPLE_IDS = [1, 2, 3, 4, 20, 34, 35, 39, 47]   # spec examples, overlaps, ambiguous, multi-step


def load_dataset(path: Path = DATASET) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def check_no_leakage(dataset: list[dict], registry) -> None:
    examples = {normalize(ex) for spec in registry for ex in spec.examples}
    leaked = [d["query"] for d in dataset if normalize(d["query"]) in examples]
    if leaked:
        raise SystemExit(f"evaluation queries duplicate router examples: {leaked}")


def score_item(item: dict, predicted: list[str], tools: set[str]) -> dict:
    if item["expected"] == "multi":
        ok = predicted == item["steps"]
        return {"lenient": ok, "strict": ok, "error": None if ok else "multi_step"}
    if len(predicted) != 1:
        return {"lenient": False, "strict": False, "error": "wrong_split"}
    p, expected, acceptable = predicted[0], item["expected"], item["acceptable"]
    lenient, strict = p in acceptable, p == expected
    error = None
    if not lenient:
        if p in tools and expected == DIRECT:
            error = "unnecessary_tool"
        elif p in tools:
            error = "incorrect_tool"
        elif expected in tools:
            error = "missed_tool"
        else:
            error = "other"
    return {"lenient": lenient, "strict": strict, "error": error}


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, int(round(pct / 100 * (len(ordered) - 1))))
    return ordered[idx]


def evaluate_router(name: str, router, dataset: list[dict], runs: int, tools: set[str]) -> dict:
    router.route("warm up call")
    rows = []
    for item in dataset:
        timings = []
        for _ in range(runs):
            t0 = time.perf_counter()
            decisions = route_with_steps(router, item["query"])
            timings.append((time.perf_counter() - t0) * 1000)
        predicted = [d.route for d in decisions]
        scored = score_item(item, predicted, tools)
        rows.append({
            "id": item["id"], "query": item["query"], "category": item["category"],
            "expected": item["expected"] if item["expected"] != "multi" else item["steps"],
            "acceptable": item.get("acceptable"), "predicted": predicted,
            "confidence": round(min(d.confidence for d in decisions), 3),
            "abstained": any(d.abstained for d in decisions),
            "path": decisions[0].router, "reason": " | ".join(d.reason for d in decisions),
            "latency_ms": round(statistics.median(timings), 3), **scored,
        })

    n = len(rows)
    errors = Counter(r["error"] for r in rows if r["error"])
    latencies = [r["latency_ms"] for r in rows]
    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r["lenient"])
    buckets = defaultdict(list)
    for r in rows:
        c = r["confidence"]
        buckets["low (<0.5)" if c < 0.5 else "mid (0.5-0.8)" if c < 0.8 else "high (>=0.8)"].append(r["lenient"])
    confusion = Counter()
    for r in rows:
        exp = "multi" if isinstance(r["expected"], list) else r["expected"]
        pred = "multi" if len(r["predicted"]) > 1 else r["predicted"][0]
        confusion[(exp, pred)] += 1
    return {
        "router": name,
        "n": n,
        "accuracy_lenient": sum(r["lenient"] for r in rows) / n,
        "accuracy_strict": sum(r["strict"] for r in rows) / n,
        "incorrect_tool_rate": errors["incorrect_tool"] / n,
        "unnecessary_tool_rate": errors["unnecessary_tool"] / n,
        "missed_tool_rate": errors["missed_tool"] / n,
        "multi_step_error_rate": (errors["multi_step"] + errors["wrong_split"]) / n,
        "clarify_rate": sum(1 for r in rows if CLARIFY in r["predicted"]) / n,
        "abstain_rate": sum(1 for r in rows if r["abstained"]) / n,
        "accuracy_by_category": {c: sum(v) / len(v) for c, v in sorted(by_cat.items())},
        "accuracy_by_confidence": {b: {"n": len(v), "accuracy": sum(v) / len(v)} for b, v in sorted(buckets.items())},
        "paths": dict(Counter(r["path"] for r in rows)),
        "latency_ms": {"mean": statistics.mean(latencies), "p50": percentile(latencies, 50),
                       "p95": percentile(latencies, 95), "max": max(latencies)},
        "confusion": {f"{e}->{p}": c for (e, p), c in sorted(confusion.items())},
        "rows": rows,
    }


def evaluate_end_to_end(assistant: Assistant, dataset: list[dict]) -> dict:
    assistant.router.route("warm up call")
    assistant.llm.generate("Say hi.")          # loads the model before the first timed direct query
    per_route = defaultdict(list)
    traces = {}
    rows = []
    for item in dataset:
        out = assistant.handle(item["query"])
        key = "multi" if len(out["routes"]) > 1 else out["routes"][0]
        per_route[key].append(out["latency_ms"])
        rows.append({"id": item["id"], "query": item["query"], "routes": out["routes"],
                     "fallback": out["fallback"], "asked_by": [s["asked_by"] for s in out["steps"]],
                     **{f"{k}_ms": v for k, v in out["latency_ms"].items()}})
        if item["id"] in EXAMPLE_IDS:
            traces[item["id"]] = out
    summary = {}
    for route, lat in sorted(per_route.items()):
        summary[route] = {
            "n": len(lat),
            "total_ms": {"mean": statistics.mean(l["total"] for l in lat),
                         "p50": percentile([l["total"] for l in lat], 50),
                         "p95": percentile([l["total"] for l in lat], 95)},
            "routing_ms_mean": statistics.mean(l["routing"] for l in lat),
            "tool_ms_mean": statistics.mean(l["tool"] for l in lat),
            "llm_ms_mean": statistics.mean(l["llm"] for l in lat),
        }
    return {"llm": assistant.llm.name, "per_route": summary, "traces": traces, "rows": rows}


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def write_markdown(results: list[dict], e2e: dict, out: Path, dataset_name: str, runs: int) -> None:
    lines = ["# Results", "", f"Dataset: {results[0]['n']} queries ({dataset_name}). "
             f"Rates use the full dataset as denominator. Router latency is the median of {runs} timed calls per query, "
             "after one warm-up call, on an Apple M2 (CPU only).", "",
             "## Routing quality", "",
             "| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['router']} | {pct(r['accuracy_lenient'])} | {pct(r['accuracy_strict'])} | "
                     f"{pct(r['incorrect_tool_rate'])} | {pct(r['unnecessary_tool_rate'])} | {pct(r['missed_tool_rate'])} | "
                     f"{pct(r['multi_step_error_rate'])} | {pct(r['clarify_rate'])} | {pct(r['abstain_rate'])} |")
    lines += ["", "## Confusion matrix (primary expected route -> predicted route)", ""]
    for r in results:
        labels = sorted({k.split("->")[0] for k in r["confusion"]} | {k.split("->")[1] for k in r["confusion"]})
        lines.append(f"### {r['router']}")
        lines.append("")
        lines.append("| expected \\ predicted | " + " | ".join(labels) + " |")
        lines.append("|---|" + "---|" * len(labels))
        for exp in labels:
            lines.append(f"| {exp} | " + " | ".join(str(r["confusion"].get(f"{exp}->{pred}", 0)) for pred in labels) + " |")
        lines.append("")
    lines += ["", "## Accuracy by query category (lenient)", "", "| Router | " + " | ".join(results[0]["accuracy_by_category"]) + " |",
              "|---|" + "---|" * len(results[0]["accuracy_by_category"])]
    for r in results:
        lines.append(f"| {r['router']} | " + " | ".join(pct(v) for v in r["accuracy_by_category"].values()) + " |")
    lines += ["", "## Accuracy by confidence bucket (lenient)", "", "| Router | bucket | n | accuracy |", "|---|---|---|---|"]
    for r in results:
        for b, v in r["accuracy_by_confidence"].items():
            lines.append(f"| {r['router']} | {b} | {v['n']} | {pct(v['accuracy'])} |")
    lines += ["", "## Router latency (ms)", "", "| Router | mean | p50 | p95 | max |", "|---|---|---|---|---|"]
    for r in results:
        l = r["latency_ms"]
        lines.append(f"| {r['router']} | {l['mean']:.3f} | {l['p50']:.3f} | {l['p95']:.3f} | {l['max']:.3f} |")
    hybrid = next((r for r in results if r["router"] == "hybrid"), None)
    if hybrid:
        lines += ["", "## Hybrid decision paths", "", "| path | queries |", "|---|---|"]
        for p, c in sorted(hybrid["paths"].items(), key=lambda kv: -kv[1]):
            lines.append(f"| {p} | {c} |")
    lines += ["", f"## End-to-end latency per route (hybrid router, LLM = {e2e['llm']})", "",
              "| Route | n | total mean | total p50 | total p95 | routing | tool | llm |", "|---|---|---|---|---|---|---|---|"]
    for route, s in e2e["per_route"].items():
        t = s["total_ms"]
        lines.append(f"| {route} | {s['n']} | {t['mean']:.1f} | {t['p50']:.1f} | {t['p95']:.1f} | "
                     f"{s['routing_ms_mean']:.2f} | {s['tool_ms_mean']:.2f} | {s['llm_ms_mean']:.1f} |")
    lines += ["", "## Errors per router", ""]
    for r in results:
        bad = [row for row in r["rows"] if not row["lenient"]]
        lines.append(f"### {r['router']} ({len(bad)} errors)")
        lines.append("")
        lines.append("| id | query | expected | predicted | conf | error |")
        lines.append("|---|---|---|---|---|---|")
        for row in bad:
            lines.append(f"| {row['id']} | {row['query']} | {row['expected']} | {','.join(row['predicted'])} | "
                         f"{row['confidence']:.2f} | {row['error']} |")
        lines.append("")
    (out / "results.md").write_text("\n".join(lines) + "\n")

    ex = ["# Example outputs", "", f"Full traces from `Assistant.handle()` with the hybrid router (LLM = {e2e['llm']}).", ""]
    for item_id, trace in sorted(e2e["traces"].items()):
        ex += [f"## {trace['query']}", "", "```json", json.dumps(trace, indent=2, ensure_ascii=False), "```", ""]
    (out / "examples.md").write_text("\n".join(ex))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true", help="use the mock LLM even if Ollama is running")
    ap.add_argument("--runs", type=int, default=5, help="timed repetitions per query for router latency")
    ap.add_argument("--dataset", type=Path, default=DATASET)
    ap.add_argument("--out", type=Path, default=RESULTS)
    args = ap.parse_args()

    import torch
    torch.set_num_threads(4)   # fixed thread count so the latency tables are reproducible on the same machine

    dataset = load_dataset(args.dataset)
    registry = build_default_registry()
    check_no_leakage(dataset, registry)
    tools = set(registry.tool_names())
    rules = RuleRouter(registry)
    embeddings = EmbeddingRouter(registry)
    hybrid = HybridRouter(rules, embeddings)

    results = [evaluate_router(r.name, r, dataset, args.runs, tools) for r in (rules, embeddings, hybrid)]
    for r in results:
        print(f"{r['router']:11} lenient {pct(r['accuracy_lenient'])}  strict {pct(r['accuracy_strict'])}  "
              f"incorrect-tool {pct(r['incorrect_tool_rate'])}  unnecessary-tool {pct(r['unnecessary_tool_rate'])}  "
              f"p50 {r['latency_ms']['p50']:.3f} ms")

    llm = MockLLM() if args.no_llm else get_llm()
    print(f"end-to-end with LLM = {llm.name}")
    e2e = evaluate_end_to_end(Assistant(hybrid, registry, llm), dataset)

    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "metrics.json").write_text(json.dumps(
        {"dataset": args.dataset.name, "runs": args.runs, "llm": llm.name,
         "routers": [{k: v for k, v in r.items() if k != "rows"} for r in results],
         "end_to_end": {k: v for k, v in e2e.items() if k not in ("traces", "rows")}}, indent=2))
    with (out / "e2e.jsonl").open("w") as f:
        for row in e2e["rows"]:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out / "predictions.jsonl").open("w") as f:
        for r in results:
            for row in r["rows"]:
                f.write(json.dumps({"router": r["router"], **row}, ensure_ascii=False) + "\n")
    write_markdown(results, e2e, out, args.dataset.name, args.runs)
    print(f"wrote {out}/metrics.json, results.md, examples.md, predictions.jsonl, e2e.jsonl")


if __name__ == "__main__":
    main()
