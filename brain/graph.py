from __future__ import annotations

from langgraph.graph import StateGraph, END

from brain.schema import TaskState
from brain.nodes import classify_and_extract, resolve_when


def route_after_classify(state: TaskState) -> str:
    """Decide the next node based on verb."""
    if state.verb in ("capture", "remind"):
        return "resolve_when"
    return END


# ── Build ───────────────────────────────────────────────────────────────────
builder = StateGraph(TaskState)

builder.add_node("classify", classify_and_extract)
builder.add_node("resolve_when", resolve_when)

builder.set_entry_point("classify")

builder.add_conditional_edges(
    "classify",
    route_after_classify,
    {
        "resolve_when": "resolve_when",
        END: END,
    },
)
builder.add_edge("resolve_when", END)

graph = builder.compile()


# ── Public helper ───────────────────────────────────────────────────────────
def run(text: str) -> TaskState:
    """Entry point for router.py.  Returns a fully-populated TaskState."""
    initial = TaskState(raw_input=text)
    result = graph.invoke(initial)
    # LangGraph returns a dict when state is a Pydantic model
    if isinstance(result, dict):
        return TaskState(**result)
    return result
