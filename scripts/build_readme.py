#!/usr/bin/env python3
"""
build_readme.py — Generates README.md and docs/timeline.md from methods.yml.

DO NOT hand-edit README.md or docs/timeline.md. Run this script instead.

Usage:
    python scripts/build_readme.py
"""

import sys
from pathlib import Path
from datetime import date

import yaml

ROOT = Path(__file__).parent.parent

CATEGORY_META = {
    "ptq_weight_only": {
        "title": "Post-Training Quantization — Weight-Only",
        "abbr": "PTQ W-only",
        "color": "#4A90D9",
        "description": (
            "These methods quantize only the weight tensors; activations remain in FP16/BF16. "
            "This avoids the challenge of activation outliers and is sufficient for memory-bound "
            "inference (most single-GPU LLM serving). The dominant category for open-weight model releases."
        ),
    },
    "ptq_weight_activation": {
        "title": "Post-Training Quantization — Weights + Activations",
        "abbr": "PTQ W+A",
        "color": "#E87D3E",
        "description": (
            "Quantizing both weights and activations enables integer matrix multiplication "
            "(W8A8 or W4A8), which is compute-bound-friendly and achieves higher throughput "
            "than W-only on GPU. The challenge is handling activation outliers without "
            "sacrificing accuracy."
        ),
    },
    "qat": {
        "title": "Quantization-Aware Training & Quantized Fine-Tuning",
        "abbr": "QAT / QFT",
        "color": "#7B68EE",
        "description": (
            "Methods that involve gradient updates: either training from scratch with simulated "
            "quantization, or fine-tuning a pre-trained model (often with LoRA adapters) while "
            "the base weights are kept quantized. Generally achieves better quality at the same "
            "bit-width than PTQ, at the cost of training compute."
        ),
    },
    "extreme_lowbit": {
        "title": "Extreme Low-Bit & Binary/Ternary Quantization",
        "abbr": "Sub-2-bit",
        "color": "#E84393",
        "description": (
            "Methods targeting 1–2 bits per weight, including binary {-1, +1}, "
            "ternary {-1, 0, +1}, and sub-2-bit codebook approaches. At these bit-widths "
            "quantization error is substantial and most methods require QAT or architectural "
            "changes. The frontier of model compression research."
        ),
    },
    "kv_cache": {
        "title": "KV-Cache Quantization",
        "abbr": "KV Quant",
        "color": "#3DAD78",
        "description": (
            "The attention KV cache grows linearly with context length and becomes the dominant "
            "memory consumer at long contexts. Quantizing K and V tensors to 4 or fewer bits "
            "reduces memory pressure, increases effective batch size, and enables longer "
            "contexts — at the cost of a small attention quality penalty."
        ),
    },
    "low_precision_training": {
        "title": "Low-Precision Training & Numerical Formats",
        "abbr": "LP Training",
        "color": "#D4A027",
        "description": (
            "Hardware-oriented floating-point formats and training recipes for using them. "
            "FP8 and MX (Microscaling) formats are now standard in H100/Blackwell training. "
            "This category is adjacent to inference quantization — the formats overlap, "
            "but the use case is accelerating training rather than compressing inference."
        ),
    },
    "moe": {
        "title": "MoE-Specific Quantization",
        "abbr": "MoE Quant",
        "color": "#9B59B6",
        "description": (
            "Mixture-of-Experts models (Mixtral, DeepSeek-MoE, etc.) pose unique quantization "
            "challenges: the total parameter count is large (many experts), but only a few "
            "experts activate per token, so expert weights are rarely observed in calibration. "
            "Methods in this category exploit MoE structure for better compression."
        ),
    },
    "systems": {
        "title": "Systems, Kernels & Runtimes",
        "abbr": "Systems",
        "color": "#607D8B",
        "description": (
            "Software that implements quantization methods in practice: inference engines, "
            "CUDA kernels, quantization toolkits. These are not novel algorithms but are the "
            "infrastructure through which the algorithms ship. One card per runtime, listing "
            "which methods it supports."
        ),
    },
}

CATEGORY_ORDER = [
    "ptq_weight_only",
    "ptq_weight_activation",
    "qat",
    "extreme_lowbit",
    "kv_cache",
    "low_precision_training",
    "moe",
    "systems",
]


def load_methods():
    with open(ROOT / "methods.yml", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def sort_methods(methods):
    """Sort by date descending within each category (newest first)."""
    def sort_key(m):
        d = m.get("date", "0000-00-00")
        if d is None or d == "unknown":
            d = "0000-00-00"
        return str(d)

    by_cat = {cat: [] for cat in CATEGORY_ORDER}
    for m in methods:
        cat = m.get("category", "unknown")
        if cat in by_cat:
            by_cat[cat].append(m)
    for cat in by_cat:
        by_cat[cat].sort(key=sort_key, reverse=True)
    return by_cat


def method_anchor(method_id):
    return method_id.lower().replace("_", "-").replace(".", "")


def render_card(m):
    """Render a single method card as Markdown."""
    parts = []

    name = m.get("name", m["id"])
    precision = m.get("precision", "unknown")
    cat_abbr = CATEGORY_META.get(m.get("category", ""), {}).get("abbr", m.get("category", ""))
    date_str = str(m.get("date", "unknown"))[:7]  # YYYY-MM
    anchor = method_anchor(m["id"])

    parts.append(f'### {name} · {precision} · {cat_abbr} · {date_str} {{#{anchor}}}')
    parts.append("")

    # Diagram
    diag = m.get("diagram")
    cap = m.get("diagram_caption", "")
    if diag:
        parts.append(f'<img src="{diag}" width="640" alt="{name} diagram">')
        if cap:
            parts.append(f"<p><em>{cap}</em></p>")
        parts.append("")

    # TL;DR
    tldr = m.get("tldr", "").strip()
    if tldr:
        parts.append(f"> {tldr}")
        parts.append("")

    # Fact table
    paper_url = m.get("paper_url")
    code_url = m.get("code_url")
    blog_url = m.get("blog_url")
    venue = m.get("venue") or ""

    paper_cell = ""
    if paper_url and paper_url not in ("null", None):
        paper_cell = f"[{paper_url.split('/')[-1]}]({paper_url})"
        if venue:
            paper_cell += f" · {venue}"
    elif venue:
        paper_cell = venue

    code_cell = ""
    if code_url and code_url not in ("null", None):
        # Extract repo name from URL
        parts_url = code_url.rstrip("/").split("/")
        repo = "/".join(parts_url[-2:]) if len(parts_url) >= 2 else code_url
        code_cell = f"[{repo}]({code_url})"

    blog_cell = ""
    if blog_url and blog_url not in ("null", None):
        blog_cell = f"[link]({blog_url})"

    # Cross-refs
    def render_refs(ids):
        if not ids:
            return "—"
        return " · ".join(f"[{r}](#{method_anchor(r)})" for r in ids)

    rows = [
        ("Paper", paper_cell or "—"),
        ("Code", code_cell or "—"),
        ("Blog / post", blog_cell or "—"),
        ("Precision", m.get("precision", "unknown")),
        ("Granularity", m.get("granularity", "unknown")),
        ("Calibration", m.get("calibration", "unknown")),
        ("Symmetric?", str(m.get("symmetric", "unknown"))),
        ("Outlier handling", m.get("handles_outliers_via", "unknown")),
        ("Hardware target", m.get("hardware_target", "unknown")),
        ("Training needed?", "yes" if m.get("requires_training") else "no"),
        ("Calibration data?", "yes" if m.get("requires_calibration_data") else "no"),
        ("Typical degradation", m.get("typical_degradation", "unknown")),
        ("Builds on", render_refs(m.get("builds_on") or [])),
        ("Superseded by", render_refs(m.get("superseded_by") or [])),
        ("Related", render_refs(m.get("related") or [])),
    ]

    parts.append("| Field | Value |")
    parts.append("|-------|-------|")
    for label, val in rows:
        if val and val != "—":
            parts.append(f"| {label} | {val} |")
    parts.append("")

    # Key idea
    key_idea = m.get("key_idea", "").strip()
    if key_idea:
        parts.append("**How it works:**")
        parts.append("")
        parts.append(key_idea)
        parts.append("")

    return "\n".join(parts)


def render_matrix(methods):
    """Big comparison matrix — all methods as rows."""
    rows = sorted(methods, key=lambda m: m.get("id", ""))

    lines = []
    lines.append("## Full Method Matrix\n")
    lines.append(
        "Every method in one table. Sort by any column. "
        "Linked IDs jump to the full card.\n"
    )
    lines.append(
        "| ID | Category | Year | W-bits | A-bits | KV-bits | Calibration? | Training? | Paper |"
    )
    lines.append(
        "|----|----------|------|--------|--------|---------|-------------|-----------|-------|"
    )

    for m in rows:
        mid = m.get("id", "")
        anchor = method_anchor(mid)
        cat = CATEGORY_META.get(m.get("category", ""), {}).get("abbr", m.get("category", ""))
        year = m.get("year", "?")
        precision = m.get("precision", "?")

        # Parse precision string into W/A/KV columns
        w_bits = a_bits = kv_bits = "—"
        if precision and precision != "unknown":
            p = precision.upper()
            import re
            wm = re.search(r"W(\S+?)(?:\s|$|A|KV)", p)
            am = re.search(r"A(\d+)", p)
            kvm = re.search(r"KV(\d+)", p)
            if wm:
                w_bits = wm.group(1)
            if am:
                a_bits = am.group(1)
            if kvm:
                kv_bits = kvm.group(1)

        calib = "yes" if m.get("requires_calibration_data") else "no"
        train = "yes" if m.get("requires_training") else "no"

        paper_url = m.get("paper_url")
        if paper_url and paper_url not in ("null", None):
            paper_cell = f"[paper]({paper_url})"
        else:
            paper_cell = "—"

        lines.append(
            f"| [{mid}](#{anchor}) | {cat} | {year} | {w_bits} | {a_bits} | {kv_bits} "
            f"| {calib} | {train} | {paper_cell} |"
        )

    return "\n".join(lines)


def render_mermaid_lineage(methods):
    """Render a Mermaid graph of the builds_on relationship."""
    lines = []
    lines.append("## Lineage Graph\n")
    lines.append(
        "Arrows point from a method to the one(s) it builds on "
        "(i.e., A → B means A builds on B).\n"
    )
    lines.append("```mermaid")
    lines.append("graph LR")

    # Only include methods that have builds_on or are referenced
    has_edges = False
    for m in methods:
        mid = m.get("id", "")
        for dep in (m.get("builds_on") or []):
            dep_name = next((x.get("name", dep) for x in methods if x.get("id") == dep), dep)
            src_name = m.get("name", mid)
            lines.append(f'    {mid}["{src_name}"] --> {dep}["{dep_name}"]')
            has_edges = True

    if not has_edges:
        lines.append("    %% No lineage edges yet")

    lines.append("```")
    return "\n".join(lines)


def render_toc(by_cat, methods):
    """Table of contents."""
    lines = ["## Table of Contents\n"]
    for cat in CATEGORY_ORDER:
        meta = CATEGORY_META.get(cat, {})
        title = meta.get("title", cat)
        count = len(by_cat.get(cat, []))
        slug = title.lower().replace(" ", "-").replace("—", "").replace("/", "").replace("&", "").replace(",", "").strip("-")
        lines.append(f"- [{title}](#{slug}) — {count} method{'s' if count != 1 else ''}")
    lines.append(f"- [Full Method Matrix](#full-method-matrix) — {len(methods)} total")
    lines.append("- [Lineage Graph](#lineage-graph)")
    lines.append("")
    return "\n".join(lines)


def render_timeline(methods):
    """Chronological timeline for docs/timeline.md."""
    sorted_methods = sorted(
        methods,
        key=lambda m: (str(m.get("date", "0000-00-00")).replace("unknown", "0000-00-00"), m.get("id", "")),
    )

    lines = [
        "# Chronological Timeline\n",
        "> Auto-generated by `scripts/build_readme.py`. Do not edit directly.\n",
        "| Date | Method | Category | Precision | Paper |",
        "|------|--------|----------|-----------|-------|",
    ]

    for m in sorted_methods:
        d = str(m.get("date", "unknown") or "unknown")
        name = m.get("name", m.get("id", ""))
        cat = CATEGORY_META.get(m.get("category", ""), {}).get("abbr", m.get("category", ""))
        prec = m.get("precision", "—")
        paper_url = m.get("paper_url")
        if paper_url and paper_url not in ("null", None):
            paper_cell = f"[paper]({paper_url})"
        else:
            paper_cell = "—"
        lines.append(f"| {d} | {name} | {cat} | {prec} | {paper_cell} |")

    return "\n".join(lines)


def main():
    methods = load_methods()
    by_cat = sort_methods(methods)

    readme_parts = []

    # Header
    readme_parts.append("# LLM Quantization Gallery\n")
    readme_parts.append(
        "> **Auto-generated** from [`methods.yml`](methods.yml) by "
        "[`scripts/build_readme.py`](scripts/build_readme.py). "
        "**Do not edit this file directly.** To add or update an entry, "
        "edit `methods.yml` and run `python scripts/build_readme.py`.\n"
    )
    readme_parts.append(
        "A curated, visual, side-by-side reference for LLM quantization methods — "
        "every major algorithm, organized by category, with consistent fact sheets, "
        "architecture diagrams, and cross-references. "
        "Modeled after Sebastian Raschka's "
        "[llm-architecture-gallery](https://github.com/rasbt/llm-architecture-gallery).\n"
    )
    readme_parts.append(
        "Before reading the cards, see **[docs/notation.md](docs/notation.md)** for the "
        "`W4A16`, `W8A8KV4`, group-size, and per-channel notation used everywhere. "
        "See **[docs/glossary.md](docs/glossary.md)** for term definitions.\n"
    )

    # TOC
    readme_parts.append(render_toc(by_cat, methods))

    # Matrix table
    readme_parts.append(render_matrix(methods))
    readme_parts.append("")

    # Category sections
    for cat in CATEGORY_ORDER:
        meta = CATEGORY_META.get(cat, {})
        title = meta.get("title", cat)
        desc = meta.get("description", "")
        cat_methods = by_cat.get(cat, [])

        readme_parts.append(f"---\n\n## {title}\n")
        if desc:
            readme_parts.append(f"{desc}\n")

        if not cat_methods:
            readme_parts.append("*No entries yet in this category.*\n")
        else:
            for m in cat_methods:
                readme_parts.append(render_card(m))
                readme_parts.append("---\n")

    # Lineage graph
    readme_parts.append(render_mermaid_lineage(methods))

    # Footer
    readme_parts.append("\n---")
    today = date.today().isoformat()
    readme_parts.append(
        f"\n*Generated {today} from {len(methods)} entries across "
        f"{sum(1 for c in CATEGORY_ORDER if by_cat.get(c))} categories.*"
    )

    readme_text = "\n".join(readme_parts)

    (ROOT / "README.md").write_text(readme_text, encoding="utf-8")
    print(f"Wrote README.md ({len(readme_text):,} chars, {len(methods)} methods)")

    # Timeline
    timeline_text = render_timeline(methods)
    (ROOT / "docs" / "timeline.md").write_text(timeline_text, encoding="utf-8")
    print(f"Wrote docs/timeline.md")


if __name__ == "__main__":
    main()
