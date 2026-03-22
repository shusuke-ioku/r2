#!/usr/bin/env python3
"""Automatic skill improvement orchestrator.

Identifies underperforming skills and runs the improvement loop on them.
"""

import argparse
import json
import sqlite3
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

from scripts.generate_eval_set import generate_eval_set
from scripts.run_eval import find_project_root, run_eval
from scripts.run_loop import run_loop
from scripts.utils import parse_skill_md


STATE_FILE = ".improvement_state.json"


def _load_state(skills_dir: Path) -> dict:
    path = skills_dir / STATE_FILE
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_state(skills_dir: Path, state: dict):
    path = skills_dir / STATE_FILE
    path.write_text(json.dumps(state, indent=2) + "\n")


def _get_usage_stats(db_path: Path) -> dict[str, dict]:
    """Get per-skill usage statistics from the database."""
    if not db_path.exists():
        return {}

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT skill_name, COUNT(*) as count, "
            "AVG(confidence) as avg_conf, "
            "MIN(confidence) as min_conf, "
            "MAX(confidence) as max_conf, "
            "MAX(timestamp) as last_used "
            "FROM usage GROUP BY skill_name"
        ).fetchall()
    finally:
        conn.close()

    return {
        row["skill_name"]: {
            "count": row["count"],
            "avg_confidence": round(row["avg_conf"], 3),
            "min_confidence": round(row["min_conf"], 3),
            "max_confidence": round(row["max_conf"], 3),
            "last_used": row["last_used"],
        }
        for row in rows
    }


def _score_skill(
    name: str,
    usage: dict | None,
    state: dict,
    min_cooldown_days: int = 7,
) -> dict:
    """Score a skill for improvement priority. Higher = more urgent."""
    reasons = []
    score = 0

    last_improved = state.get(name, {}).get("last_improved")
    if last_improved:
        days_since = (datetime.now() - datetime.fromisoformat(last_improved)).days
        if days_since < min_cooldown_days:
            return {"score": -1, "reasons": ["recently improved"], "cooldown_remaining": min_cooldown_days - days_since}

    if usage is None:
        reasons.append("no usage data")
        score += 1
        return {"score": score, "reasons": reasons}

    # Low average confidence
    if usage["avg_confidence"] < 0.7:
        reasons.append(f"low avg confidence ({usage['avg_confidence']:.2f})")
        score += 3

    # High variance (spread between min and max)
    spread = usage["max_confidence"] - usage["min_confidence"]
    if spread > 0.4 and usage["count"] >= 3:
        reasons.append(f"high confidence variance (spread={spread:.2f})")
        score += 2

    # No eval set exists
    has_eval = state.get(name, {}).get("has_eval_set", False)
    if not has_eval:
        reasons.append("no eval set")
        score += 1

    # Enough new events since last improvement
    events_since = usage["count"] - state.get(name, {}).get("events_at_last_improve", 0)
    if events_since >= 10:
        reasons.append(f"{events_since} new events since last improvement")
        score += 2

    if not reasons:
        reasons.append("looks healthy")

    return {"score": score, "reasons": reasons, "usage": usage}


def report(skills_dir: Path, db_path: Path, min_cooldown_days: int = 7) -> list[dict]:
    """Generate a priority-ranked report of skills needing improvement."""
    state = _load_state(skills_dir)
    usage_stats = _get_usage_stats(db_path)

    results = []
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        name, description, _ = parse_skill_md(skill_dir)

        # Check if eval set exists
        if name not in state:
            state[name] = {}
        state[name]["has_eval_set"] = (skill_dir / "eval_set.json").exists()

        usage = usage_stats.get(name)
        scoring = _score_skill(name, usage, state, min_cooldown_days)

        results.append({
            "name": name,
            "description": description[:80] + "..." if len(description) > 80 else description,
            "score": scoring["score"],
            "reasons": scoring["reasons"],
            "usage": usage,
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def improve_skill(
    skill_path: Path,
    db_path: Path,
    model: str,
    max_iterations: int = 3,
    num_workers: int = 5,
    runs_per_query: int = 2,
    holdout: float = 0.4,
    verbose: bool = True,
) -> dict:
    """Run the improvement pipeline for a single skill.

    Returns the improvement result including best_description and scores.
    """
    name, original_description, _ = parse_skill_md(skill_path)
    project_root = find_project_root()

    if verbose:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Improving: {name}", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)

    # Step 1: Generate/refresh eval set
    if verbose:
        print("Generating eval set...", file=sys.stderr)
    eval_set = generate_eval_set(
        skill_path=skill_path,
        db_path=db_path,
        max_total=20,
        synthetic_model=model,
        project_root=project_root,
    )
    if verbose:
        pos = sum(1 for e in eval_set if e["should_trigger"])
        neg = len(eval_set) - pos
        print(f"Eval set: {len(eval_set)} queries ({pos} positive, {neg} negative)", file=sys.stderr)

    if len(eval_set) < 4:
        return {
            "skill": name,
            "status": "skipped",
            "reason": f"eval set too small ({len(eval_set)} queries)",
        }

    # Step 2: Run improvement loop
    if verbose:
        print("Running improvement loop...", file=sys.stderr)

    result = run_loop(
        eval_set=eval_set,
        skill_path=skill_path,
        description_override=None,
        num_workers=num_workers,
        timeout=30,
        max_iterations=max_iterations,
        runs_per_query=runs_per_query,
        trigger_threshold=0.5,
        holdout=holdout,
        model=model,
        verbose=verbose,
    )

    return {
        "skill": name,
        "status": "completed",
        "original_description": original_description,
        "best_description": result["best_description"],
        "best_score": result["best_score"],
        "best_train_score": result["best_train_score"],
        "best_test_score": result.get("best_test_score"),
        "iterations_run": result["iterations_run"],
        "description_changed": result["best_description"] != original_description,
    }


def apply_description(skill_path: Path, new_description: str) -> bool:
    """Write an improved description back to SKILL.md."""
    skill_md = skill_path / "SKILL.md"
    content = skill_md.read_text()
    lines = content.split("\n")

    # Find and replace description in frontmatter
    if lines[0].strip() != "---":
        return False

    end_idx = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return False

    # Rebuild frontmatter with new description
    new_lines = ["---"]
    i = 1
    description_written = False
    while i < end_idx:
        line = lines[i]
        if line.startswith("description:"):
            # Write new description in folded style
            new_lines.append("description: >")
            # Wrap description to ~78 chars per line, indented with 2 spaces
            words = new_description.split()
            current_line = " "
            for word in words:
                if len(current_line) + len(word) + 1 > 78:
                    new_lines.append(current_line)
                    current_line = "  " + word
                else:
                    current_line += " " + word if current_line.strip() else "  " + word
            if current_line.strip():
                new_lines.append(current_line)
            description_written = True
            # Skip old description continuation lines
            i += 1
            while i < end_idx and (lines[i].startswith("  ") or lines[i].startswith("\t")):
                i += 1
            continue
        else:
            new_lines.append(line)
        i += 1

    new_lines.append("---")
    # Add rest of file (body after frontmatter)
    new_lines.extend(lines[end_idx + 1:])

    if description_written:
        # Save backup
        history_file = skill_path / "description_history.json"
        history = json.loads(history_file.read_text()) if history_file.exists() else []
        name, old_desc, _ = parse_skill_md(skill_path)
        history.append({
            "description": old_desc,
            "replaced_at": datetime.now().isoformat(),
        })
        history_file.write_text(json.dumps(history, indent=2) + "\n")

        # Write updated SKILL.md
        skill_md.write_text("\n".join(new_lines))
        return True

    return False


def auto_improve(
    skills_dir: Path,
    db_path: Path,
    model: str,
    dry_run: bool = True,
    force_skills: list[str] | None = None,
    max_skills: int = 3,
    max_iterations: int = 3,
    num_workers: int = 5,
    apply: bool = False,
    verbose: bool = True,
) -> dict:
    """Main orchestrator: identify and improve underperforming skills."""
    state = _load_state(skills_dir)

    # Get priority report
    priorities = report(skills_dir, db_path)

    if force_skills:
        candidates = [p for p in priorities if p["name"] in force_skills]
    else:
        candidates = [p for p in priorities if p["score"] > 0]

    candidates = candidates[:max_skills]

    if dry_run:
        return {
            "mode": "dry_run",
            "candidates": candidates,
            "all_skills": priorities,
        }

    # Run improvement on candidates
    results = []
    for candidate in candidates:
        skill_path = skills_dir / candidate["name"]
        if not (skill_path / "SKILL.md").exists():
            continue

        result = improve_skill(
            skill_path=skill_path,
            db_path=db_path,
            model=model,
            max_iterations=max_iterations,
            num_workers=num_workers,
            verbose=verbose,
        )
        results.append(result)

        # Update state
        usage_stats = _get_usage_stats(db_path)
        usage = usage_stats.get(candidate["name"], {})
        state[candidate["name"]] = {
            "last_improved": datetime.now().isoformat(),
            "events_at_last_improve": usage.get("count", 0),
            "has_eval_set": True,
            "last_score": result.get("best_score"),
        }

        # Apply if requested and description improved
        if apply and result.get("description_changed"):
            applied = apply_description(skill_path, result["best_description"])
            result["applied"] = applied
            if verbose and applied:
                print(f"Applied new description for {candidate['name']}", file=sys.stderr)

    _save_state(skills_dir, state)

    return {
        "mode": "improve",
        "applied": apply,
        "results": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Auto-improve skill descriptions")
    parser.add_argument("--skills-dir", required=True, help="Path to skills directory")
    parser.add_argument("--db", required=True, help="Path to .usage.db")
    parser.add_argument("--model", default="sonnet", help="Model for improvement")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Report only (default)")
    parser.add_argument("--run", action="store_true", help="Actually run improvements")
    parser.add_argument("--apply", action="store_true", help="Apply improved descriptions to SKILL.md")
    parser.add_argument("--force", nargs="+", help="Force improvement on specific skills")
    parser.add_argument("--max-skills", type=int, default=3)
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    result = auto_improve(
        skills_dir=Path(args.skills_dir),
        db_path=Path(args.db),
        model=args.model,
        dry_run=not args.run,
        force_skills=args.force,
        max_skills=args.max_skills,
        max_iterations=args.max_iterations,
        apply=args.apply,
        verbose=args.verbose,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
