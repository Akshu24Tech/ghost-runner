def route(text: str) -> str:
    """Return the reply string for text. Pure function — no side effects."""
    cmd = text.strip().lower().split()[0] if text.strip() else ""

    if cmd in ("/start", "/help"):
        return (
            "Ghost Runner online.\n"
            "Commands I know:\n"
            "  /start — this message\n"
            "  /ping  — check I'm alive\n"
            "  /help  — same as /start"
        )

    if cmd == "/ping":
        return "pong"

    # Anything unrecognised: echo with a prefix so routing is visually confirmed.
    return f"[UNROUTED] {text}"
