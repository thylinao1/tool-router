"""Assistant: route -> execute -> answer, with per-stage latency and fallbacks.

Fallback rules:
  * route == clarify          -> ask the user which of the top two candidates they meant
  * tool returns needs_input  -> relay the tool's own clarifying question
  * tool returns error        -> answer with the LLM instead, flagged as a fallback
  * a step refers to the previous result but that result has no number -> reported as unresolved
Each step records who asked for clarification, if anyone: "router", "tool" or None, and
whether a value from the previous step was substituted into it.
"""

from __future__ import annotations

import time

from .schema import RoutingDecision, DIRECT, CLARIFY
from .tools import ToolRegistry
from .multistep import split_compound_query, resolve_reference

MAX_QUERY_CHARS = 500
UNRESOLVED = "unresolved"


class Assistant:
    def __init__(self, router, registry: ToolRegistry, llm) -> None:
        self.router = router
        self.registry = registry
        self.llm = llm

    def _describe(self, route: str) -> str:
        return self.registry.get(route).description if route in self.registry.names() else f"the {route} tool"

    def _execute(self, step: str, decision: RoutingDecision) -> dict:
        tool_ms = llm_ms = 0.0
        fallback = False
        asked_by = None
        if decision.route == UNRESOLVED:
            answer = "The previous step did not produce a number, so this step cannot use its result."
        elif decision.route == CLARIFY:
            asked_by = "router"
            names = [self._describe(c[0]) for c in decision.candidates[:2]]
            answer = (f"I can help with that, but I am not sure whether you want {' or '.join(names)}. "
                      f"Which one did you mean?")
        elif decision.route == DIRECT:
            t = time.perf_counter()
            answer = self.llm.generate(step)
            llm_ms = (time.perf_counter() - t) * 1000
        else:
            t = time.perf_counter()
            result = self.registry.get(decision.route).handler(step)
            tool_ms = (time.perf_counter() - t) * 1000
            if result.status == "needs_input":
                asked_by = "tool"
                answer = result.text
            elif result.status == "ok":
                answer = result.text
            else:
                fallback = True
                t = time.perf_counter()
                answer = self.llm.generate(step)
                llm_ms = (time.perf_counter() - t) * 1000
                answer = f"({decision.route} could not handle this, answering directly) {answer}"
        return {"step": step, "decision": decision.to_dict(), "answer": answer,
                "tool_ms": round(tool_ms, 3), "llm_ms": round(llm_ms, 3),
                "fallback": fallback, "asked_by": asked_by}

    def handle(self, query: str) -> dict:
        t0 = time.perf_counter()
        if len(query) > MAX_QUERY_CHARS:
            return {"query": query[:80] + "...", "routes": [], "steps": [],
                    "answer": f"Please keep requests under {MAX_QUERY_CHARS} characters.",
                    "latency_ms": {"routing": 0.0, "tool": 0.0, "llm": 0.0,
                                   "total": round((time.perf_counter() - t0) * 1000, 3)},
                    "fallback": False, "llm": self.llm.name}
        steps = []
        previous_answer = None
        for part in split_compound_query(query):
            text, status, value = resolve_reference(part, previous_answer)
            if status == UNRESOLVED:
                decision = RoutingDecision(route=UNRESOLVED, confidence=0.0, router="dependency", abstained=True,
                                           reason="this step refers to the previous result, but that answer contains no number")
            else:
                decision = self.router.route(text)
            step = self._execute(text, decision)
            step["step"] = part
            step["dependency"] = None if status == "none" else {"status": status, "value": value, "routed_text": text}
            previous_answer = step["answer"]
            steps.append(step)
        total_ms = (time.perf_counter() - t0) * 1000
        return {
            "query": query,
            "routes": [s["decision"]["route"] for s in steps],
            "steps": steps,
            "answer": "\n".join(s["answer"] for s in steps),
            "latency_ms": {
                "routing": round(sum(s["decision"]["latency_ms"] for s in steps), 3),
                "tool": round(sum(s["tool_ms"] for s in steps), 3),
                "llm": round(sum(s["llm_ms"] for s in steps), 3),
                "total": round(total_ms, 3),
            },
            "fallback": any(s["fallback"] for s in steps),
            "llm": self.llm.name,
        }
