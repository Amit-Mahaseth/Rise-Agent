"""
RiseAgent AI — Database layer.
Provides a Supabase client for production and an in-memory fallback
store for demo mode so the dashboard works without Supabase credentials.
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timezone, timedelta
from typing import Any

from config import get_settings

logger = logging.getLogger("riseagent.database")

# ── Supabase client (lazy) ───────────────────────────────────────
_supabase_client = None


def _get_supabase():
    """Return supabase client, creating on first call."""
    global _supabase_client
    if _supabase_client is None:
        settings = get_settings()
        if settings.supabase_url and settings.supabase_service_key:
            from supabase import create_client
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_service_key,
            )
        else:
            logger.warning("Supabase credentials not set — using in-memory store")
            _supabase_client = None
    return _supabase_client


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# In-memory store for demo mode
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

_store: dict[str, list[dict]] = {
    "leads": [],
    "calls": [],
    "call_events": [],
    "scores": [],
    "rm_queue": [],
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Unified CRUD helpers — route to Supabase or in-memory
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def db_insert(table: str, data: dict) -> dict:
    """Insert a row. Returns the inserted row dict."""
    client = _get_supabase()
    if client is not None:
        try:
            result = client.table(table).insert(data).execute()
            return result.data[0] if result.data else data
        except Exception as exc:
            logger.error("Supabase insert error on %s: %s", table, exc)
            raise
    # In-memory fallback
    if "id" not in data:
        data["id"] = _new_id()
    if "created_at" not in data and "started_at" not in data and "queued_at" not in data:
        data["created_at"] = _now_iso()
    _store.setdefault(table, []).append(data)
    return data


async def db_select(
    table: str,
    filters: dict[str, Any] | None = None,
    order_by: str | None = None,
    order_desc: bool = True,
    limit: int | None = None,
) -> list[dict]:
    """Select rows with optional filters, ordering and limit."""
    client = _get_supabase()
    if client is not None:
        try:
            q = client.table(table).select("*")
            if filters:
                for col, val in filters.items():
                    q = q.eq(col, val)
            if order_by:
                q = q.order(order_by, desc=order_desc)
            if limit:
                q = q.limit(limit)
            result = q.execute()
            return result.data or []
        except Exception as exc:
            logger.error("Supabase select error on %s: %s", table, exc)
            raise
    # In-memory fallback
    rows = _store.get(table, [])
    if filters:
        for col, val in filters.items():
            rows = [r for r in rows if r.get(col) == val]
    if order_by:
        rows = sorted(rows, key=lambda r: r.get(order_by, ""), reverse=order_desc)
    if limit:
        rows = rows[:limit]
    return rows


async def db_update(table: str, row_id: str, data: dict) -> dict:
    """Update a row by id."""
    client = _get_supabase()
    if client is not None:
        try:
            result = client.table(table).update(data).eq("id", row_id).execute()
            return result.data[0] if result.data else data
        except Exception as exc:
            logger.error("Supabase update error on %s: %s", table, exc)
            raise
    # In-memory fallback
    rows = _store.get(table, [])
    for row in rows:
        if row.get("id") == row_id:
            row.update(data)
            return row
    return data


async def db_count(table: str, filters: dict[str, Any] | None = None) -> int:
    """Count rows with optional filters."""
    rows = await db_select(table, filters=filters)
    return len(rows)


# ── Schema SQL (for reference / Supabase migrations) ─────────────
SCHEMA_SQL = """
-- leads
CREATE TABLE IF NOT EXISTS leads (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  phone text NOT NULL UNIQUE,
  language text DEFAULT 'unknown',
  source text,
  status text DEFAULT 'pending',
  created_at timestamptz DEFAULT now(),
  re_engage_after timestamptz
);

-- calls
CREATE TABLE IF NOT EXISTS calls (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  call_sid text UNIQUE,
  provider text,
  status text DEFAULT 'initiated',
  duration_seconds int DEFAULT 0,
  language_used text,
  call_number int DEFAULT 1,
  started_at timestamptz DEFAULT now(),
  ended_at timestamptz
);

-- call_events
CREATE TABLE IF NOT EXISTS call_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  call_id uuid REFERENCES calls(id),
  turn_number int,
  speaker text CHECK (speaker IN ('agent', 'lead')),
  text text,
  language text,
  timestamp timestamptz DEFAULT now()
);

-- scores
CREATE TABLE IF NOT EXISTS scores (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  call_id uuid REFERENCES calls(id),
  total_score int,
  verbal_intent bool DEFAULT false,
  objection_count int DEFAULT 0,
  duration_score int DEFAULT 0,
  network_mentioned bool DEFAULT false,
  tone_score int DEFAULT 0,
  classification text CHECK (classification IN ('hot','warm','cold')),
  created_at timestamptz DEFAULT now()
);

-- rm_queue
CREATE TABLE IF NOT EXISTS rm_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id uuid REFERENCES leads(id),
  call_id uuid REFERENCES calls(id),
  transcript text,
  objections_raised text[],
  rebuttals_used text[],
  recommended_action text,
  rm_status text DEFAULT 'pending',
  queued_at timestamptz DEFAULT now(),
  actioned_at timestamptz
);
"""
