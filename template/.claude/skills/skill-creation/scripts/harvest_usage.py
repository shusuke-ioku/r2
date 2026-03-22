#!/usr/bin/env python3
"""Extract and label real queries from the skills engine usage database.

Produces eval-set-compatible entries from actual dispatched queries.
"""

import json
import sqlite3
from pathlib import Path


def harvest_usage(
    db_path: Path,
    skill_name: str,
    confidence_threshold_pos: float = 0.7,
    confidence_threshold_neg: float = 0.7,
    max_negatives_per_skill: int = 5,
    exclude_queries: set[str] | None = None,
) -> dict:
    """Harvest real queries from usage DB for a given skill.

    Returns:
        {
            "positives": [{"query": ..., "should_trigger": True}, ...],
            "negatives": [{"query": ..., "should_trigger": False}, ...],
            "ambiguous": [{"query": ..., "confidence": ..., "dispatched_to": ...}, ...],
        }
    """
    exclude = {q.lower().strip() for q in (exclude_queries or set())}

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        # Positive candidates: queries dispatched TO this skill with high confidence
        pos_rows = conn.execute(
            "SELECT DISTINCT query, confidence FROM usage "
            "WHERE skill_name = ? AND confidence >= ? "
            "ORDER BY confidence DESC",
            (skill_name, confidence_threshold_pos),
        ).fetchall()

        # Ambiguous: queries dispatched to this skill with low confidence
        amb_rows = conn.execute(
            "SELECT DISTINCT query, confidence FROM usage "
            "WHERE skill_name = ? AND confidence < ? "
            "ORDER BY confidence DESC",
            (skill_name, confidence_threshold_pos),
        ).fetchall()

        # Negative candidates: queries dispatched to OTHER skills with high confidence
        neg_rows = conn.execute(
            "SELECT DISTINCT query, skill_name as dispatched_to, confidence FROM usage "
            "WHERE skill_name != ? AND confidence >= ? "
            "ORDER BY confidence DESC "
            "LIMIT ?",
            (skill_name, confidence_threshold_neg, max_negatives_per_skill * 10),
        ).fetchall()
    finally:
        conn.close()

    seen = set()

    def dedup(query: str) -> bool:
        key = query.lower().strip()
        if key in seen or key in exclude:
            return False
        seen.add(key)
        return True

    positives = []
    for row in pos_rows:
        if dedup(row["query"]):
            positives.append({"query": row["query"], "should_trigger": True})

    ambiguous = []
    for row in amb_rows:
        if dedup(row["query"]):
            ambiguous.append({
                "query": row["query"],
                "confidence": row["confidence"],
                "dispatched_to": skill_name,
            })

    negatives = []
    skills_seen = {}
    for row in neg_rows:
        dispatched = row["dispatched_to"]
        if skills_seen.get(dispatched, 0) >= max_negatives_per_skill:
            continue
        if dedup(row["query"]):
            negatives.append({"query": row["query"], "should_trigger": False})
            skills_seen[dispatched] = skills_seen.get(dispatched, 0) + 1

    return {
        "positives": positives,
        "negatives": negatives,
        "ambiguous": ambiguous,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Harvest usage data for a skill")
    parser.add_argument("--db", required=True, help="Path to .usage.db")
    parser.add_argument("--skill", required=True, help="Skill name")
    parser.add_argument("--pos-threshold", type=float, default=0.7)
    parser.add_argument("--neg-threshold", type=float, default=0.7)
    args = parser.parse_args()

    result = harvest_usage(
        db_path=Path(args.db),
        skill_name=args.skill,
        confidence_threshold_pos=args.pos_threshold,
        confidence_threshold_neg=args.neg_threshold,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
