from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TaskState(BaseModel):
    # ── input ──────────────────────────────────────────────────────────────
    raw_input: str = ""

    # ── LLM fills these ────────────────────────────────────────────────────
    verb: Literal["capture", "brief", "remind", "unknown"] = "unknown"
    title: str | None = None
    raw_when: str | None = None   # exactly what the user typed: "friday 5pm"

    # ── code fills this ────────────────────────────────────────────────────
    due: datetime | None = None   # resolved by resolve_when node, never by LLM

    # ── diagnostics ────────────────────────────────────────────────────────
    error: str | None = None
