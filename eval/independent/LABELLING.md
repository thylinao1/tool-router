# Independent labelling set

`to_label.jsonl` contains queries written by people other than the author of
the routers, prototypes and rules. Labelling them independently gives a
measurement that the main evaluation set cannot: the rules and prototypes were
written with that set in view, this one was not.

## How to label

Open `to_label.jsonl`. Each line is one item:

```json
{"id": 1, "query": "...", "expected": "", "acceptable": [], "category": ""}
```

Fill in three fields for every item:

* `expected`: the single best route. One of `calculator`, `weather`,
  `web_search`, `direct`, `clarify`. Use `multi` when the message contains two
  separate requests, and add `"steps": ["weather", "calculator"]` in order.
* `acceptable`: every route you would accept as a reasonable decision,
  including the expected one. Leave it as `[expected]` when only one route is
  defensible. Add `clarify` when asking the user would also be reasonable.
* `category`: one of `clear`, `overlap`, `ambiguous`, `no_tool`, `multi`.
  Use `overlap` when the wording contains a word typical of another route.

Route definitions:

| Route | Use when |
|---|---|
| `calculator` | the answer is arithmetic on numbers present in the text (15% of 80, 12 squared plus 7, minutes in three days) |
| `weather` | current conditions or a forecast for a place or time |
| `web_search` | the answer needs current or external information: news, scores, prices, rates, who currently holds a role, opening hours, events |
| `direct` | the assistant can answer from general knowledge: explanations, stable facts, writing, translation, advice, code |
| `clarify` | the request is too underspecified to route (no referent, no location where one is required, or two routes equally plausible) |

Label from the user's intent, not from the words. "Explain how weather
forecasting works" is `direct`; "how many seconds in a day" is `calculator`
with `direct` acceptable.

Do not look at the router's output or at `eval/dataset.jsonl` while labelling.
The file has 60 items. If that is too many, label the first 40 and delete the
remaining lines; the evaluator scores whatever the file contains.

## How `multi` is scored

If a labelled file uses `multi` without an ordered `steps` list, the
evaluator applies two rules:

* An item whose `expected` is `multi` counts as strictly correct only if the
  router split the message into two or more steps. It counts as leniently
  correct if the router split it, or if the router's single route appears in
  the item's `acceptable` list.
* An item whose `acceptable` list contains `multi` counts as leniently
  correct if the router split the message, in addition to the usual rule.

Both rules use only what the labeller wrote. Adding `"steps": [...]` to a
`multi` item gives exact sequence scoring instead.

## Recommended procedure for a golden set

Use three or more labellers who did not write the routers. Each labels the
file independently, then disagreements are discussed and one adjudicated
label is kept per item. Record the agreement rate before adjudication. Score
every router once against the adjudicated file and do not tune afterwards.

## Scoring

Save the completed file as `labelled.jsonl` in this folder and run:

```bash
.venv/bin/python -m eval.run_eval --dataset eval/independent/labelled.jsonl --out results/independent
```

The evaluator refuses to run while any item has an empty `expected` field.
Results appear in `results/independent/results.md` in the same format as the
main evaluation.
