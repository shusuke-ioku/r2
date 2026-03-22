#!/usr/bin/env python3
"""Add missing references to Zotero by parsing citekeys or typst compile errors.

Usage:
    # Add specific citekeys
    python .claude/scripts/zotero_add.py bai1998Estimating hainmueller2012Entropy

    # Auto-detect missing keys from typst compile errors
    python .claude/scripts/zotero_add.py --from-compile

Requires ZOTERO_API_KEY and ZOTERO_LIBRARY_ID in .env (project root).
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv
from pyzotero import zotero

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

ZOTERO_API_KEY = os.getenv("ZOTERO_API_KEY")
ZOTERO_LIBRARY_ID = os.getenv("ZOTERO_LIBRARY_ID")
ZOTERO_LIBRARY_TYPE = "user"

CROSSREF_API = "https://api.crossref.org/works"
CROSSREF_MAILTO = os.getenv("CROSSREF_MAILTO", "")  # polite pool for better rate limits

TYPST_FILE = PROJECT_ROOT / "paper" / "paper.typ"


# ---------------------------------------------------------------------------
# Citekey parsing
# ---------------------------------------------------------------------------

def parse_citekey(citekey: str) -> dict:
    """Extract author, year, and title hint from a BBT-style citekey.

    Patterns handled:
        author2024TitleWord       → author="author", year=2024, hint="TitleWord"
        authorSecond2024Title     → author="authorSecond", year=2024, hint="Title"
    """
    m = re.match(r"^([a-zA-Z]+?)(\d{4})(.+)$", citekey)
    if not m:
        return {"author": "", "year": "", "hint": citekey}
    return {
        "author": m.group(1),
        "year": m.group(2),
        "hint": m.group(3),
    }


def hint_to_words(hint: str) -> str:
    """Split a camelCase hint into space-separated words for search."""
    words = re.sub(r"([a-z])([A-Z])", r"\1 \2", hint)
    # Also split on transitions like "NSDAPand" → keep as-is, good enough
    return words


# ---------------------------------------------------------------------------
# CrossRef search
# ---------------------------------------------------------------------------

def search_crossref(author: str, year: str, hint: str, rows: int = 5) -> list[dict]:
    """Query CrossRef for candidate works matching the parsed citekey."""
    params = {
        "query.author": author,
        "query.bibliographic": hint_to_words(hint),
        "rows": rows,
        "select": "DOI,title,author,type,container-title,published-print,published-online,volume,issue,page",
        "mailto": CROSSREF_MAILTO,
    }
    if year:
        params["filter"] = f"from-pub-date:{year},until-pub-date:{year}"

    resp = requests.get(CROSSREF_API, params=params, timeout=30)
    resp.raise_for_status()
    items = resp.json().get("message", {}).get("items", [])
    return items


def pick_best_match(items: list[dict], author: str, year: str) -> dict | None:
    """Return the best CrossRef result, or None if nothing plausible."""
    if not items:
        return None
    # Simple heuristic: first result is usually best (CrossRef ranks by relevance).
    # Optionally verify author surname appears in the result.
    for item in items:
        cr_authors = item.get("author", [])
        for a in cr_authors:
            family = a.get("family", "").lower()
            if author.lower() in family or family in author.lower():
                return item
    # Fallback: return the top result anyway
    return items[0]


# ---------------------------------------------------------------------------
# CrossRef → Zotero item conversion
# ---------------------------------------------------------------------------

# Map CrossRef type → Zotero item type
CROSSREF_TO_ZOTERO_TYPE = {
    "journal-article": "journalArticle",
    "book": "book",
    "book-chapter": "bookSection",
    "proceedings-article": "conferencePaper",
    "monograph": "book",
    "edited-book": "book",
    "report": "report",
    "dissertation": "thesis",
}


def crossref_to_zotero_item(cr: dict, zot: zotero.Zotero, citekey: str) -> dict:
    """Convert a CrossRef work record to a pyzotero item dict."""
    cr_type = cr.get("type", "journal-article")
    zot_type = CROSSREF_TO_ZOTERO_TYPE.get(cr_type, "journalArticle")
    template = zot.item_template(zot_type)

    # Title
    titles = cr.get("title", [])
    template["title"] = titles[0] if titles else ""

    # Authors
    creators = []
    for a in cr.get("author", []):
        creators.append({
            "creatorType": "author",
            "firstName": a.get("given", ""),
            "lastName": a.get("family", ""),
        })
    if creators:
        template["creators"] = creators

    # Date
    date_parts = (
        cr.get("published-print", {}).get("date-parts", [[]])
        or cr.get("published-online", {}).get("date-parts", [[]])
    )
    if date_parts and date_parts[0]:
        parts = date_parts[0]
        template["date"] = "-".join(str(p) for p in parts)

    # Journal / container
    containers = cr.get("container-title", [])
    if containers:
        if zot_type == "journalArticle":
            template["publicationTitle"] = containers[0]
        elif zot_type == "bookSection":
            template["bookTitle"] = containers[0]

    # Volume, issue, pages
    if cr.get("volume"):
        template["volume"] = cr["volume"]
    if cr.get("issue"):
        template["issue"] = cr["issue"]
    if cr.get("page"):
        template["pages"] = cr["page"]

    # DOI
    if cr.get("DOI"):
        template["DOI"] = cr["DOI"]
        template["url"] = f"https://doi.org/{cr['DOI']}"

    # Pin BBT citekey
    template["extra"] = f"Citation Key: {citekey}"

    return template


# ---------------------------------------------------------------------------
# Zotero operations
# ---------------------------------------------------------------------------

def get_zotero_client() -> zotero.Zotero:
    if not ZOTERO_API_KEY or not ZOTERO_LIBRARY_ID:
        print("ERROR: ZOTERO_API_KEY and ZOTERO_LIBRARY_ID must be set in .env",
              file=sys.stderr)
        sys.exit(1)
    return zotero.Zotero(ZOTERO_LIBRARY_ID, ZOTERO_LIBRARY_TYPE, ZOTERO_API_KEY)


def citekey_exists_in_zotero(zot: zotero.Zotero, citekey: str) -> bool:
    """Check if a citekey already exists in the Zotero library (via extra field)."""
    # Search by the citekey text in the 'everything' field
    results = zot.items(q=citekey, qmode="everything", limit=10)
    for item in results:
        extra = item.get("data", {}).get("extra", "")
        if f"Citation Key: {citekey}" in extra:
            return True
    return False


def add_to_zotero(zot: zotero.Zotero, item: dict, citekey: str) -> bool:
    """Create item in Zotero. Returns True on success."""
    try:
        resp = zot.create_items([item])
        if resp.get("successful"):
            print(f"  ✓ Added to Zotero: {citekey}")
            return True
        else:
            failed = resp.get("failed", {})
            print(f"  ✗ Failed to add {citekey}: {failed}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"  ✗ Error adding {citekey}: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Process a single citekey
# ---------------------------------------------------------------------------

def process_citekey(citekey: str, zot: zotero.Zotero) -> bool:
    """Resolve a citekey via CrossRef and add to Zotero. Returns True on success."""
    print(f"\n→ Processing: {citekey}")

    # Check if already in Zotero
    if citekey_exists_in_zotero(zot, citekey):
        print(f"  ⊘ Already in Zotero, skipping.")
        return True

    parsed = parse_citekey(citekey)
    print(f"  Parsed: author={parsed['author']}, year={parsed['year']}, "
          f"hint={parsed['hint']}")

    # Search CrossRef
    print(f"  Searching CrossRef...")
    try:
        results = search_crossref(parsed["author"], parsed["year"], parsed["hint"])
    except requests.RequestException as e:
        print(f"  ✗ CrossRef search failed: {e}", file=sys.stderr)
        return False

    best = pick_best_match(results, parsed["author"], parsed["year"])
    if not best:
        print(f"  ✗ No CrossRef match found for {citekey}", file=sys.stderr)
        return False

    # Show what we found
    title = best.get("title", ["(no title)"])[0]
    authors = ", ".join(
        a.get("family", "") for a in best.get("author", [])[:3]
    )
    doi = best.get("DOI", "no DOI")
    print(f"  Match: {authors} — {title} (DOI: {doi})")

    # Convert and add
    item = crossref_to_zotero_item(best, zot, citekey)
    return add_to_zotero(zot, item, citekey)


# ---------------------------------------------------------------------------
# --from-compile mode
# ---------------------------------------------------------------------------

def extract_missing_keys_from_compile() -> list[str]:
    """Run typst compile and extract missing bibliography keys from errors."""
    print(f"Running: typst compile {TYPST_FILE}")
    result = subprocess.run(
        ["typst", "compile", str(TYPST_FILE)],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    # Typst error format: "error: key `citekey` does not exist in the bibliography"
    stderr = result.stderr + result.stdout
    pattern = re.compile(r"key `([^`]+)` does not exist")
    keys = pattern.findall(stderr)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for k in keys:
        if k not in seen:
            seen.add(k)
            unique.append(k)
    return unique


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add missing references to Zotero via CrossRef lookup."
    )
    parser.add_argument(
        "citekeys",
        nargs="*",
        help="BBT-style citekeys to resolve (e.g., bai1998Estimating)",
    )
    parser.add_argument(
        "--from-compile",
        action="store_true",
        help="Run typst compile and auto-resolve all missing bibliography keys",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search CrossRef but don't add to Zotero",
    )
    args = parser.parse_args()

    if not args.citekeys and not args.from_compile:
        parser.print_help()
        sys.exit(1)

    # Collect citekeys
    keys = list(args.citekeys)
    if args.from_compile:
        missing = extract_missing_keys_from_compile()
        if missing:
            print(f"\nFound {len(missing)} missing key(s): {', '.join(missing)}")
            keys.extend(missing)
        else:
            print("\nNo missing bibliography keys found. Paper compiles cleanly!")
            if not keys:
                return

    if not keys:
        print("No citekeys to process.")
        return

    zot = get_zotero_client()

    success = 0
    failed = 0
    for key in keys:
        ok = process_citekey(key, zot) if not args.dry_run else _dry_run(key)
        if ok:
            success += 1
        else:
            failed += 1
        # Be polite to APIs
        time.sleep(0.5)

    print(f"\nDone: {success} added, {failed} failed out of {len(keys)} total.")


def _dry_run(citekey: str) -> bool:
    """Dry-run: search CrossRef only, don't add to Zotero."""
    print(f"\n→ [DRY RUN] Processing: {citekey}")
    parsed = parse_citekey(citekey)
    print(f"  Parsed: author={parsed['author']}, year={parsed['year']}, "
          f"hint={parsed['hint']}")
    try:
        results = search_crossref(parsed["author"], parsed["year"], parsed["hint"])
    except requests.RequestException as e:
        print(f"  ✗ CrossRef search failed: {e}", file=sys.stderr)
        return False

    best = pick_best_match(results, parsed["author"], parsed["year"])
    if not best:
        print(f"  ✗ No match found", file=sys.stderr)
        return False

    title = best.get("title", ["(no title)"])[0]
    authors = ", ".join(a.get("family", "") for a in best.get("author", [])[:3])
    doi = best.get("DOI", "no DOI")
    print(f"  Match: {authors} — {title} (DOI: {doi})")
    return True


if __name__ == "__main__":
    main()
