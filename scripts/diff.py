#!/usr/bin/env python3
"""
diff.py — Side-by-side fact-sheet comparison for two quantization methods.

Usage:
    python scripts/diff.py gptq awq
    python scripts/diff.py gptq awq --markdown
    python scripts/diff.py --list          # show all available ids
"""

import argparse
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent.parent

COMPARE_FIELDS = [
    ("Category", "category"),
    ("Year", "year"),
    ("Precision", "precision"),
    ("Granularity", "granularity"),
    ("Calibration", "calibration"),
    ("Symmetric?", "symmetric"),
    ("Outlier handling", "handles_outliers_via"),
    ("Hardware target", "hardware_target"),
    ("Training needed?", "requires_training"),
    ("Calibration data?", "requires_calibration_data"),
    ("Typical degradation", "typical_degradation"),
    ("Builds on", "builds_on"),
    ("Paper", "paper_url"),
    ("Venue", "venue"),
]

ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"


def load_methods():
    with open(ROOT / "methods.yml", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def get_method(methods, mid):
    for m in methods:
        if m.get("id") == mid:
            return m
    return None


def fmt_val(val):
    if val is None or val == "null":
        return "—"
    if isinstance(val, bool):
        return "yes" if val else "no"
    if isinstance(val, list):
        return ", ".join(str(v) for v in val) if val else "—"
    return str(val)


def terminal_diff(ma, mb):
    name_a = ma.get("name", ma["id"])
    name_b = mb.get("name", mb["id"])
    col_w = 36

    def pad(s, w):
        s = str(s)
        if len(s) > w:
            s = s[: w - 1] + "…"
        return s.ljust(w)

    print(f"\n{ANSI_BOLD}{pad('Field', 24)} {pad(name_a, col_w)} {pad(name_b, col_w)}{ANSI_RESET}")
    print("-" * (24 + col_w * 2 + 2))

    for label, key in COMPARE_FIELDS:
        va = fmt_val(ma.get(key))
        vb = fmt_val(mb.get(key))
        if va == vb:
            color = ""
        else:
            color = ANSI_YELLOW
        print(f"{color}{pad(label, 24)} {pad(va, col_w)} {pad(vb, col_w)}{ANSI_RESET}")

    print()

    # TL;DR side by side
    print(f"\n{ANSI_BOLD}TL;DR — {name_a}{ANSI_RESET}")
    print(ma.get("tldr", "").strip())
    print(f"\n{ANSI_BOLD}TL;DR — {name_b}{ANSI_RESET}")
    print(mb.get("tldr", "").strip())
    print()


def markdown_diff(ma, mb):
    name_a = ma.get("name", ma["id"])
    name_b = mb.get("name", mb["id"])

    lines = [
        f"## {name_a} vs. {name_b}\n",
        f"| Field | {name_a} | {name_b} | Same? |",
        f"|-------|{'—' * len(name_a)}|{'—' * len(name_b)}|-------|",
    ]

    for label, key in COMPARE_FIELDS:
        va = fmt_val(ma.get(key))
        vb = fmt_val(mb.get(key))
        same = "yes" if va == vb else "**diff**"
        lines.append(f"| {label} | {va} | {vb} | {same} |")

    lines.append("")
    lines.append(f"**{name_a} TL;DR:** {ma.get('tldr', '').strip()}")
    lines.append("")
    lines.append(f"**{name_b} TL;DR:** {mb.get('tldr', '').strip()}")

    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(
        description="Compare two quantization methods side-by-side."
    )
    parser.add_argument("method_a", nargs="?", help="First method id")
    parser.add_argument("method_b", nargs="?", help="Second method id")
    parser.add_argument(
        "--markdown", action="store_true", help="Output as markdown table"
    )
    parser.add_argument(
        "--list", action="store_true", help="List all available method ids"
    )
    args = parser.parse_args()

    methods = load_methods()

    if args.list:
        for m in sorted(methods, key=lambda x: x.get("id", "")):
            print(f"  {m.get('id','?'):30s} {m.get('name','')}")
        return

    if not args.method_a or not args.method_b:
        parser.print_help()
        sys.exit(1)

    ma = get_method(methods, args.method_a)
    mb = get_method(methods, args.method_b)

    if ma is None:
        print(f"ERROR: method '{args.method_a}' not found. Use --list to see all ids.")
        sys.exit(1)
    if mb is None:
        print(f"ERROR: method '{args.method_b}' not found. Use --list to see all ids.")
        sys.exit(1)

    if args.markdown:
        # On Windows, stdout may not support UTF-8; reconfigure if needed
        import sys
        import io
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass
        markdown_diff(ma, mb)
    else:
        terminal_diff(ma, mb)


if __name__ == "__main__":
    main()
