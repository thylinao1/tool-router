# Results

Dataset: 22 queries (heldout.jsonl). Rates use the full dataset as denominator. Router latency is the median of repeated calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate |
|---|---|---|---|---|---|---|---|
| rules | 90.9% | 81.8% | 0.0% | 0.0% | 9.1% | 0.0% | 0.0% |
| embeddings | 86.4% | 81.8% | 9.1% | 4.5% | 0.0% | 0.0% | 0.0% |
| hybrid | 77.3% | 77.3% | 0.0% | 4.5% | 4.5% | 0.0% | 22.7% |

## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 66.7% | 90.9% | 100.0% | 100.0% | 100.0% |
| embeddings | 66.7% | 90.9% | 100.0% | 100.0% | 75.0% |
| hybrid | 100.0% | 90.9% | 100.0% | 66.7% | 25.0% |

## Accuracy by confidence bucket (lenient)

| Router | bucket | n | accuracy |
|---|---|---|---|
| rules | high (>=0.8) | 8 | 100.0% |
| rules | low (<0.5) | 1 | 100.0% |
| rules | mid (0.5-0.8) | 13 | 84.6% |
| embeddings | high (>=0.8) | 11 | 90.9% |
| embeddings | low (<0.5) | 4 | 75.0% |
| embeddings | mid (0.5-0.8) | 7 | 85.7% |
| hybrid | high (>=0.8) | 11 | 90.9% |
| hybrid | low (<0.5) | 4 | 25.0% |
| hybrid | mid (0.5-0.8) | 7 | 85.7% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.024 | 0.024 | 0.035 | 0.036 |
| embeddings | 6.049 | 5.849 | 6.375 | 10.581 |
| hybrid | 3.568 | 5.365 | 5.746 | 6.162 |

## Hybrid decision paths

| path | queries |
|---|---|
| hybrid(rules) | 9 |
| hybrid(agree) | 5 |
| hybrid(clarify) | 5 |
| hybrid(embeddings) | 3 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 5 | 840.8 | 2.0 | 3239.0 | 3.68 | 0.50 | 836.5 |
| clarify | 5 | 23.3 | 19.1 | 44.3 | 23.23 | 0.00 | 0.0 |
| direct | 2 | 2206.0 | 1296.0 | 3116.1 | 4.59 | 0.00 | 2201.3 |
| multi | 1 | 0.4 | 0.4 | 0.4 | 0.07 | 0.27 | 0.0 |
| weather | 5 | 8.4 | 7.0 | 22.0 | 8.18 | 0.14 | 0.0 |
| web_search | 4 | 8.2 | 9.8 | 12.8 | 7.98 | 0.15 | 0.0 |

## Errors per router

### rules (2 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 6 | Do I need sunscreen in Bali this afternoon? | weather | direct | 0.50 | missed_tool |
| 17 | Find the cheapest flights from Singapore to Tokyo next month | web_search | direct | 0.50 | missed_tool |

### embeddings (3 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 16 | Explain how a calculator computes square roots | direct | calculator | 0.95 | unnecessary_tool |
| 17 | Find the cheapest flights from Singapore to Tokyo next month | web_search | weather | 0.50 | incorrect_tool |
| 18 | Any idea? | clarify | web_search | 0.32 | incorrect_tool |

### hybrid (5 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 12 | What does HTTP stand for? | direct | clarify | 0.45 | other |
| 15 | What's the melting point of gold? | direct | clarify | 0.29 | other |
| 16 | Explain how a calculator computes square roots | direct | calculator | 0.95 | unnecessary_tool |
| 17 | Find the cheapest flights from Singapore to Tokyo next month | web_search | clarify | 0.50 | missed_tool |
| 20 | Tell me a fun fact about octopuses | direct | clarify | 0.44 | other |

