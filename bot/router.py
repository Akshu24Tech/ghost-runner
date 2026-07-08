from __future__ import annotations


def _brain_reply(text: str) -> str:
    """Run text through the LangGraph graph and format the result."""
    from brain.graph import run  # local import keeps startup fast if brain is slow

    state = run(text)

    if state.verb == "capture":
        if state.due and not state.error:
            due_str = state.due.strftime("%a %Y-%m-%d %H:%M")
            return f"capture: \"{state.title}\" — due {due_str}"
        elif state.error == "when_unclear":
            return f"capture: \"{state.title}\" — when? (couldn't parse date)"
        else:
            return f"capture: \"{state.title}\""

    if state.verb == "remind":
        if state.due:
            due_str = state.due.strftime("%a %Y-%m-%d %H:%M")
            return f"remind: \"{state.title}\" at {due_str}"
        return f"remind: \"{state.title}\" — when? (couldn't parse date)"

    if state.verb == "brief":
        return f"brief: \"{state.title}\" — (briefing not yet implemented)"

    # unknown / error
    err = f" [{state.error}]" if state.error else ""
    return f"unknown{err} — I didn't understand that. Try /help."


def route(text: str) -> str:
    """Return the reply string for text. Pure function — no side effects."""
    cmd = text.strip().lower().split()[0] if text.strip() else ""

    if cmd in ("/start", "/help"):
        return (
            "Ghost Runner online.\n"
            "Commands I know:\n"
            "  /start — this message\n"
            "  /ping  — check I'm alive\n"
            "  /help  — same as /start\n"
            "Or just tell me a task: \"assignment X due friday 5pm\""
        )

    if cmd == "/ping":
        return "pong"

    # Not a slash-command → brain
    return _brain_reply(text)
