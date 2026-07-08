from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

from dateutil import parser as du_parser
from langchain_ollama import ChatOllama

from brain.schema import TaskState

log = logging.getLogger(__name__)

# ── LLM setup ──────────────────────────────────────────────────────────────
llm = ChatOllama(model="llama3.2", temperature=0, format="json")

SYSTEM = """\
You are a task-extraction assistant. Given a message, return ONLY valid JSON with exactly these keys:
  "verb"     : one of "capture", "brief", "remind" — or "unknown" if none fit
  "title"    : short task title string, or null
  "raw_when" : the exact time/date phrase the user wrote, or null

verb meanings:
  capture — save / note / log a task or assignment
  brief   — summarise or give info about something
  remind  — set a reminder

Do NOT add any text outside the JSON object.
Example output: {"verb": "capture", "title": "DBMS unit 3", "raw_when": "friday 5pm"}
"""

VALID_VERBS = {"capture", "brief", "remind", "unknown"}


# ── Node 1 ─────────────────────────────────────────────────────────────────
def classify_and_extract(state: TaskState) -> TaskState:
    """Call the LLM once (with one retry) to classify verb and extract fields."""
    updates: dict = {}

    for attempt in range(2):
        try:
            messages = [
                ("system", SYSTEM),
                ("human", state.raw_input),
            ]
            resp = llm.invoke(messages)
            raw = resp.content.strip()

            # Small models sometimes wrap JSON in markdown fences — strip them
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()

            data = json.loads(raw)

            verb = str(data.get("verb", "unknown")).lower().strip()
            if verb not in VALID_VERBS:
                log.warning("LLM returned invalid verb %r → mapping to 'unknown'", verb)
                verb = "unknown"

            updates = {
                "verb": verb,
                "title": data.get("title") or None,
                "raw_when": data.get("raw_when") or None,
            }
            log.info("classify OK (attempt %d): %s", attempt + 1, updates)
            break

        except (json.JSONDecodeError, KeyError, Exception) as exc:
            log.warning("classify attempt %d failed: %s", attempt + 1, exc)
            if attempt == 1:
                updates = {
                    "verb": "unknown",
                    "error": f"classify_failed: {exc}",
                }

    return state.model_copy(update=updates)


# ── Node 2 ─────────────────────────────────────────────────────────────────

# Bare-date policy (v0 decision, not an accident):
# If the user says "friday" with no time, we treat it as 09:00.
# "next friday" = the coming Friday, not the one after — revisit if users complain.
BARE_DATE_HOUR = 9


def resolve_when(state: TaskState) -> TaskState:
    """Resolve state.raw_when → state.due using Python only.  No LLM."""
    if not state.raw_when:
        return state.model_copy(update={"error": "when_unclear"})

    now = datetime.now()

    # Clean default: strip minutes/seconds so dateutil can't inherit them.
    # "friday 5pm" says nothing about minutes → we want 17:00, not 17:32.
    # Hour is set to BARE_DATE_HOUR so a bare "friday" resolves to 09:00
    # rather than whatever hour it currently is.
    default = now.replace(
        hour=BARE_DATE_HOUR,
        minute=0,
        second=0,
        microsecond=0,
    )

    try:
        # Normalize words dateutil's fuzzy mode silently skips.
        # "noon" and "midnight" are unambiguous; replace them before parsing
        # so dateutil sees clock values it can't misread.
        raw = state.raw_when.lower()
        raw = raw.replace("noon", "12:00").replace("midnight", "00:00")

        due = du_parser.parse(raw, fuzzy=True, default=default)

        # Enforce future: if the resolved datetime is in the past, push it
        # forward by 7 days (handles "friday" on a Friday or past dates).
        if due <= now:
            due += timedelta(days=7)

        log.info("resolved %r → %s", state.raw_when, due.isoformat())
        return state.model_copy(update={"due": due})

    except (ValueError, OverflowError) as exc:
        log.warning("date parse failed for %r: %s", state.raw_when, exc)
        return state.model_copy(update={"error": "when_unclear"})
