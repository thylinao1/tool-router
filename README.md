# Tool Router

A small GenAI assistant that decides, for each user request, whether to answer
directly with an LLM or to pass the request to one of three tools (`calculator`,
`weather`, `web_search`). The routing decision is made without the LLM's
native tool calling, without function-calling APIs, and without any prompt
whose purpose is to output a tool name. The LLM is used only to generate
answers.

Three routers are implemented and compared on the same evaluation set:

| Router | Mechanism | Median latency | Accuracy |
|---|---|---|---|
| `rules` | weighted regular-expression rules per route, combined with noisy-OR | 0.02 ms | 94.0% lenient, 80.0% strict |
| `embeddings` | nearest labelled examples with `all-MiniLM-L6-v2` | 5 ms | 70.0% lenient, 66.0% strict |
| `hybrid` | rules first, embeddings as a second opinion, explicit `clarify` decision | 5 ms | 92.0% lenient, 88.0% strict |

On this set the rule router scores one query higher than the hybrid on lenient
accuracy; the same person wrote the rules and the evaluation set, which favours
the rules. The hybrid scores higher on strict accuracy and on both held-out
sets. On the first held-out set the frozen system scored 77.3%, which revealed
a flaw in the ambiguity policy. After that one change, a second held-out set
(a slot-by-slot paraphrase of the first) scored 100.0%. The Evaluation section
gives the details and the caveats.

Full tables, per-query predictions and error lists are in [`results/results.md`](results/results.md).
Example traces are in [`results/examples.md`](results/examples.md).

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# route one query and answer it (uses Ollama llama3.2:3b if running, otherwise a mock LLM)
.venv/bin/python cli.py "What is 245 * 18?"
.venv/bin/python cli.py --decision-only "Write a haiku about rain"
.venv/bin/python cli.py --router rules "Who won the latest Formula 1 race?"
.venv/bin/python cli.py --on-ambiguous direct "How much is it?"     # answer instead of asking

# tests and evaluation
.venv/bin/python -m pytest -q
.venv/bin/python -m eval.run_eval              # writes results/
.venv/bin/python -m eval.run_eval --no-llm     # same, with the mock LLM for direct answers
.venv/bin/python -m eval.run_eval --dataset eval/heldout2.jsonl --out results/heldout2
```

The first run downloads the sentence-transformer model (about 90 MB). The
tools are mocked: the calculator evaluates real arithmetic in a restricted
parser, the weather tool returns fixed conditions for ten cities and
deterministic pseudo-data elsewhere, and web search returns fixed snippets.
The routing logic is the subject of the project.

## How routing works

### Routes and the registry

Every route, including `direct`, is a `RouteSpec` in `router/tools.py`:

```python
RouteSpec(
    name="weather",
    description="a weather report for a location",                  # used in clarification questions
    examples=["Is it going to rain in London tomorrow?", ...],      # embedding prototypes
    patterns=[("weather_word", r"\b(weather|forecast|temperature|...)\b", 0.85)],  # rule, weight
    exclusions=[("not_a_place", r"\b(boiling|melting|sun|oven|...)\b")],           # veto
    handler=weather,                                                  # None for direct
)
```

Treating `direct` as a route with its own examples and patterns makes the
question "does this request need a tool at all?" an ordinary classification
decision rather than a special case. It is also why adding a tool is a single
registry entry (see "Adding a tool" below).

### Router 1: rules

Each rule is `(name, regex, weight)`. A route's score is the noisy-OR of the
weights of the rules that matched: `score = 1 - prod(1 - w_i)`. Several weak
matches accumulate, one strong match is sufficient, and the score never
exceeds 1. If any exclusion regex matches, the route's score is set to 0 and
the route is recorded as vetoed.

Confidence is `top_score - 0.5 * runner_up_score`, clipped to `[0, 1]`. When
two routes both match, confidence decreases instead of selecting the marginal
winner. If no rule matched anything, the router returns `direct` at
confidence 0.5 and marks the decision as abstained.

Example, `"What is 245 * 18?"`:

```
calculator: arithmetic_expression (0.95) and what_is_number (0.60) matched
            score = 1 - (1-0.95)(1-0.60) = 0.98
others:     no match, 0
confidence = 0.98 - 0.5 * 0 = 0.98      -> calculator
```

Example, `"Is it raining today?"`:

```
weather:    weather_word (0.85)          score 0.85
web_search: time_now (0.40)              score 0.40
confidence = 0.85 - 0.5 * 0.40 = 0.65   -> weather, below the hybrid's fast-path threshold
```

Example, `"What is the derivative of x squared?"`: the `math_verb` rule
matches for calculator, but the `conceptual_math` exclusion (`derivative`)
vetoes it, so calculator scores 0 and the decision is `direct` with
`vetoed=["calculator"]`.

### Router 2: embeddings

Every example utterance in the registry is encoded once with
`sentence-transformers/all-MiniLM-L6-v2` (22M parameters, CPU). A query is
encoded and compared by cosine similarity against all examples. A route's score
is the mean similarity of its three most similar examples; using the mean of
the top three rather than the single best reduces the influence of one
unusually similar prototype.

Route scores go through a softmax with temperature 0.08 and the winner's
probability is the confidence. Two routes with similar scores give a confidence
near 0.5, which is the signal the hybrid uses to detect ambiguity.

Softmax compares routes with each other only, so a second check applies: if
the best route's top-3 mean cosine is below 0.30, no route has close examples,
the confidence is capped at 0.5 and the decision is marked abstained. This
check is not a rare out-of-distribution guard. It applies to 36% of the
evaluation queries, mostly general questions that are far from every
prototype, and it is the main reason such questions end up as low-confidence
direct answers in the hybrid rather than as clarifications.

Example, `"What is the weather in Singapore today?"`:

```
top-3 mean cosine:  weather 0.60, web_search 0.25, direct 0.25, calculator 0.18
softmax(scores / 0.08): weather 0.99   -> weather, confidence 0.99
```

Example, `"Write a haiku about rain"`:

```
weather 0.37, direct 0.35    -> softmax gives weather 0.53
```

The embedding router routes this query incorrectly: "rain" places the query
close to weather prototypes and 0.53 is only slightly above an even split.
The rule router routes it correctly because a creative-writing exclusion
vetoes weather. This is the general pattern in the results: embeddings
generalise to paraphrase but respond to surface topic, while rules are
precise but cover only the phrasings that were written down.

### Router 3: hybrid

`HybridRouter` runs the rules first and calls the embedding model only when
the rules are not confident. The decision procedure, in order:

1. Rules confident (`>= 0.8`) and not abstained: take the rule decision. No embedding call.
2. Embeddings selected a route that a rule vetoed: take the rule decision. A veto overrides the embedding choice.
3. Embeddings abstained (no route has close examples): take the rule decision if the rules had any signal, otherwise ambiguous. Tagged `rules-after-abstain` to keep it distinct from step 1.
4. Rules abstained (nothing matched): take the embedding decision if `>= 0.6`, otherwise ambiguous.
5. Both have signal and agree: that route, with the mean of the two confidences.
6. Both have signal and disagree: the embedding decision only if `>= 0.8`, otherwise ambiguous.

An ambiguous outcome does not always produce a question. A wrong tool call
has the higher cost (latency, and possibly an unusable answer), while a direct
answer to a general question has a low cost. The ambiguous branch therefore
asks the user only when the leading candidate is a tool and at least one
router had some signal. If neither router had any signal, or if the leading
candidate is already `direct`, the assistant answers directly at a confidence
capped at 0.5 and records the reason. Building the router with
`on_ambiguous="direct"` disables clarification entirely.

Examples from the evaluation set:

| Query | Rules | Embeddings | Hybrid path | Decision |
|---|---|---|---|---|
| What is 245 * 18? | calculator 0.98 | not called | step 1 | calculator |
| Why do cats purr? | direct 0.70 (`why do`) | abstained (top-3 mean 0.27) | step 3 | direct |
| What's the temperature of the sun's surface? | direct, weather vetoed (`sun`) | weather 0.76 | step 2 | direct |
| How many seconds are in a day? | abstained | calculator 0.86 | step 4 | calculator |
| How much is it? | abstained | calculator 0.53 | step 4, tool leads | clarify |
| Tell me a fun fact about octopuses | abstained | direct 0.44, abstained | step 3, both abstained | direct, capped at 0.5 |
| Convert 100 USD to SGD | abstained | calculator 0.50, abstained | step 3, both abstained | direct (incorrect) |
| What time is it in Tokyo? | abstained | weather 0.87 | step 4 | weather (incorrect) |

On the 50-query set the paths divide as follows: 19 queries were resolved
without calling the embedding model (step 1), 9 were agreements, 7 fell back
to rules after the encoder abstained (step 3), 6 were vetoes, 4 were embedding
decisions, 3 were low-confidence direct answers and 2 were clarifications.

### The structured decision

Every router returns a `RoutingDecision`:

```json
{
  "route": "calculator",
  "confidence": 0.98,
  "reason": "matched arithmetic_expression, what_is_number for calculator (score 0.98)",
  "router": "hybrid(rules)",
  "candidates": [["calculator", 0.98], ["weather", 0.0], ["web_search", 0.0], ["direct", 0.0]],
  "vetoed": [],
  "abstained": false,
  "latency_ms": 0.03
}
```

`reason` is built from the rule names or the nearest example, so each decision
can be traced to its evidence. `router` records which hybrid path was taken,
which is how the path counts above were produced.

### Ambiguity: two layers

Ambiguity is handled at two levels, which cover different cases.

* Router level. When neither router is confident and a tool is the leading
  candidate, the decision is `clarify` and the assistant asks which of the top
  two candidates the user meant: "I am not sure whether you want a calculation
  or a web search for current information. Which one did you mean?" When the
  leading candidate is `direct`, or no router has any signal, the assistant
  answers directly at low confidence instead of asking.
* Tool level. A confidently routed query can still lack required information.
  `"What's the weather?"` routes to weather at 0.85 (the word itself is
  unambiguous) and the tool returns `needs_input` with its own question:
  "Which location would you like the weather for?" The assistant relays it.
  Each step in the trace records `asked_by` as `"router"`, `"tool"` or `null`,
  so the two layers can be distinguished in the results.

The `on_ambiguous` setting selects between the two failure modes: `clarify`
never calls the wrong tool but costs the user a turn; `direct` always answers
but may answer from outdated knowledge when a tool was required.

### Fallback behaviour

If a tool is chosen and then fails (`ToolResult.status == "error"`), the
assistant answers with the LLM instead, prefixes the answer with
"(calculator could not handle this, answering directly)", and sets
`fallback: true` in the trace. Requests over 500 characters are refused
before routing, which also bounds the regular-expression work a single query
can cause. `"How many seconds are in a day?"` is the typical case: the hybrid
routes it to the calculator, the expression extractor finds no arithmetic, and
the LLM answers. The routing was reasonable, the tool was too limited, and the
user still receives an answer.

### Multi-step routing

`split_compound_query` splits on `and`, `and then`, `also`, `then` and `;`,
but only when every resulting part reads as a request on its own (it starts
with a question or command word, or contains arithmetic). Each part is routed
and executed separately and the answers are joined.

```
"What's the weather in Tokyo and what is 12 * 7?"   -> ["weather", "calculator"]
"What is the difference between TCP and UDP?"       -> not split ("UDP?" is not a request)
"Add 14 and 27 and multiply the result by 2"        -> not split ("27" is not a request)
```

This handles independent sub-requests. It does not handle dependent ones
("search for the Bitcoin price and multiply it by 0.5"), which would require
the output of step 1 to be passed into step 2. See Limitations.

### Adding a tool

`tests/test_new_tool.py` registers a `unit_converter` with five example
utterances, one regex rule and a handler, then asserts that all three routers
route `"Convert 5 km to miles"` to it and that the assistant returns
`3.11 miles`. No router code changes. The embedding router encodes the new
examples when it is constructed; the rule router compiles the new patterns.

## Evaluation

### Dataset

`eval/dataset.jsonl` has 50 queries:

| Category | n | What it tests |
|---|---|---|
| clear | 13 | unambiguous tool requests |
| no_tool | 10 | explanations, writing, translation, greetings |
| overlap | 15 | surface words that belong to one route, intent that belongs to another (`"Explain how weather forecasting models work"`) |
| ambiguous | 8 | missing referents or no suitable tool (`"How much is it?"`, `"What time is it in Tokyo?"`) |
| multi | 4 | compound requests |

Each item has a primary `expected` route and an `acceptable` list. For
`"Who is the current president of France?"` the primary is `web_search`
(the answer changes over time) and `direct` is acceptable. For ambiguous
items `clarify` is usually acceptable and sometimes primary.

The evaluator refuses to run if any evaluation query is a verbatim copy of a
registry example (`check_no_leakage`). This check is limited: it does not
detect entity-swapped paraphrases, and it places no constraint on the rule
regexes, which were written with the evaluation set in view. The rules, the
prototypes and the evaluation set were all written by the same person, and
both the exclusion lists and the prototype sets were extended after the first
evaluation run (see "Design iterations").

To estimate how much this affects the numbers, two further sets were written
after tuning. `eval/heldout.jsonl` (22 queries) was run against the frozen
system; that run revealed a flaw in the ambiguity policy and led to iteration
4, so its later re-run is not a held-out score. `eval/heldout2.jsonl`
(22 queries) was then written and run once against the final system. It
mirrors the first set slot by slot (same category and label shape per
position, paraphrased queries), so it measures whether the iteration-4 change
holds up under paraphrase; it is not an independent sample of new traffic.

### Metrics

All rates use the full dataset size as the denominator.

| Metric | Definition |
|---|---|
| accuracy (lenient) | predicted route is in the item's `acceptable` list |
| accuracy (strict) | predicted route equals the primary `expected` route |
| incorrect tool selection rate | a tool was chosen, the primary expected route is a different tool or clarify, and the chosen tool is not acceptable |
| unnecessary tool-call rate | a tool was chosen where `direct` was the primary route and that tool was not acceptable |
| missed tool rate | `direct` or `clarify` was chosen where a tool was expected and not acceptable |
| clarify rate | fraction of decisions that asked for clarification |
| abstain rate | fraction of decisions where the router reported no real signal (rules: nothing matched; embeddings: no close examples) |
| router latency | median of `--runs` timed calls per query (default 5, recorded in the results) after a warm-up call, `perf_counter` |
| end-to-end latency | `Assistant.handle()` wall time divided into routing, tool and LLM time, per route |

Multi-step items count as correct only if the predicted route sequence equals
the labelled one; a single-step item that is split counts as incorrect.

### Results

Routing quality on the 50-query set:

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|
| rules | 94.0% | 80.0% | 2.0% | 2.0% | 2.0% | 0.0% | 24.0% |
| embeddings | 70.0% | 66.0% | 14.0% | 14.0% | 0.0% | 0.0% | 36.0% |
| hybrid | 92.0% | 88.0% | 4.0% | 2.0% | 2.0% | 4.0% | 12.0% |

The hybrid's higher strict accuracy comes from the ambiguous category: the
rule router has no way to express uncertainty, so each ambiguous item it
scores correctly on is a default to `direct` that happened to match the label.
The hybrid's four errors are two incorrect tools (`"What time is it in
Tokyo?"` and `"Calculate the average yearly rainfall in Singapore"` to
weather), one unnecessary tool (`"What's 5 plus the number of planets?"` to
the calculator, which then fails and falls back to the LLM) and one missed
tool (`"Convert 100 USD to SGD"` answered directly, where the live rate
required a search).

The embedding router's errors are almost all of one kind: a query that
mentions a place or a temperature-related word is drawn to weather, and a
query that mentions calculating is drawn to the calculator, regardless of
intent. Rules with exclusions address these cases, which is why the hybrid
recovers them.

Held-out sets (22 queries each):

The first held-out set against the frozen v1 system (kept in `results/heldout-v1-frozen/`):

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Clarify rate |
|---|---|---|---|---|---|---|
| rules | 90.9% | 81.8% | 0.0% | 0.0% | 9.1% | 0.0% |
| embeddings | 86.4% | 81.8% | 9.1% | 4.5% | 0.0% | 0.0% |
| hybrid | 77.3% | 77.3% | 0.0% | 4.5% | 4.5% | 22.7% |

This run led to design iteration 4. After the policy change the same set
gives the figures below. These are a re-run on a set that had already been
examined, not a held-out score:

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|
| rules | 90.9% | 81.8% | 0.0% | 0.0% | 9.1% | 0.0% | 31.8% |
| embeddings | 86.4% | 81.8% | 9.1% | 4.5% | 0.0% | 0.0% | 27.3% |
| hybrid | 95.5% | 90.9% | 0.0% | 0.0% | 4.5% | 0.0% | 22.7% |

The second held-out set was written after that change and run once against
the final system. It mirrors the first set slot by slot, so it contains a
paraphrase of every query the first run got wrong. It therefore tests whether
the change generalises across phrasing rather than sampling new queries:

| Router | Accuracy (lenient) | Accuracy (strict) | Incorrect tool | Unnecessary tool | Missed tool | Clarify rate | Abstain rate |
|---|---|---|---|---|---|---|---|
| rules | 90.9% | 77.3% | 0.0% | 0.0% | 9.1% | 0.0% | 31.8% |
| embeddings | 81.8% | 77.3% | 4.5% | 13.6% | 0.0% | 0.0% | 36.4% |
| hybrid | 100.0% | 90.9% | 0.0% | 0.0% | 0.0% | 0.0% | 18.2% |

The hybrid's two strict misses on the second set are the two ambiguous items
where `clarify` was the primary label and a direct answer was acceptable
(`"And?"`, `"How's it looking?"`). The rule router missed two tool requests
that contain no trigger word (`"Will it be foggy at Heathrow tomorrow
morning?"`, `"Which movies are showing in Singapore cinemas this weekend?"`);
the embedding router sent `"Proofread this sentence: their going to the park"`
to weather. The hybrid recovered all of these cases.

### Latency

Router latency in isolation (median of 5 calls per query, after warm-up, Apple M2, CPU only):

| Router | mean | p50 | p95 | max |
|---|---|---|---|---|
| rules | 0.022 | 0.023 | 0.036 | 0.038 |
| embeddings | 5.983 | 5.461 | 10.328 | 10.487 |
| hybrid | 3.489 | 5.184 | 5.789 | 6.234 |

The hybrid's mean is below the embedding router's because 19 of 50 queries
(38.0%) resolve on the rule fast path without calling the encoder.

End-to-end latency per route, hybrid router, local `llama3.2:3b` through Ollama:

| Route | n | total mean | total p50 | total p95 | routing | tool | LLM |
|---|---|---|---|---|---|---|---|
| calculator | 7 | 517.4 | 51.3 | 1603.8 | 13.9 | 1.17 | 501.8 |
| clarify | 2 | 21.1 | 14.9 | 27.2 | 21.0 | 0.00 | 0.0 |
| direct | 22 | 2238.8 | 2314.9 | 3423.2 | 17.2 | 0.00 | 2221.4 |
| multi | 4 | 713.8 | 5.4 | 2848.7 | 53.3 | 1.38 | 658.9 |
| weather | 9 | 45.4 | 8.7 | 339.8 | 45.1 | 0.26 | 0.0 |
| web_search | 6 | 6.3 | 0.2 | 24.5 | 6.2 | 0.10 | 0.0 |

Three observations follow from this table.

* The LLM accounts for most of the time. A direct answer takes about 2.3 s on
  this laptop; a weather or search route answers in about 10 ms. Routing cost
  is small relative to either. With real tools behind the mocks (200 to 800 ms
  per call), the router's own speed matters less than avoiding unnecessary
  calls, which is why the unnecessary-tool rate is reported alongside accuracy.
* The calculator mean is raised by fallbacks. Three calculator-routed queries
  (`"What is 10 degrees Celsius in Fahrenheit?"`, `"How many seconds are in a
  day?"`, `"What's 5 plus the number of planets?"`) had no parseable
  expression, so the assistant fell back to the LLM. The calculator's p50 of
  51 ms is the cost of the tool path itself; the mean of 517 ms reflects the
  tool's limited scope.
* Embedding calls are slower immediately after an LLM call. On the shared CPU,
  encoder routing took a median of 23 ms when the previous query had run the
  LLM and 10 ms otherwise (cold caches and idle threads). This is why the
  per-route routing column is higher than the isolated router latency above.

### Comparison of the approaches

* Rules cost tens of microseconds and are precise on the phrasings they were
  written for. They do not generalise to paraphrases that were not
  anticipated, and each new phrasing requires a person to add a rule. Their
  high score here is partly due to the same person writing the rules and the
  evaluation set.
* Embeddings generalise across phrasing without rule writing and cost about
  6 ms per query on a laptop CPU. Their weakness is that a small general
  encoder responds to surface topic (places, "calculate", "temperature")
  rather than to what the user wants done, so overlapping intents are where
  they fail.
* The hybrid resolves 38.0% of queries on the rule path and calls the encoder
  only when the rules are not confident. Vetoes and abstentions let each
  router cover cases the other cannot, and low confidence becomes a
  clarifying question (when a tool leads) or a low-confidence direct answer
  instead of an incorrect tool call. It still inherits the encoder's
  place-name bias where no rule matches or the encoder is confident enough to
  override a weak rule (`"What time is it in Tokyo?"` and `"Calculate the
  average yearly rainfall in Singapore"` both go to weather).

### Scalability

Three quantities grow, with different effects. More tools add rules and
prototypes: rule cost is linear in the number of regexes and remains in the
microsecond range, and embedding cost is one encoder pass plus a dot product
against every prototype (a few hundred prototypes remain under a millisecond
after encoding), but every new route also re-normalises the softmax, so
thresholds need to be re-checked after each addition. Query volume is bounded
by the encoder: at about 6 ms per query on one laptop core, a single process
handles roughly a hundred queries per second before batching or a second
process is needed, and the rule path removes a share of traffic from the
encoder. New phrasings are the main ongoing cost: rules require a person to
add each one, prototypes require a labelled example, and neither scales
without someone reviewing the failures.

## Design decisions

* Confidence has a defined meaning for each router (rule score minus half the
  runner-up; softmax probability with an absolute-similarity cap) rather than
  being a value selected for presentation. The accuracy-by-confidence table in
  `results/results.md` shows whether low confidence predicts errors.
* Thresholds (`rule_accept=0.8`, `embed_accept=0.6`, `strong_accept=0.8`,
  `min_similarity=0.3`) were chosen by examining the confidence distribution
  on the evaluation set. A production system would hold out a separate
  calibration split; the held-out sets above are a small version of that.
* The LLM is a local model (`llama3.2:3b` through Ollama) so the whole
  pipeline runs offline on a laptop. When Ollama is not running, the
  evaluator falls back to a mock LLM and records this in the results.
* The calculator is real but restricted: expressions are parsed with `ast`
  and only numeric constants, arithmetic operators and `sqrt` are evaluated.
  `__import__("os")` is rejected as a parse error and never executed.

### Design iterations

The first evaluation run scored the hybrid at 72%, below the rule router
alone. Three changes were made, all general rather than query-specific:

1. The embedding router gained the absolute-similarity cap. Before it, `"What
   time is it in Tokyo?"` was routed to weather at 0.99 because softmax only
   compares routes with each other.
2. The hybrid was changed to treat a rule veto as overriding and an embedding
   abstention as the absence of a signal. Before that, `"Why do cats purr?"`
   became a clarification because the two routers "disagreed" when one of
   them had no signal.
3. The prototype sets were rebalanced: every weather example contained a
   city, so any query naming a place moved toward weather. Weather examples
   without places, and direct and search examples with places, were added.
   Two exclusions (creative writing is not a forecast request; a unit
   conversion between Celsius and Fahrenheit is not weather) and four
   factual-question prototypes for `direct` were added as well.
4. The first held-out run (results kept in `results/heldout-v1-frozen/`)
   showed the hybrid at 77% lenient, below both single routers, with a 23%
   clarify rate. Three of its five errors were clarifications on general
   questions (`"What does HTTP stand for?"`, `"Tell me a fun fact about
   octopuses"`): both routers had weak signal and the hybrid asked
   "calculation or web search?", which is a worse outcome than answering. The
   ambiguity policy was changed to clarify only when a tool is the leading
   candidate, and `explain` was added to the calculator's conceptual-math
   exclusion for consistency with the weather exclusion that already
   contained it. Because that held-out set had now been examined, a second
   one was written and run once.
5. An independent review of the finished project found, among smaller items,
   that this document had quoted the re-run of the first held-out set as a
   held-out score, that the "fast path" count had merged step 1 with step 3,
   that the abstain check was described as a nearest-example rule when it
   uses the top-3 mean, and that three labels credited a tool that could not
   answer the query (yearly rainfall to weather; days until Christmas and
   "5 plus the number of planets" to the calculator). The labels were
   corrected and the numbers above are from the rerun. Routing decisions did
   not change; the corrections affected scores, not behaviour.

Changes of this kind are a continuing maintenance cost for any system based
on rules or prototypes.

## Limitations

* Small, single-author evaluation. 50 plus 22 queries, labelled by the
  person who wrote the routers. Production traffic would contain phrasings
  that none of the rules or prototypes cover.
* The encoder responds to topic rather than intent. `all-MiniLM-L6-v2` is a
  general sentence encoder. `"What time is it in Tokyo?"` still routes to
  weather because "in Tokyo" outweighs "what time". A small classifier
  fine-tuned on labelled routing data, or a cross-encoder reranker, would
  address this at the cost of training data and latency.
* Multi-step routing covers independent steps only. Sub-requests that depend
  on each other's output are not chained.
* Mock tools. Real weather and search APIs would add 200 to 800 ms per call,
  which changes the latency profile: the router's 6 ms becomes negligible and
  the relevant figure becomes how often an unnecessary tool call is made.
* Clarification has no memory. The assistant asks the user which route they
  meant but does not carry the answer into the next turn.
* Adding a route changes every confidence. The embedding confidence is a
  softmax over all routes, so registering a fifth route re-normalises the
  other four and can change decisions near a threshold. The add-a-tool test
  shows that the new tool is reachable, not that existing decisions are
  unchanged.
* English only, and the rule regexes assume it.

## Possible improvements

* Replace the top-3-mean scoring with a logistic regression over the embedding
  (a few hundred labelled queries would be sufficient) and calibrate its
  probabilities with a held-out split.
* Chain dependent multi-step requests by substituting a step's answer into
  the next step's query.
* Let the LLM rephrase tool output for the user (currently the tool text is
  returned verbatim to keep tool routes at millisecond latency).
* Cache query embeddings for repeated queries.

## Project layout

```
router/
  schema.py      RoutingDecision
  tools.py       RouteSpec, ToolRegistry, calculator / weather / web_search, default registry
  rules.py       RuleRouter
  embeddings.py  EmbeddingRouter
  hybrid.py      HybridRouter
  multistep.py   compound-query splitting
  llm.py         OllamaLLM, MockLLM
  app.py         Assistant: route, execute, answer, latency trace, 500-character cap
eval/
  dataset.jsonl  50 evaluation queries
  heldout.jsonl  22 post-tuning queries (v1, led to iteration 4)
  heldout2.jsonl 22 post-tuning queries (v2, run once against the final system)
  run_eval.py    metrics, latency, results writer
results/         metrics.json, results.md, examples.md, predictions.jsonl, e2e.jsonl
                 (+ heldout/, heldout2/, heldout-v1-frozen/)
tests/           39 pytest tests, including the add-a-tool test
cli.py           one-shot command line
```
