# Results

Dataset: 22 queries (heldout.jsonl). Rates use the full dataset as denominator. Router latency is the median of 5 timed calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|
| rules | 90.9% | 81.8% | 0.0% | 0.0% | 9.1% | 0.0% | 0.0% | 31.8% |
| embeddings | 86.4% | 81.8% | 9.1% | 4.5% | 0.0% | 0.0% | 0.0% | 27.3% |
| hybrid | 95.5% | 90.9% | 0.0% | 0.0% | 4.5% | 0.0% | 0.0% | 22.7% |

## Confusion matrix (primary expected route -> predicted route)

### rules

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 3 | 0 | 1 | 0 | 0 | 0 |
| clarify | 0 | 0 | 1 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 1 | 0 | 4 | 0 |
| web_search | 0 | 0 | 1 | 0 | 0 | 4 |

### embeddings

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 0 | 0 | 0 | 1 |
| direct | 1 | 0 | 4 | 0 | 0 | 1 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 1 | 4 |

### hybrid

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 1 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 1 | 0 | 0 | 4 |


## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 66.7% | 90.9% | 100.0% | 100.0% | 100.0% |
| embeddings | 66.7% | 90.9% | 100.0% | 100.0% | 75.0% |
| hybrid | 100.0% | 90.9% | 100.0% | 100.0% | 100.0% |

## Accuracy by confidence bucket (lenient)

| Router | bucket | n | accuracy |
|---|---|---|---|
| rules | high (>=0.8) | 8 | 100.0% |
| rules | low (<0.5) | 1 | 100.0% |
| rules | mid (0.5-0.8) | 13 | 84.6% |
| embeddings | high (>=0.8) | 11 | 90.9% |
| embeddings | low (<0.5) | 4 | 75.0% |
| embeddings | mid (0.5-0.8) | 7 | 85.7% |
| hybrid | high (>=0.8) | 10 | 100.0% |
| hybrid | low (<0.5) | 4 | 100.0% |
| hybrid | mid (0.5-0.8) | 8 | 87.5% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.023 | 0.023 | 0.034 | 0.035 |
| embeddings | 5.898 | 5.646 | 6.354 | 10.552 |
| hybrid | 3.506 | 5.185 | 5.765 | 5.939 |

## Hybrid decision paths

| path | queries |
|---|---|
| hybrid(rules) | 8 |
| hybrid(agree) | 5 |
| hybrid(fallback) | 5 |
| hybrid(embeddings) | 2 |
| hybrid(rules-after-abstain) | 1 |
| hybrid(veto) | 1 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 4 | 231.5 | 3.2 | 921.3 | 2.84 | 0.92 | 227.6 |
| direct | 8 | 2196.1 | 2524.4 | 3278.0 | 15.71 | 0.00 | 2180.2 |
| multi | 1 | 0.5 | 0.5 | 0.5 | 0.12 | 0.31 | 0.0 |
| weather | 5 | 12.0 | 18.4 | 21.7 | 11.76 | 0.17 | 0.0 |
| web_search | 4 | 12.9 | 19.8 | 22.1 | 12.68 | 0.19 | 0.0 |

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

### hybrid (1 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 17 | Find the cheapest flights from Singapore to Tokyo next month | web_search | direct | 0.50 | missed_tool |

