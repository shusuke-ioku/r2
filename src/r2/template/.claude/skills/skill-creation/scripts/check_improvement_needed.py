#!/usr/bin/env python3
"""Lightweight check for whether skills need improvement.

No API calls — reads only SQLite and local state files.
Designed to be called at session end for a quick nudge.
"""

import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path


def check_improvement_needed(
    skills_dir: Path,
    db_path: Path,
    min_events_since_last: int = 15,
    days_since_last: int = 14,
    min_total_events: int = 5,
) -> list[dict]:
    """Return list of skills that should be improved, with reasons.

    This function is cheap (SQLite reads only, no API calls).
    """
    if not db_path.exists():
        return []

    # Load state
    state_path = skills_dir / ".improvement_state.json"
    state = json.loads(state_path.read_text()) if state_path.exists() else {}

    # Get usage stats
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT skill_name, COUNT(*) as count, "
            "AVG(confidence) as avg_conf "
            "FROM usage GROUP BY skill_name"
        ).fetchall()
    finally:
        conn.close()

    usage = {
        row["skill_name"]: {"count": row["count"], "avg_confidence": round(row["avg_conf"], 3)}
        for row in rows
    }

    # Check each skill with enough events
    candidates = []
    for name, stats in usage.items():
        if stats["count"] < min_total_events:
            continue

        skill_state = state.get(name, {})
        last_improved = skill_state.get("last_improved")
        events_at_last = skill_state.get("events_at_last_improve", 0)
        new_events = stats["count"] - events_at_last

        reasons = []

        if last_improved:
            days = (datetime.now() - datetime.fromisoformat(last_improved)).days
            if days >= days_since_last and new_events >= min_events_since_last:
                reasons.append(f"{new_events} new events, {days} days since last improvement")
        else:
            if new_events >= min_events_since_last:
                reasons.append(f"never improved, {new_events} events accumulated")
            elif stats["avg_confidence"] < 0.6:
                reasons.append(f"never improved, low confidence ({stats['avg_confidence']:.2f})")

        if stats["avg_confidence"] < 0.6:
            reasons.append(f"low avg confidence ({stats['avg_confidence']:.2f})")

        if reasons:
            candidates.append({
                "skill": name,
                "reasons": reasons,
                "events": stats["count"],
                "avg_confidence": stats["avg_confidence"],
            })

    candidates.sort(key=lambda x: x["avg_confidence"])
    return candidates


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check if skills need improvement")
    parser.add_argument("--skills-dir", required=True)
    parser.add_argument("--db", required=True)
    parser.add_argument("--min-events", type=int, default=15)
    parser.add_argument("--days", type=int, default=14)
    args = parser.parse_args()

    candidates = check_improvement_needed(
        skills_dir=Path(args.skills_dir),
        db_path=Path(args.db),
        min_events_since_last=args.min_events,
        days_since_last=args.days,
    )

    if candidates:
        print(f"{len(candidates)} skill(s) may benefit from improvement:")
        for c in candidates:
            print(f"  - {c['skill']}: {', '.join(c['reasons'])}")
        print("\nRun /improve-skills to review and optimize.")
    else:
        print("All skills look healthy.")

    return len(candidates)


if __name__ == "__main__":
    sys.exit(0 if main() == 0 else 0)
