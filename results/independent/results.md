# Results

Dataset: 60 queries (labelled.jsonl). Rates use the full dataset as denominator. Router latency is the median of 5 timed calls per query, after one warm-up call, on an Apple M2 (CPU only).

## Routing quality

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Multi-step errors | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|---|
| rules | 31.7% | 25.0% | 5.0% | 1.7% | 33.3% | 15.0% | 0.0% | 65.0% |
| embeddings | 43.3% | 31.7% | 31.7% | 13.3% | 0.0% | 11.7% | 0.0% | 56.7% |
| hybrid | 36.7% | 28.3% | 15.0% | 1.7% | 25.0% | 15.0% | 13.3% | 40.0% |
| classifier | 60.0% | 48.3% | 21.7% | 5.0% | 0.0% | 11.7% | 0.0% | 21.7% |
| hybrid-clf | 60.0% | 51.7% | 10.0% | 0.0% | 8.3% | 15.0% | 11.7% | 16.7% |

## Confusion matrix (primary expected route -> predicted route)

### rules

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 2 | 0 | 7 | 0 | 0 | 1 |
| clarify | 0 | 0 | 8 | 0 | 0 | 1 |
| direct | 0 | 0 | 9 | 0 | 0 | 1 |
| multi | 1 | 0 | 9 | 2 | 0 | 3 |
| weather | 0 | 0 | 0 | 0 | 0 | 0 |
| web_search | 0 | 0 | 13 | 0 | 1 | 2 |

### embeddings

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 10 | 0 | 0 | 0 | 0 | 0 |
| clarify | 2 | 0 | 0 | 0 | 5 | 2 |
| direct | 2 | 0 | 2 | 0 | 4 | 2 |
| multi | 2 | 0 | 2 | 2 | 3 | 6 |
| weather | 0 | 0 | 0 | 0 | 0 | 0 |
| web_search | 0 | 0 | 0 | 0 | 11 | 5 |

### hybrid

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 4 | 1 | 5 | 0 | 0 | 0 |
| clarify | 1 | 2 | 4 | 0 | 2 | 0 |
| direct | 0 | 0 | 9 | 0 | 0 | 1 |
| multi | 1 | 0 | 8 | 2 | 2 | 2 |
| weather | 0 | 0 | 0 | 0 | 0 | 0 |
| web_search | 0 | 4 | 5 | 0 | 7 | 0 |

### classifier

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 10 | 0 | 0 | 0 | 0 | 0 |
| clarify | 2 | 0 | 1 | 0 | 3 | 3 |
| direct | 2 | 0 | 7 | 0 | 0 | 1 |
| multi | 2 | 0 | 2 | 2 | 3 | 6 |
| weather | 0 | 0 | 0 | 0 | 0 | 0 |
| web_search | 0 | 0 | 0 | 0 | 6 | 10 |

### hybrid-clf

| expected \ predicted | calculator | clarify | direct | multi | weather | web_search |
|---|---|---|---|---|---|---|
| calculator | 8 | 2 | 0 | 0 | 0 | 0 |
| clarify | 1 | 2 | 4 | 0 | 1 | 1 |
| direct | 0 | 0 | 10 | 0 | 0 | 0 |
| multi | 1 | 1 | 5 | 2 | 1 | 5 |
| weather | 0 | 0 | 0 | 0 | 0 | 0 |
| web_search | 0 | 1 | 2 | 0 | 4 | 9 |


## Accuracy by query category (lenient)

| Router | ambiguous | clear | multi | no_tool | overlap |
|---|---|---|---|---|---|
| rules | 0.0% | 28.0% | 45.5% | 100.0% | 38.5% |
| embeddings | 11.1% | 64.0% | 63.6% | 0.0% | 15.4% |
| hybrid | 33.3% | 28.0% | 54.5% | 100.0% | 30.8% |
| classifier | 11.1% | 84.0% | 63.6% | 50.0% | 46.2% |
| hybrid-clf | 33.3% | 76.0% | 54.5% | 100.0% | 46.2% |

## Accuracy by confidence bucket (lenient)

| Router | bucket | n | accuracy |
|---|---|---|---|
| rules | high (>=0.8) | 7 | 42.9% |
| rules | low (<0.5) | 7 | 71.4% |
| rules | mid (0.5-0.8) | 46 | 23.9% |
| embeddings | high (>=0.8) | 9 | 55.6% |
| embeddings | low (<0.5) | 17 | 41.2% |
| embeddings | mid (0.5-0.8) | 34 | 41.2% |
| hybrid | high (>=0.8) | 14 | 50.0% |
| hybrid | low (<0.5) | 11 | 36.4% |
| hybrid | mid (0.5-0.8) | 35 | 31.4% |
| classifier | high (>=0.8) | 13 | 69.2% |
| classifier | low (<0.5) | 13 | 38.5% |
| classifier | mid (0.5-0.8) | 34 | 64.7% |
| hybrid-clf | high (>=0.8) | 16 | 56.2% |
| hybrid-clf | low (<0.5) | 12 | 41.7% |
| hybrid-clf | mid (0.5-0.8) | 32 | 68.8% |

## Router latency (ms)

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.043 | 0.041 | 0.062 | 0.066 |
| embeddings | 6.314 | 6.078 | 6.607 | 13.246 |
| hybrid | 5.622 | 6.066 | 6.771 | 12.627 |
| classifier | 7.135 | 6.188 | 9.918 | 18.017 |
| hybrid-clf | 5.595 | 6.017 | 7.202 | 11.787 |

## Decision paths: hybrid

| path | queries |
|---|---|
| hybrid(fallback) | 23 |
| hybrid(embeddings) | 14 |
| hybrid(clarify) | 8 |
| hybrid(rules) | 7 |
| hybrid(rules-after-abstain) | 5 |
| hybrid(agree) | 2 |
| hybrid(veto) | 1 |

## Decision paths: hybrid-clf

| path | queries |
|---|---|
| hybrid-clf(classifier) | 27 |
| hybrid-clf(fallback) | 10 |
| hybrid-clf(rules) | 7 |
| hybrid-clf(clarify) | 7 |
| hybrid-clf(agree) | 6 |
| hybrid-clf(rules-after-abstain) | 2 |
| hybrid-clf(veto) | 1 |

## End-to-end latency per route (hybrid router, LLM = ollama)

| Route | n | total mean | total p50 | total p95 | routing | tool | llm |
|---|---|---|---|---|---|---|---|
| calculator | 6 | 1650.1 | 1356.1 | 3051.7 | 40.30 | 0.32 | 1609.2 |
| clarify | 7 | 25.5 | 29.5 | 34.8 | 25.40 | 0.00 | 0.0 |
| direct | 31 | 2008.9 | 1880.2 | 3286.7 | 17.62 | 0.00 | 1991.1 |
| multi | 2 | 694.8 | 33.9 | 1355.8 | 33.28 | 0.07 | 661.3 |
| weather | 11 | 22.5 | 26.8 | 32.8 | 22.26 | 0.15 | 0.0 |
| web_search | 3 | 8.6 | 12.2 | 13.5 | 8.41 | 0.19 | 0.0 |

## Errors per router

### rules (41 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 1 | 14 hours at 13.50 an hour, what does that come to | clarify | direct | 0.50 | other |
| 2 | chance of thunderstorms over pulau ubin saturday afternoon? planning to cycle there | clarify | direct | 0.50 | other |
| 4 | has the RTS link to JB opened yet or is it still under construction | web_search | direct | 0.50 | missed_tool |
| 6 | How muggy is Penang going to be on Tuesday? Trying to figure out if I can survive in jeans. | multi | direct | 0.50 | multi_step |
| 7 | same but for sunday | clarify | direct | 0.50 | other |
| 9 | 4 kopi at 1.80 and 2 kaya toast sets at 3.20, total? | calculator | direct | 0.50 | missed_tool |
| 11 | when is the next NUS career fair, i think i missed the email | multi | direct | 0.80 | multi_step |
| 12 | how much is a return ferry ticket to bintan these days | web_search | direct | 0.50 | missed_tool |
| 13 | whats the uv index looking like in bintan tomorrow morning | web_search | direct | 0.50 | missed_tool |
| 15 | how do i cite a youtube video in APA 7 | clarify | direct | 0.50 | other |
| 17 | when does the NUS financial aid application for next academic year close | web_search | direct | 0.50 | missed_tool |
| 18 | clementi looking wet in the next hour? deciding if i walk to the mrt or just grab | web_search | direct | 0.50 | missed_tool |
| 21 | split 96.30 three ways and write me a short paylah reminder i can send the other two | multi | direct | 0.80 | multi_step |
| 22 | allowance 1250, rent 380, phone 95, grab 42.60, what's left | calculator | direct | 0.50 | missed_tool |
| 24 | so how much do i owe her | clarify | direct | 0.50 | other |
| 25 | give me two caption ideas for a bintan sunset photo, nothing cringe | multi | direct | 0.50 | multi_step |
| 29 | what's the latest on the haze this week, bad enough that they'd cancel the outdoor orientation camp? | multi | web_search | 0.82 | multi_step |
| 30 | if i run 5.2 km at 6 min 15 per km how long does that take | calculator | direct | 0.50 | missed_tool |
| 31 | what's it doing outside in Frankfurt right now | clarify | web_search | 0.40 | incorrect_tool |
| 32 | Has the Spurs manager actually gone or is that still just rumours? | multi | direct | 0.50 | multi_step |
| 33 | split 4,860 across 9 sites, what does each site get | calculator | direct | 0.50 | missed_tool |
| 35 | Any frost forecast for Leeds overnight? Got a 6am drive up. | web_search | weather | 0.85 | incorrect_tool |
| 37 | why's the FTSE off this morning | multi | direct | 0.50 | multi_step |
| 38 | three shifts of 11 people, two call in sick on each, how many are actually on the floor | calculator | direct | 0.50 | missed_tool |
| 39 | same again but for friday | clarify | direct | 0.50 | other |
| 40 | highs and lows for Madrid thursday through sunday pls | clarify | direct | 0.50 | other |
| 41 | what's the national living wage going up to in april, need it for the budget | web_search | direct | 0.50 | missed_tool |
| 43 | Has the Bank of England decision landed yet, and can you tell me in one line what a hawkish hold means? | multi | direct | 0.50 | multi_step |
| 45 | Does it look like it'll clear up over Manchester by kick-off on Saturday? | web_search | direct | 0.50 | missed_tool |
| 46 | give me a three line agenda for a 20 min catch-up with the night shift leads | multi | direct | 0.50 | multi_step |
| 47 | who's chelsea actually signed this window so far | web_search | direct | 0.50 | missed_tool |
| 48 | has the newcastle game been moved for tv or is it still sunday 2pm | web_search | direct | 0.50 | missed_tool |
| 49 | Warehouse did 14,320 units last month and 16,105 this month. What's that as a percentage increase? | calculator | web_search | 0.40 | incorrect_tool |
| 51 | Rotterdam wed evening, am I landing into a downpour or is it fine? | web_search | direct | 0.50 | missed_tool |
| 52 | what about the other site? | clarify | direct | 0.50 | other |
| 53 | how many pallets is 1,860 boxes at 24 a pallet, round up | calculator | direct | 0.50 | missed_tool |
| 54 | is the tube strike on thursday still going ahead | web_search | direct | 0.50 | missed_tool |
| 55 | FIFO vs LIFO for stock rotation, plain english, two sentences max | direct | web_search | 0.60 | unnecessary_tool |
| 56 | Dublin saturday lunchtime, dry enough to sit outside? | web_search | direct | 0.50 | missed_tool |
| 57 | £38.50 a head for 27 people with 20% VAT on top, what's the damage | calculator | direct | 0.50 | missed_tool |
| 60 | Rolls-Royce results were out this morning, what did they say on guidance? | web_search | direct | 0.50 | missed_tool |

### embeddings (34 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 1 | 14 hours at 13.50 an hour, what does that come to | clarify | calculator | 0.67 | incorrect_tool |
| 3 | Explain the big O of a nested for loop in a way I can actually remember for Thursday's quiz. | direct | calculator | 0.67 | unnecessary_tool |
| 5 | rewrite this so it sounds less passive aggressive: as per my last email, your section was due monday | direct | weather | 0.37 | unnecessary_tool |
| 7 | same but for sunday | clarify | weather | 0.65 | incorrect_tool |
| 10 | Write a short text to my shift manager asking to swap my Saturday shift for Sunday. Casual but not sloppy. | direct | weather | 0.38 | unnecessary_tool |
| 13 | whats the uv index looking like in bintan tomorrow morning | web_search | weather | 0.70 | incorrect_tool |
| 15 | how do i cite a youtube video in APA 7 | clarify | web_search | 0.38 | incorrect_tool |
| 18 | clementi looking wet in the next hour? deciding if i walk to the mrt or just grab | web_search | weather | 0.78 | incorrect_tool |
| 19 | is it actually bad to eat instant noodles for dinner five nights in a row, asking for a friend (me) | direct | weather | 0.31 | unnecessary_tool |
| 21 | split 96.30 three ways and write me a short paylah reminder i can send the other two | multi | calculator | 0.50 | multi_step |
| 23 | Is the Deepavali public holiday this year giving us a Friday or a Monday off? | web_search | weather | 0.76 | incorrect_tool |
| 24 | so how much do i owe her | clarify | calculator | 0.50 | incorrect_tool |
| 25 | give me two caption ideas for a bintan sunset photo, nothing cringe | multi | direct | 0.50 | multi_step |
| 26 | My stats prof lost me on p-values. Can you walk through one slowly with a coin flip example? | direct | calculator | 0.50 | unnecessary_tool |
| 27 | will the skies be clear at east coast park tonight, there's supposed to be a meteor shower | multi | weather | 0.96 | multi_step |
| 28 | will it still be drizzling around bugis at 7 tonight? meeting friends for dinner | web_search | weather | 0.73 | incorrect_tool |
| 29 | what's the latest on the haze this week, bad enough that they'd cancel the outdoor orientation camp? | multi | weather | 0.72 | multi_step |
| 31 | what's it doing outside in Frankfurt right now | clarify | weather | 0.78 | incorrect_tool |
| 35 | Any frost forecast for Leeds overnight? Got a 6am drive up. | web_search | weather | 0.92 | incorrect_tool |
| 37 | why's the FTSE off this morning | multi | web_search | 0.42 | multi_step |
| 39 | same again but for friday | clarify | weather | 0.50 | incorrect_tool |
| 40 | highs and lows for Madrid thursday through sunday pls | clarify | weather | 0.50 | incorrect_tool |
| 41 | what's the national living wage going up to in april, need it for the budget | web_search | weather | 0.48 | incorrect_tool |
| 42 | Is it affect or effect in 'this will ___ the delivery schedule'? | direct | weather | 0.50 | unnecessary_tool |
| 43 | Has the Bank of England decision landed yet, and can you tell me in one line what a hawkish hold means? | multi | web_search | 0.45 | multi_step |
| 45 | Does it look like it'll clear up over Manchester by kick-off on Saturday? | web_search | weather | 0.68 | incorrect_tool |
| 46 | give me a three line agenda for a 20 min catch-up with the night shift leads | multi | web_search | 0.49 | multi_step |
| 48 | has the newcastle game been moved for tv or is it still sunday 2pm | web_search | weather | 0.60 | incorrect_tool |
| 51 | Rotterdam wed evening, am I landing into a downpour or is it fine? | web_search | weather | 0.92 | incorrect_tool |
| 52 | what about the other site? | clarify | web_search | 0.50 | incorrect_tool |
| 54 | is the tube strike on thursday still going ahead | web_search | weather | 0.74 | incorrect_tool |
| 55 | FIFO vs LIFO for stock rotation, plain english, two sentences max | direct | web_search | 0.38 | unnecessary_tool |
| 56 | Dublin saturday lunchtime, dry enough to sit outside? | web_search | weather | 0.86 | incorrect_tool |
| 59 | What's the polite way to chase an invoice that's 30 days overdue without sounding like a debt collector? | direct | web_search | 0.28 | unnecessary_tool |

### hybrid (38 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 1 | 14 hours at 13.50 an hour, what does that come to | clarify | calculator | 0.67 | incorrect_tool |
| 4 | has the RTS link to JB opened yet or is it still under construction | web_search | direct | 0.50 | missed_tool |
| 7 | same but for sunday | clarify | weather | 0.65 | incorrect_tool |
| 11 | when is the next NUS career fair, i think i missed the email | multi | direct | 0.80 | multi_step |
| 12 | how much is a return ferry ticket to bintan these days | web_search | direct | 0.46 | missed_tool |
| 13 | whats the uv index looking like in bintan tomorrow morning | web_search | weather | 0.70 | incorrect_tool |
| 15 | how do i cite a youtube video in APA 7 | clarify | direct | 0.38 | other |
| 17 | when does the NUS financial aid application for next academic year close | web_search | direct | 0.43 | missed_tool |
| 18 | clementi looking wet in the next hour? deciding if i walk to the mrt or just grab | web_search | weather | 0.78 | incorrect_tool |
| 21 | split 96.30 three ways and write me a short paylah reminder i can send the other two | multi | direct | 0.80 | multi_step |
| 23 | Is the Deepavali public holiday this year giving us a Friday or a Monday off? | web_search | clarify | 0.76 | missed_tool |
| 24 | so how much do i owe her | clarify | direct | 0.50 | other |
| 25 | give me two caption ideas for a bintan sunset photo, nothing cringe | multi | direct | 0.50 | multi_step |
| 27 | will the skies be clear at east coast park tonight, there's supposed to be a meteor shower | multi | weather | 0.96 | multi_step |
| 28 | will it still be drizzling around bugis at 7 tonight? meeting friends for dinner | web_search | clarify | 0.73 | missed_tool |
| 29 | what's the latest on the haze this week, bad enough that they'd cancel the outdoor orientation camp? | multi | web_search | 0.82 | multi_step |
| 30 | if i run 5.2 km at 6 min 15 per km how long does that take | calculator | direct | 0.50 | missed_tool |
| 32 | Has the Spurs manager actually gone or is that still just rumours? | multi | direct | 0.50 | multi_step |
| 33 | split 4,860 across 9 sites, what does each site get | calculator | direct | 0.50 | missed_tool |
| 35 | Any frost forecast for Leeds overnight? Got a 6am drive up. | web_search | weather | 0.85 | incorrect_tool |
| 37 | why's the FTSE off this morning | multi | direct | 0.42 | multi_step |
| 38 | three shifts of 11 people, two call in sick on each, how many are actually on the floor | calculator | direct | 0.50 | missed_tool |
| 39 | same again but for friday | clarify | direct | 0.50 | other |
| 41 | what's the national living wage going up to in april, need it for the budget | web_search | clarify | 0.48 | missed_tool |
| 43 | Has the Bank of England decision landed yet, and can you tell me in one line what a hawkish hold means? | multi | direct | 0.45 | multi_step |
| 45 | Does it look like it'll clear up over Manchester by kick-off on Saturday? | web_search | weather | 0.68 | incorrect_tool |
| 46 | give me a three line agenda for a 20 min catch-up with the night shift leads | multi | direct | 0.49 | multi_step |
| 47 | who's chelsea actually signed this window so far | web_search | direct | 0.50 | missed_tool |
| 48 | has the newcastle game been moved for tv or is it still sunday 2pm | web_search | clarify | 0.60 | missed_tool |
| 49 | Warehouse did 14,320 units last month and 16,105 this month. What's that as a percentage increase? | calculator | clarify | 0.62 | missed_tool |
| 51 | Rotterdam wed evening, am I landing into a downpour or is it fine? | web_search | weather | 0.92 | incorrect_tool |
| 52 | what about the other site? | clarify | direct | 0.50 | other |
| 53 | how many pallets is 1,860 boxes at 24 a pallet, round up | calculator | direct | 0.50 | missed_tool |
| 54 | is the tube strike on thursday still going ahead | web_search | weather | 0.74 | incorrect_tool |
| 55 | FIFO vs LIFO for stock rotation, plain english, two sentences max | direct | web_search | 0.60 | unnecessary_tool |
| 56 | Dublin saturday lunchtime, dry enough to sit outside? | web_search | weather | 0.86 | incorrect_tool |
| 57 | £38.50 a head for 27 people with 20% VAT on top, what's the damage | calculator | direct | 0.50 | missed_tool |
| 60 | Rolls-Royce results were out this morning, what did they say on guidance? | web_search | direct | 0.50 | missed_tool |

### classifier (24 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 1 | 14 hours at 13.50 an hour, what does that come to | clarify | calculator | 0.69 | incorrect_tool |
| 3 | Explain the big O of a nested for loop in a way I can actually remember for Thursday's quiz. | direct | calculator | 0.51 | unnecessary_tool |
| 7 | same but for sunday | clarify | web_search | 0.40 | incorrect_tool |
| 13 | whats the uv index looking like in bintan tomorrow morning | web_search | weather | 0.51 | incorrect_tool |
| 15 | how do i cite a youtube video in APA 7 | clarify | direct | 0.49 | other |
| 18 | clementi looking wet in the next hour? deciding if i walk to the mrt or just grab | web_search | weather | 0.62 | incorrect_tool |
| 21 | split 96.30 three ways and write me a short paylah reminder i can send the other two | multi | calculator | 0.68 | multi_step |
| 24 | so how much do i owe her | clarify | calculator | 0.59 | incorrect_tool |
| 25 | give me two caption ideas for a bintan sunset photo, nothing cringe | multi | direct | 0.68 | multi_step |
| 26 | My stats prof lost me on p-values. Can you walk through one slowly with a coin flip example? | direct | calculator | 0.45 | unnecessary_tool |
| 27 | will the skies be clear at east coast park tonight, there's supposed to be a meteor shower | multi | weather | 0.85 | multi_step |
| 28 | will it still be drizzling around bugis at 7 tonight? meeting friends for dinner | web_search | weather | 0.43 | incorrect_tool |
| 29 | what's the latest on the haze this week, bad enough that they'd cancel the outdoor orientation camp? | multi | weather | 0.64 | multi_step |
| 31 | what's it doing outside in Frankfurt right now | clarify | weather | 0.51 | incorrect_tool |
| 35 | Any frost forecast for Leeds overnight? Got a 6am drive up. | web_search | weather | 0.89 | incorrect_tool |
| 37 | why's the FTSE off this morning | multi | web_search | 0.73 | multi_step |
| 39 | same again but for friday | clarify | web_search | 0.43 | incorrect_tool |
| 40 | highs and lows for Madrid thursday through sunday pls | clarify | weather | 0.32 | incorrect_tool |
| 42 | Is it affect or effect in 'this will ___ the delivery schedule'? | direct | web_search | 0.48 | unnecessary_tool |
| 43 | Has the Bank of England decision landed yet, and can you tell me in one line what a hawkish hold means? | multi | web_search | 0.74 | multi_step |
| 46 | give me a three line agenda for a 20 min catch-up with the night shift leads | multi | web_search | 0.42 | multi_step |
| 51 | Rotterdam wed evening, am I landing into a downpour or is it fine? | web_search | weather | 0.91 | incorrect_tool |
| 52 | what about the other site? | clarify | web_search | 0.62 | incorrect_tool |
| 56 | Dublin saturday lunchtime, dry enough to sit outside? | web_search | weather | 0.84 | incorrect_tool |

### hybrid-clf (24 errors)

| id | query | expected | predicted | conf | error |
|---|---|---|---|---|---|
| 1 | 14 hours at 13.50 an hour, what does that come to | clarify | calculator | 0.69 | incorrect_tool |
| 6 | How muggy is Penang going to be on Tuesday? Trying to figure out if I can survive in jeans. | multi | clarify | 0.55 | multi_step |
| 7 | same but for sunday | clarify | direct | 0.40 | other |
| 11 | when is the next NUS career fair, i think i missed the email | multi | direct | 0.80 | multi_step |
| 13 | whats the uv index looking like in bintan tomorrow morning | web_search | clarify | 0.51 | missed_tool |
| 15 | how do i cite a youtube video in APA 7 | clarify | direct | 0.49 | other |
| 18 | clementi looking wet in the next hour? deciding if i walk to the mrt or just grab | web_search | weather | 0.62 | incorrect_tool |
| 21 | split 96.30 three ways and write me a short paylah reminder i can send the other two | multi | direct | 0.80 | multi_step |
| 25 | give me two caption ideas for a bintan sunset photo, nothing cringe | multi | direct | 0.68 | multi_step |
| 27 | will the skies be clear at east coast park tonight, there's supposed to be a meteor shower | multi | weather | 0.85 | multi_step |
| 29 | what's the latest on the haze this week, bad enough that they'd cancel the outdoor orientation camp? | multi | web_search | 0.82 | multi_step |
| 35 | Any frost forecast for Leeds overnight? Got a 6am drive up. | web_search | weather | 0.85 | incorrect_tool |
| 37 | why's the FTSE off this morning | multi | web_search | 0.73 | multi_step |
| 38 | three shifts of 11 people, two call in sick on each, how many are actually on the floor | calculator | clarify | 0.50 | missed_tool |
| 39 | same again but for friday | clarify | direct | 0.43 | other |
| 40 | highs and lows for Madrid thursday through sunday pls | clarify | direct | 0.32 | other |
| 41 | what's the national living wage going up to in april, need it for the budget | web_search | direct | 0.48 | missed_tool |
| 43 | Has the Bank of England decision landed yet, and can you tell me in one line what a hawkish hold means? | multi | web_search | 0.74 | multi_step |
| 45 | Does it look like it'll clear up over Manchester by kick-off on Saturday? | web_search | direct | 0.48 | missed_tool |
| 46 | give me a three line agenda for a 20 min catch-up with the night shift leads | multi | direct | 0.42 | multi_step |
| 49 | Warehouse did 14,320 units last month and 16,105 this month. What's that as a percentage increase? | calculator | clarify | 0.71 | missed_tool |
| 51 | Rotterdam wed evening, am I landing into a downpour or is it fine? | web_search | weather | 0.91 | incorrect_tool |
| 52 | what about the other site? | clarify | web_search | 0.62 | incorrect_tool |
| 56 | Dublin saturday lunchtime, dry enough to sit outside? | web_search | weather | 0.84 | incorrect_tool |

