# Results

Dataset: 22 queries (heldout2.jsonl). Rates use the full dataset as denominator. Router latency is the median of 5 timed calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|
| rules | 90.9% | 77.3% | 0.0% | 0.0% | 9.1% | 0.0% | 0.0% | 31.8% |
| embeddings | 81.8% | 77.3% | 4.5% | 13.6% | 0.0% | 0.0% | 0.0% | 36.4% |
| hybrid | 100.0% | 90.9% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 18.2% |
| classifier | 95.5% | 86.4% | 0.0% | 4.5% | 0.0% | 0.0% | 0.0% | 13.6% |
| hybrid-clf | 100.0% | 90.9% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 13.6% |

## Confusion matrix (primary expected route -> predicted route)

### rules

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 3 | 0 | 1 | 0 | 0 | 0 |
| clarify | 0 | 0 | 2 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 1 | 0 | 4 | 0 |
| web_search | 0 | 0 | 1 | 0 | 0 | 3 |

### embeddings

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 0 | 0 | 1 | 1 |
| direct | 1 | 0 | 3 | 0 | 2 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 4 |

### hybrid

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 2 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 4 |

### classifier

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 2 | 0 | 0 | 0 |
| direct | 1 | 0 | 5 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 4 |

### hybrid-clf

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 0 | 2 | 0 | 0 | 0 |
| direct | 0 | 0 | 6 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 1 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 5 | 0 |
| web_search | 0 | 0 | 0 | 0 | 0 | 4 |


## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 100.0% | 80.0% | 100.0% | 100.0% | 100.0% |
| embeddings | 75.0% | 100.0% | 100.0% | 66.7% | 50.0% |
| hybrid | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |
| classifier | 100.0% | 100.0% | 100.0% | 100.0% | 75.0% |
| hybrid-clf | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% |

## Accuracy by confidence bucket (lenient)

| Router | bucket | n | accuracy |
|---|---|---|---|
| rules | high (>=0.8) | 9 | 100.0% |
| rules | low (<0.5) | 1 | 100.0% |
| rules | mid (0.5-0.8) | 12 | 83.3% |
| embeddings | high (>=0.8) | 11 | 90.9% |
| embeddings | low (<0.5) | 3 | 33.3% |
| embeddings | mid (0.5-0.8) | 8 | 87.5% |
| hybrid | high (>=0.8) | 13 | 100.0% |
| hybrid | low (<0.5) | 2 | 100.0% |
| hybrid | mid (0.5-0.8) | 7 | 100.0% |
| classifier | high (>=0.8) | 8 | 100.0% |
| classifier | low (<0.5) | 3 | 100.0% |
| classifier | mid (0.5-0.8) | 11 | 90.9% |
| hybrid-clf | high (>=0.8) | 11 | 100.0% |
| hybrid-clf | low (<0.5) | 3 | 100.0% |
| hybrid-clf | mid (0.5-0.8) | 8 | 100.0% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.022 | 0.023 | 0.032 | 0.032 |
| embeddings | 7.033 | 6.774 | 7.234 | 13.462 |
| hybrid | 3.988 | 6.413 | 7.049 | 7.370 |
| classifier | 7.267 | 6.880 | 8.317 | 13.424 |
| hybrid-clf | 4.034 | 6.324 | 7.152 | 7.250 |

## Decision paths: hybrid

| path | queries |
|---|---|
| hybrid(rules) | 9 |
| hybrid(fallback) | 4 |
| hybrid(agree) | 3 |
| hybrid(embeddings) | 3 |
| hybrid(rules-after-abstain) | 2 |
| hybrid(veto) | 1 |

## Decision paths: hybrid-clf

| path | queries |
|---|---|
| hybrid-clf(rules) | 9 |
| hybrid-clf(agree) | 5 |
| hybrid-clf(fallback) | 4 |
| hybrid-clf(classifier) | 3 |
| hybrid-clf(veto) | 1 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 4 | 260.8 | 24.7 | 1012.7 | 9.71 | 1.37 | 249.6 |
| direct | 8 | 1873.8 | 1987.9 | 3226.8 | 14.91 | 0.00 | 1858.8 |
| multi | 1 | 0.7 | 0.7 | 0.7 | 0.18 | 0.41 | 0.0 |
| weather | 5 | 8.2 | 0.4 | 26.7 | 7.96 | 0.14 | 0.0 |
| web_search | 4 | 14.1 | 20.9 | 24.4 | 13.87 | 0.19 | 0.0 |

## Errors per router

### rules (2 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 13 | Will it be foggy at Heathrow tomorrow morning? | weather | direct | 0.50 | missed_tool |
| 17 | Which movies are showing in Singapore cinemas this weekend? | web_search | direct | 0.50 | missed_tool |

### embeddings (4 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 15 | What's the freezing point of ethanol? | direct | weather | 0.50 | unnecessary_tool |
| 16 | Explain why the calculator app rounds numbers | direct | calculator | 0.82 | unnecessary_tool |
| 18 | And? | clarify | web_search | 0.33 | incorrect_tool |
| 21 | Proofread this sentence: their going to the park | direct | weather | 0.46 | unnecessary_tool |

### hybrid (0 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|

### classifier (1 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 16 | Explain why the calculator app rounds numbers | direct | calculator | 0.56 | unnecessary_tool |

### hybrid-clf (0 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|

