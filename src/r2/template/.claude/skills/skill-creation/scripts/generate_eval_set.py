#!/usr/bin/env python3
"""Build balanced eval sets from usage data and optional synthetic generation.

Merges real queries from usage DB with existing eval sets and generates
synthetic queries via Claude when real data is sparse.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from scripts.harvest_usage import harvest_usage
from scripts.utils import parse_skill_md


def _generate_synthetic(
    skill_name: str,
    skill_description: str,
    existing_queries: list[str],
    count_positive: int,
    count_negative: int,
    model: str,
    project_root: Path,
) -> list[dict]:
    """Generate synthetic eval queries via Claude."""
    existing_str = "\n".join(f"  - {q}" for q in existing_queries[:10]) or "  (none)"

    prompt = f"""Generate exactly {count_positive} queries that SHOULD trigger the "{skill_name}" skill and {count_negative} queries that should NOT trigger it.

Skill description: {skill_description}

Existing queries (do not duplicate):
{existing_str}

Output ONLY valid JSON — an array of objects with "query" (string) and "should_trigger" (boolean). No commentary.

Example format:
[
  {{"query": "example positive query", "should_trigger": true}},
  {{"query": "example negative query", "should_trigger": false}}
]"""

    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", model, "--output-format", "text"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(project_root),
            env=env,
        )
        # Extract JSON from response (handle markdown code blocks)
        text = result.stdout.strip()
        if "```" in text:
            # Extract content between code fences
            parts = text.split("```")
            for part in parts[1:]:
                lines = part.strip().split("\n")
                if lines[0].lower() in ("json", ""):
                    lines = lines[1:]
                candidate = "\n".join(lines)
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue
        return json.loads(text)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
        print(f"Warning: synthetic generation failed: {e}", file=sys.stderr)
        return []


def generate_eval_set(
    skill_path: Path,
    db_path: Path,
    max_total: int = 20,
    target_balance: float = 0.5,
    synthetic_model: str | None = None,
    project_root: Path | None = None,
) -> list[dict]:
    """Build a balanced eval set from usage data + existing + synthetic.

    Returns the eval set as a list of {"query": ..., "should_trigger": ...} dicts.
    Also writes the result to skill_path/eval_set.json.
    """
    name, description, _ = parse_skill_md(skill_path)

    # Load existing eval set
    eval_file = skill_path / "eval_set.json"
    existing = json.loads(eval_file.read_text()) if eval_file.exists() else []
    existing_queries = {e["query"].lower().strip() for e in existing}

    # Harvest real usage
    harvested = {"positives": [], "negatives": [], "ambiguous": []}
    if db_path.exists():
        harvested = harvest_usage(
            db_path=db_path,
            skill_name=name,
            exclude_queries=existing_queries,
        )

    # Merge: existing + harvested positives + harvested negatives
    merged = list(existing)
    seen = set(existing_queries)

    for entry in harvested["positives"] + harvested["negatives"]:
        key = entry["query"].lower().strip()
        if key not in seen:
            seen.add(key)
            merged.append({"query": entry["query"], "should_trigger": entry["should_trigger"]})

    # Check balance
    pos_count = sum(1 for e in merged if e["should_trigger"])
    neg_count = len(merged) - pos_count
    total = len(merged)

    # Generate synthetic if needed
    if synthetic_model and total < max_total:
        target_pos = int(max_total * target_balance)
        target_neg = max_total - target_pos
        need_pos = max(0, target_pos - pos_count)
        need_neg = max(0, target_neg - neg_count)

        if need_pos + need_neg > 0:
            root = project_root or _find_project_root()
            synthetic = _generate_synthetic(
                skill_name=name,
                skill_description=description,
                existing_queries=[e["query"] for e in merged],
                count_positive=need_pos,
                count_negative=need_neg,
                model=synthetic_model,
                project_root=root,
            )
            for entry in synthetic:
                key = entry.get("query", "").lower().strip()
                if key and key not in seen:
                    seen.add(key)
                    merged.append({
                        "query": entry["query"],
                        "should_trigger": entry["should_trigger"],
                    })

    # Trim to max
    merged = merged[:max_total]

    # Write
    eval_file.write_text(json.dumps(merged, indent=2) + "\n")
    return merged


def _find_project_root() -> Path:
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate eval set for a skill")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--db", required=True, help="Path to .usage.db")
    parser.add_argument("--max-total", type=int, default=20)
    parser.add_argument("--synthetic-model", default=None, help="Model for synthetic generation")
    args = parser.parse_args()

    result = generate_eval_set(
        skill_path=Path(args.skill_path),
        db_path=Path(args.db),
        max_total=args.max_total,
        synthetic_model=args.synthetic_model,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
