# Results

Dataset: 22 queries (heldout.jsonl). Rates use the full dataset as denominator. Router latency is the median of 5 timed calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|
| rules | 90.9% | 81.8% | 0.0% | 0.0% | 9.1% | 0.0% | 0.0% | 31.8% |
| embeddings | 86.4% | 81.8% | 9.1% | 4.5% | 0.0% | 0.0% | 0.0% | 27.3% |
| hybrid | 95.5% | 90.9% | 0.0% | 0.0% | 4.5% | 0.0% | 0.0% | 22.7% |
| classifier | 90.9% | 90.9% | 4.5% | 4.5% | 0.0% | 0.0% | 0.0% | 22.7% |
| hybrid-clf | 100.0% | 95.5% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 9.1% |

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

### classifier

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 0 | 0 | 0 | 1 |
| direct | 1 | 0 | 5 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 5 |

### hybrid-clf

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 1 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 5 |


## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 66.7% | 90.9% | 100.0% | 100.0% | 100.0% |
| embeddings | 66.7% | 90.9% | 100.0% | 100.0% | 75.0% |
| hybrid | 100.0% | 90.9% | 100.0% | 100.0% | 100.0% |
| classifier | 66.7% | 100.0% | 100.0% | 100.0% | 75.0% |
| hybrid-clf | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

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
| classifier | high (>=0.8) | 7 | 100.0% |
| classifier | low (<0.5) | 5 | 60.0% |
| classifier | mid (0.5-0.8) | 10 | 100.0% |
| hybrid-clf | high (>=0.8) | 8 | 100.0% |
| hybrid-clf | low (<0.5) | 2 | 100.0% |
| hybrid-clf | mid (0.5-0.8) | 12 | 100.0% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.024 | 0.023 | 0.034 | 0.036 |
| embeddings | 6.031 | 5.882 | 6.196 | 11.091 |
| hybrid | 3.647 | 5.446 | 6.003 | 6.115 |
| classifier | 5.955 | 5.682 | 6.069 | 10.921 |
| hybrid-clf | 3.668 | 5.420 | 5.986 | 6.055 |

## Decision paths: hybrid

| path | queries |
|---|---|
| hybrid(rules) | 8 |
| hybrid(agree) | 5 |
| hybrid(fallback) | 5 |
| hybrid(embeddings) | 2 |
| hybrid(rules-after-abstain) | 1 |
| hybrid(veto) | 1 |

## Decision paths: hybrid-clf

| path | queries |
|---|---|
| hybrid-clf(rules) | 8 |
| hybrid-clf(classifier) | 5 |
| hybrid-clf(agree) | 4 |
| hybrid-clf(rules-after-abstain) | 2 |
| hybrid-clf(fallback) | 2 |
| hybrid-clf(veto) | 1 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 4 | 211.7 | 4.7 | 840.7 | 3.11 | 1.31 | 207.2 |
| direct | 8 | 2052.5 | 2464.4 | 3090.9 | 19.53 | 0.00 | 2032.7 |
| multi | 1 | 0.6 | 0.6 | 0.6 | 0.12 | 0.44 | 0.0 |
| weather | 5 | 13.8 | 21.4 | 23.1 | 13.42 | 0.36 | 0.0 |
| web_search | 4 | 18.8 | 20.0 | 43.4 | 18.54 | 0.17 | 0.0 |

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

### classifier (2 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 16 | Explain how a calculator computes square roots | direct | calculator | 0.48 | unnecessary_tool |
| 18 | Any idea? | clarify | web_search | 0.47 | incorrect_tool |

### hybrid-clf (0 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|

