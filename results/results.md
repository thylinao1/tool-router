# Results

Dataset: 50 queries (dataset.jsonl). Rates use the full dataset as denominator. Router latency is the median of 5 timed calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|
| rules | 94.0% | 80.0% | 2.0% | 2.0% | 2.0% | 0.0% | 0.0% | 24.0% |
| embeddings | 70.0% | 66.0% | 14.0% | 14.0% | 0.0% | 2.0% | 0.0% | 36.0% |
| hybrid | 92.0% | 88.0% | 4.0% | 2.0% | 2.0% | 0.0% | 4.0% | 12.0% |
| classifier | 88.0% | 80.0% | 8.0% | 4.0% | 0.0% | 0.0% | 0.0% | 24.0% |
| hybrid-clf | 94.0% | 88.0% | 2.0% | 2.0% | 2.0% | 0.0% | 6.0% | 12.0% |

## Confusion matrix (primary expected route -> predicted route)

### rules

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 5 | 0 | 1 | 0 | 0 | 0 |
| clarify | 0 | 0 | 3 | 0 | 1 | 0 |
| direct | 1 | 0 | 20 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 4 | 0 | 0 |
| weather | 0 | 0 | 1 | 0 | 5 | 0 |
| web_search | 1 | 0 | 2 | 0 | 0 | 6 |

### embeddings

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 5 | 0 | 0 | 0 | 1 | 0 |
| clarify | 1 | 0 | 0 | 0 | 2 | 1 |
| direct | 2 | 0 | 14 | 0 | 5 | 0 |
| multi | 0 | 0 | 0 | 4 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 6 | 0 |
| web_search | 1 | 0 | 0 | 0 | 3 | 5 |

### hybrid

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 6 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 2 | 1 | 0 | 1 | 0 |
| direct | 1 | 0 | 20 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 4 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 6 | 0 |
| web_search | 0 | 0 | 1 | 0 | 2 | 6 |

### classifier

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 6 | 0 | 0 | 0 | 0 | 0 |
| clarify | 1 | 0 | 1 | 0 | 1 | 1 |
| direct | 2 | 0 | 19 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 4 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 6 | 0 |
| web_search | 2 | 0 | 1 | 0 | 1 | 5 |

### hybrid-clf

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 6 | 0 | 0 | 0 | 0 | 0 |
| clarify | 0 | 2 | 1 | 0 | 1 | 0 |
| direct | 1 | 0 | 20 | 0 | 0 | 0 |
| multi | 0 | 0 | 0 | 4 | 0 | 0 |
| weather | 0 | 0 | 0 | 0 | 6 | 0 |
| web_search | 1 | 1 | 1 | 0 | 0 | 6 |


## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 87.5% | 100.0% | 100.0% | 100.0% | 86.7% |
| embeddings | 62.5% | 92.3% | 75.0% | 100.0% | 33.3% |
| hybrid | 75.0% | 100.0% | 100.0% | 100.0% | 86.7% |
| classifier | 62.5% | 100.0% | 100.0% | 100.0% | 80.0% |
| hybrid-clf | 87.5% | 100.0% | 100.0% | 100.0% | 86.7% |

## Accuracy by confidence bucket (lenient)

| Router | bucket | n | accuracy |
|---|---|---|---|
| rules | high (>=0.8) | 18 | 94.4% |
| rules | mid (0.5-0.8) | 32 | 93.8% |
| embeddings | high (>=0.8) | 20 | 90.0% |
| embeddings | low (<0.5) | 5 | 80.0% |
| embeddings | mid (0.5-0.8) | 25 | 52.0% |
| hybrid | high (>=0.8) | 28 | 89.3% |
| hybrid | low (<0.5) | 1 | 100.0% |
| hybrid | mid (0.5-0.8) | 21 | 95.2% |
| classifier | high (>=0.8) | 10 | 100.0% |
| classifier | low (<0.5) | 12 | 75.0% |
| classifier | mid (0.5-0.8) | 28 | 89.3% |
| hybrid-clf | high (>=0.8) | 19 | 94.7% |
| hybrid-clf | low (<0.5) | 5 | 100.0% |
| hybrid-clf | mid (0.5-0.8) | 26 | 92.3% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.022 | 0.023 | 0.034 | 0.041 |
| embeddings | 5.974 | 5.489 | 10.638 | 10.913 |
| hybrid | 3.571 | 5.325 | 5.984 | 6.439 |
| classifier | 5.984 | 5.533 | 10.496 | 10.867 |
| hybrid-clf | 3.650 | 5.337 | 6.328 | 6.593 |

## Decision paths: hybrid

| path | queries |
|---|---|
| hybrid(rules) | 19 |
| hybrid(agree) | 9 |
| hybrid(rules-after-abstain) | 7 |
| hybrid(veto) | 6 |
| hybrid(embeddings) | 4 |
| hybrid(fallback) | 3 |
| hybrid(clarify) | 2 |

## Decision paths: hybrid-clf

| path | queries |
|---|---|
| hybrid-clf(rules) | 19 |
| hybrid-clf(agree) | 15 |
| hybrid-clf(fallback) | 6 |
| hybrid-clf(rules-after-abstain) | 4 |
| hybrid-clf(clarify) | 3 |
| hybrid-clf(classifier) | 2 |
| hybrid-clf(veto) | 1 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 7 | 542.3 | 456.5 | 1531.0 | 72.92 | 2.01 | 466.8 |
| clarify | 2 | 23.1 | 21.1 | 25.2 | 23.05 | 0.00 | 0.0 |
| direct | 22 | 2092.2 | 2068.8 | 3334.3 | 17.70 | 0.00 | 2074.2 |
| multi | 4 | 520.2 | 1.8 | 2078.0 | 11.93 | 0.45 | 507.7 |
| weather | 9 | 46.0 | 9.2 | 291.0 | 45.34 | 0.63 | 0.0 |
| web_search | 6 | 6.9 | 0.2 | 26.1 | 6.80 | 0.10 | 0.0 |

## Errors per router

### rules (3 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 23 | Calculate the average yearly rainfall in Singapore | web_search | calculator | 0.70 | incorrect_tool |
| 25 | Convert 100 USD to SGD | web_search | direct | 0.50 | missed_tool |
| 37 | What's 5 plus the number of planets? | direct | calculator | 0.88 | unnecessary_tool |

### embeddings (15 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 14 | Look up the opening hours of the Louvre | web_search | weather | 0.50 | incorrect_tool |
| 18 | How do I calculate compound interest? | direct | calculator | 0.50 | unnecessary_tool |
| 19 | What is the boiling point of water in Fahrenheit? | direct | weather | 0.67 | unnecessary_tool |
| 20 | Write a haiku about rain | direct | weather | 0.53 | unnecessary_tool |
| 21 | What's the temperature of the sun's surface? | direct | weather | 0.76 | unnecessary_tool |
| 22 | What is the derivative of x squared? | direct | calculator | 0.78 | unnecessary_tool |
| 23 | Calculate the average yearly rainfall in Singapore | web_search | weather | 0.84 | incorrect_tool |
| 25 | Convert 100 USD to SGD | web_search | calculator | 0.50 | incorrect_tool |
| 26 | What is 10 degrees Celsius in Fahrenheit? | calculator | weather | 0.71 | incorrect_tool |
| 31 | Explain how weather forecasting models work | direct | weather | 0.76 | unnecessary_tool |
| 32 | Tell me about Singapore | direct | weather | 0.39 | unnecessary_tool |
| 34 | How many days until Christmas? | clarify | weather | 0.52 | incorrect_tool |
| 38 | How much is it? | clarify | calculator | 0.53 | incorrect_tool |
| 40 | What time is it in Tokyo? | web_search | weather | 0.87 | incorrect_tool |
| 49 | Calculate 45 * 3 and then explain what a prime number is | ['calculator', 'direct'] | calculator,calculator | 0.50 | multi_step |

### hybrid (4 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 23 | Calculate the average yearly rainfall in Singapore | web_search | weather | 0.84 | incorrect_tool |
| 25 | Convert 100 USD to SGD | web_search | direct | 0.50 | missed_tool |
| 37 | What's 5 plus the number of planets? | direct | calculator | 0.88 | unnecessary_tool |
| 40 | What time is it in Tokyo? | web_search | weather | 0.87 | incorrect_tool |

### classifier (6 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 18 | How do I calculate compound interest? | direct | calculator | 0.59 | unnecessary_tool |
| 23 | Calculate the average yearly rainfall in Singapore | web_search | calculator | 0.30 | incorrect_tool |
| 25 | Convert 100 USD to SGD | web_search | calculator | 0.56 | incorrect_tool |
| 37 | What's 5 plus the number of planets? | direct | calculator | 0.44 | unnecessary_tool |
| 38 | How much is it? | clarify | calculator | 0.55 | incorrect_tool |
| 40 | What time is it in Tokyo? | web_search | weather | 0.36 | incorrect_tool |

### hybrid-clf (3 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 23 | Calculate the average yearly rainfall in Singapore | web_search | calculator | 0.70 | incorrect_tool |
| 25 | Convert 100 USD to SGD | web_search | clarify | 0.56 | missed_tool |
| 37 | What's 5 plus the number of planets? | direct | calculator | 0.88 | unnecessary_tool |

