#!/usr/bin/env python3
"""
validate.py — Schema-checks methods.yml.

Checks:
  - All required fields present on every entry
  - No duplicate ids
  - builds_on / superseded_by / related reference existing ids
  - URLs are syntactically valid (and optionally HTTP-reachable)
  - diagram paths exist on disk
  - date format is YYYY-MM-DD
  - year is an integer

Usage:
    python scripts/validate.py                  # fast, no network
    python scripts/validate.py --check-urls     # also HEAD-requests every URL (slow)
"""

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent

REQUIRED_FIELDS = [
    "id", "name", "full_name", "category", "subcategory",
    "year", "date", "authors", "affiliation",
    "paper_url", "code_url", "blog_url", "venue",
    "precision", "granularity", "calibration", "symmetric",
    "handles_outliers_via", "hardware_target",
    "requires_training", "requires_calibration_data",
    "typical_degradation",
    "tldr", "key_idea",
    "builds_on", "superseded_by", "related",
    "diagram", "diagram_caption",
]

VALID_CATEGORIES = {
    "ptq_weight_only",
    "ptq_weight_activation",
    "qat",
    "extreme_lowbit",
    "kv_cache",
    "low_precision_training",
    "moe",
    "systems",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://")


def load_methods():
    yml_path = ROOT / "methods.yml"
    with open(yml_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        print("FAIL: methods.yml must be a YAML list at the top level.")
        sys.exit(1)
    return data


def validate_fields(entry, errors):
    eid = entry.get("id", "<NO ID>")
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"[{eid}] Missing required field: '{field}'")


def validate_category(entry, errors):
    eid = entry.get("id", "<NO ID>")
    cat = entry.get("category")
    if cat and cat not in VALID_CATEGORIES:
        errors.append(
            f"[{eid}] Unknown category '{cat}'. "
            f"Valid: {sorted(VALID_CATEGORIES)}"
        )


def validate_date(entry, errors):
    eid = entry.get("id", "<NO ID>")
    date = entry.get("date")
    if date and date != "unknown" and not DATE_RE.match(str(date)):
        errors.append(f"[{eid}] 'date' must be YYYY-MM-DD or 'unknown', got: {date!r}")


def validate_year(entry, errors):
    eid = entry.get("id", "<NO ID>")
    year = entry.get("year")
    if year and year != "unknown":
        try:
            int(year)
        except (TypeError, ValueError):
            errors.append(f"[{eid}] 'year' must be an integer or 'unknown', got: {year!r}")


def validate_urls(entry, errors):
    eid = entry.get("id", "<NO ID>")
    for field in ("paper_url", "code_url", "blog_url"):
        val = entry.get(field)
        if val and val != "null" and val is not None:
            if not URL_RE.match(str(val)):
                errors.append(f"[{eid}] '{field}' is not a valid URL: {val!r}")


def validate_diagram(entry, errors):
    eid = entry.get("id", "<NO ID>")
    diag = entry.get("diagram")
    if diag and diag != "unknown":
        path = ROOT / diag
        if not path.exists():
            errors.append(f"[{eid}] diagram file not found: {diag}")


def validate_cross_refs(entries, errors):
    all_ids = {e["id"] for e in entries if "id" in e}
    for entry in entries:
        eid = entry.get("id", "<NO ID>")
        for field in ("builds_on", "superseded_by", "related"):
            refs = entry.get(field, []) or []
            for ref in refs:
                if ref not in all_ids:
                    errors.append(
                        f"[{eid}] '{field}' references unknown id: '{ref}'"
                    )


def validate_unique_ids(entries, errors):
    seen = {}
    for entry in entries:
        eid = entry.get("id")
        if eid is None:
            continue
        if eid in seen:
            errors.append(f"Duplicate id: '{eid}' (first seen at index {seen[eid]})")
        else:
            seen[eid] = entries.index(entry)


def check_urls_live(entries, errors):
    import urllib.request
    import urllib.error

    print("Checking URLs (this may take a while)...")
    for entry in entries:
        eid = entry.get("id", "<NO ID>")
        for field in ("paper_url", "code_url", "blog_url"):
            url = entry.get(field)
            if not url or url == "null" or url is None:
                continue
            try:
                req = urllib.request.Request(url, method="HEAD")
                req.add_header("User-Agent", "Mozilla/5.0 (quantization-gallery-validator)")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    code = resp.status
                    if code >= 400:
                        errors.append(f"[{eid}] {field} returned HTTP {code}: {url}")
            except urllib.error.HTTPError as e:
                if e.code == 405:
                    pass  # HEAD not allowed, that's fine
                elif e.code >= 400:
                    errors.append(f"[{eid}] {field} HTTP {e.code}: {url}")
            except Exception as exc:
                errors.append(f"[{eid}] {field} unreachable ({exc}): {url}")


def main():
    parser = argparse.ArgumentParser(description="Validate methods.yml")
    parser.add_argument(
        "--check-urls",
        action="store_true",
        help="HEAD-request every URL (slow; requires network)",
    )
    args = parser.parse_args()

    entries = load_methods()
    errors = []
    warnings = []

    validate_unique_ids(entries, errors)
    validate_cross_refs(entries, errors)

    for entry in entries:
        validate_fields(entry, errors)
        validate_category(entry, errors)
        validate_date(entry, errors)
        validate_year(entry, errors)
        validate_urls(entry, errors)
        validate_diagram(entry, errors)

    if args.check_urls:
        check_urls_live(entries, errors)

    # Summary
    print(f"Loaded {len(entries)} entries.")
    cats = {}
    for e in entries:
        c = e.get("category", "unknown")
        cats[c] = cats.get(c, 0) + 1
    for cat, count in sorted(cats.items()):
        print(f"  {cat}: {count} methods")
    print()

    if errors:
        print(f"FAILED — {len(errors)} error(s):")
        for err in errors:
            print(f"  ERROR: {err}")
        sys.exit(1)
    else:
        print("OK — all checks passed.")


if __name__ == "__main__":
    main()
