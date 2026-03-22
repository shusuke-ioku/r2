"""SQLite-backed usage tracking for skills."""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from r2.skills_engine.config import SkillsConfig, get_config
from r2.skills_engine.models import UsageEvent


def _get_db_path(config: SkillsConfig | None = None) -> Path:
    if config is None:
        config = get_config()
    return config.resolve(config.usage_db_path)


def _get_conn(config: SkillsConfig | None = None) -> sqlite3.Connection:
    db_path = _get_db_path(config)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            query TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn


def log_usage(
    skill_name: str,
    query: str,
    confidence: float,
    config: SkillsConfig | None = None,
) -> UsageEvent:
    """Record a skill dispatch/usage event."""
    event = UsageEvent(
        skill_name=skill_name,
        query=query,
        confidence=confidence,
        timestamp=datetime.now(),
    )
    conn = _get_conn(config)
    try:
        conn.execute(
            "INSERT INTO usage (skill_name, query, confidence, timestamp) VALUES (?, ?, ?, ?)",
            (event.skill_name, event.query, event.confidence, event.timestamp.isoformat()),
        )
        conn.commit()
    finally:
        conn.close()
    return event


def query_usage(
    skill_name: str | None = None,
    limit: int = 50,
    config: SkillsConfig | None = None,
) -> list[dict]:
    """Query usage history. Optionally filter by skill name."""
    conn = _get_conn(config)
    try:
        if skill_name:
            rows = conn.execute(
                "SELECT skill_name, query, confidence, timestamp FROM usage "
                "WHERE skill_name = ? ORDER BY timestamp DESC LIMIT ?",
                (skill_name, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT skill_name, query, confidence, timestamp FROM usage "
                "ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            ).fetchall()
    finally:
        conn.close()

    return [
        {
            "skill_name": r[0],
            "query": r[1],
            "confidence": r[2],
            "timestamp": r[3],
        }
        for r in rows
    ]


def get_usage_stats(config: SkillsConfig | None = None) -> dict:
    """Get aggregated usage statistics."""
    conn = _get_conn(config)
    try:
        total = conn.execute("SELECT COUNT(*) FROM usage").fetchone()[0]
        by_skill = conn.execute(
            "SELECT skill_name, COUNT(*) as cnt, AVG(confidence) as avg_conf "
            "FROM usage GROUP BY skill_name ORDER BY cnt DESC"
        ).fetchall()
        recent = conn.execute(
            "SELECT skill_name, query, confidence, timestamp FROM usage "
            "ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
    finally:
        conn.close()

    return {
        "total_events": total,
        "by_skill": [
            {"name": r[0], "count": r[1], "avg_confidence": round(r[2], 3)}
            for r in by_skill
        ],
        "recent": [
            {"skill": r[0], "query": r[1][:80], "confidence": r[2], "timestamp": r[3]}
            for r in recent
        ],
    }
