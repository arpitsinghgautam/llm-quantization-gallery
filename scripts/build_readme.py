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

MERMAID_DIR = ROOT / "assets" / "mermaid"


def load_mermaid(method_id):
    """Read assets/mermaid/{id}.mmd and return as a mermaid fenced block, or None."""
    path = MERMAID_DIR / f"{method_id}.mmd"
    if path.exists():
        body = path.read_text(encoding="utf-8").strip()
        return "```mermaid\n" + body + "\n```"
    return None


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


def render_card(m, path_prefix=""):
    """Render a single method card as Markdown.

    path_prefix: prepended to relative asset paths (e.g. "../" for docs/methods.md).
    """
    parts = []

    name = m.get("name", m["id"])
    precision = m.get("precision", "unknown")
    cat_abbr = CATEGORY_META.get(m.get("category", ""), {}).get("abbr", m.get("category", ""))
    date_str = str(m.get("date", "unknown"))[:7]  # YYYY-MM
    anchor = method_anchor(m["id"])

    parts.append(f'<a id="{anchor}"></a>')
    parts.append(f'### {name} · {precision} · {cat_abbr} · {date_str}')
    parts.append("")

    # Diagram
    diag = m.get("diagram")
    cap = m.get("diagram_caption", "")
    if diag:
        src = path_prefix + diag if diag and not diag.startswith("http") else diag
        parts.append(f'<img src="{src}" width="640" alt="{name} diagram">')
        if cap:
            parts.append(f"<p><em>{cap}</em></p>")
        parts.append("")

    # Mermaid flowchart (for methods that have one)
    mermaid_block = load_mermaid(m["id"])
    if mermaid_block:
        parts.append(mermaid_block)
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
        import re as _re
        w_bits = a_bits = kv_bits = "—"
        p = (precision or "").strip()
        p_up = p.upper()

        # n/a or pruning → leave all blank
        if p_up.startswith("N/A"):
            pass
        # sub-1-bit special case
        elif "SUB-1" in p_up or "~0.1" in p_up:
            w_bits = "<1"
        # KV-only formats (no W prefix)
        elif p_up.startswith("KV") and "W" not in p_up:
            kvm = _re.search(r"KV([\d.]+(?:-[\d.]+)?)", p_up)
            if kvm: kv_bits = kvm.group(1)
        # FP8 / MXFP / NVFP / low-precision training formats
        elif _re.search(r"(?:FP8|MXFP|NVFP|FP4)", p_up) and not _re.search(r"^W\d", p_up):
            nums = _re.findall(r"(?:MX|NV|E\d)?FP(\d+)", p_up)
            w_bits = "/".join(sorted(set(nums))) if nums else "FP"
            a_bits = w_bits
        else:
            # W bits: W followed by digits/decimals, ranges with / or –
            wm = _re.search(r"W([\d.]+(?:[/–\-][\dW.]+)*)", p_up)
            if wm:
                raw = wm.group(1).replace("W", "")
                w_bits = raw
            # A bits: digit-preceded A + digits, up to 32
            am = _re.search(r"(?<=[\d\s])A(\d+)", p_up)
            if am and int(am.group(1)) <= 32:
                a_bits = am.group(1)
            # KV bits
            kvm = _re.search(r"KV([\d.]+(?:-[\d.]+)?)", p_up)
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
    lines.append("- [Chronological Overview](#chronological-overview)")
    lines.append("")
    return "\n".join(lines)


def render_mermaid_timeline(methods):
    """Mermaid timeline diagram grouped by year."""
    from collections import defaultdict

    by_year = defaultdict(list)
    for m in methods:
        year = m.get("year")
        try:
            by_year[int(year)].append(m.get("name", m["id"]))
        except (TypeError, ValueError):
            pass

    lines = ["## Chronological Overview\n"]
    lines.append(
        "> Methods grouped by publication year. "
        "See [docs/timeline.md](docs/timeline.md) for the full sortable table.\n"
    )
    lines.append("```mermaid")
    lines.append("timeline")
    lines.append("    title LLM Quantization — Publication Timeline")
    for year in sorted(by_year.keys()):
        names = by_year[year]
        lines.append(f"    section {year}")
        for name in names:
            # Mermaid timeline: each entry is "    key : value" but we just use name
            safe_name = name.replace(":", " ").replace('"', "")
            lines.append(f"        {safe_name}")
    lines.append("```")
    return "\n".join(lines)


def render_chronological_section(methods):
    """Plain markdown table for README — methods published 2022–2025."""
    in_range = [m for m in methods if str(m.get("year", "0")) in ("2022", "2023", "2024", "2025")]
    sorted_methods = sorted(
        in_range,
        key=lambda m: (str(m.get("date") or m.get("year") or "0"), m.get("id", "")),
    )

    lines = ["## Chronological Overview\n"]
    lines.append(
        "Methods published 2022–2025, ordered by date. "
        "See [docs/timeline.md](docs/timeline.md) for the full table.\n"
    )
    lines.append("| Date | Method | Category | Precision |")
    lines.append("|------|--------|----------|-----------|")
    for m in sorted_methods:
        d = str(m.get("date") or m.get("year") or "?")
        if len(d) > 7:
            d = d[:7]
        mid = m.get("id", "")
        anchor = method_anchor(mid)
        name = m.get("name", mid)
        cat = CATEGORY_META.get(m.get("category", ""), {}).get("abbr", m.get("category", ""))
        prec = m.get("precision", "—")
        lines.append(f"| {d} | [{name}](#{anchor}) | {cat} | {prec} |")
    return "\n".join(lines)


def render_timeline(methods):
    """Chronological timeline for docs/timeline.md.

    Writes assets/mermaid/timeline-gantt.mmd (2022-present only) as a side-effect.
    The SVG pre-render is referenced from the doc instead of a mermaid fenced block.
    """
    sorted_methods = sorted(
        methods,
        key=lambda m: (str(m.get("date", "0000-00-00")).replace("unknown", "0000-00-00"), m.get("id", "")),
    )

    # ── Build gantt mmd (2022–present only) ──────────────────────────────────
    gantt_methods = [
        m for m in sorted_methods
        if str(m.get("year", "0")).isdigit() and int(m.get("year", 0)) >= 2022
    ]

    gantt_src = ["gantt", "    dateFormat  YYYY-MM-DD", "    axisFormat  %Y", "    tickInterval 1year"]
    for cat in CATEGORY_ORDER:
        meta = CATEGORY_META.get(cat, {})
        cat_methods = [m for m in gantt_methods if m.get("category") == cat]
        if not cat_methods:
            continue
        gantt_src.append(f"    section {meta.get('abbr', cat)}")
        for m in cat_methods:
            d = str(m.get("date") or "0000-01-01")
            if d.startswith("0000") or d == "unknown":
                continue  # skip unknown dates in the chart
            elif len(d) == 4:
                d = d + "-01-01"
            elif len(d) == 7:
                d = d + "-01"
            name_safe = m.get("name", m["id"]).replace(":", "").replace(",", "")[:28]
            gantt_src.append(f"        {name_safe} :milestone, {d}, 0d")

    gantt_mmd = "\n".join(gantt_src)
    mmd_path = ROOT / "assets" / "mermaid" / "timeline-gantt.mmd"
    mmd_path.write_text(gantt_mmd, encoding="utf-8")
    print("Wrote assets/mermaid/timeline-gantt.mmd")

    # ── Build docs/timeline.md ────────────────────────────────────────────────
    lines = [
        "# Chronological Timeline\n",
        "## Publication Timeline (2022 – present)\n",
        "![LLM Quantization Timeline Gantt Chart](../assets/mermaid-rendered/timeline-gantt.svg)\n",
        "## Full Table\n",
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


def render_preview_grid(methods):
    """HTML thumbnail grid of all method diagrams, 6 per row."""
    # Sort by category order then name for a consistent visual grouping
    cat_order = {c: i for i, c in enumerate(CATEGORY_ORDER)}
    sorted_m = sorted(
        methods,
        key=lambda m: (cat_order.get(m.get("category", ""), 99), m.get("name", m["id"]).lower()),
    )

    cols = 6
    rows_html = []
    row_cells = []

    for m in sorted_m:
        mid = m["id"]
        name = m.get("name", mid)
        diag = m.get("diagram", "")
        anchor = method_anchor(mid)
        if diag:
            cell = (
                f'<td align="center" width="160">'
                f'<a href="docs/methods.md#{anchor}">'
                f'<img src="{diag}" width="155" alt="{name}"><br>'
                f'<sub><b>{name}</b></sub>'
                f'</a></td>'
            )
        else:
            cell = (
                f'<td align="center" width="160">'
                f'<a href="docs/methods.md#{anchor}">'
                f'<sub><b>{name}</b></sub>'
                f'</a></td>'
            )
        row_cells.append(cell)
        if len(row_cells) == cols:
            rows_html.append("<tr>" + "".join(row_cells) + "</tr>")
            row_cells = []

    if row_cells:
        # Pad last row
        while len(row_cells) < cols:
            row_cells.append("<td></td>")
        rows_html.append("<tr>" + "".join(row_cells) + "</tr>")

    return "<table>\n" + "\n".join(rows_html) + "\n</table>"


def main():
    methods = load_methods()
    by_cat = sort_methods(methods)
    today = date.today().isoformat()
    n_cats = sum(1 for c in CATEGORY_ORDER if by_cat.get(c))

    # ── docs/methods.md — full method cards ───────────────────────────────────
    methods_parts = []
    methods_parts.append("# LLM Quantization Gallery — Method Details\n")
    methods_parts.append(
        "> Auto-generated by `scripts/build_readme.py`. Do not edit directly. "
        "Edit `methods.yml` and re-run the script.\n"
    )
    methods_parts.append(
        "See **[docs/notation.md](notation.md)** for the `W4A16`, `W8A8KV4`, "
        "group-size, and per-channel notation used everywhere. "
        "See **[docs/glossary.md](glossary.md)** for term definitions.\n"
    )

    methods_parts.append(render_toc(by_cat, methods))
    methods_parts.append(render_matrix(methods))
    methods_parts.append("")

    for cat in CATEGORY_ORDER:
        meta = CATEGORY_META.get(cat, {})
        title = meta.get("title", cat)
        desc = meta.get("description", "")
        cat_methods = by_cat.get(cat, [])

        methods_parts.append(f"---\n\n## {title}\n")
        if desc:
            methods_parts.append(f"{desc}\n")

        if not cat_methods:
            methods_parts.append("*No entries yet in this category.*\n")
        else:
            for m in cat_methods:
                methods_parts.append(render_card(m, path_prefix="../"))
                methods_parts.append("---\n")

    methods_parts.append(render_chronological_section(methods))
    methods_parts.append(f"\n---\n\n*Generated {today} from {len(methods)} entries across {n_cats} categories.*")

    methods_text = "\n".join(methods_parts)
    (ROOT / "docs" / "methods.md").write_text(methods_text, encoding="utf-8")
    print(f"Wrote docs/methods.md ({len(methods_text):,} chars, {len(methods)} methods)")

    # ── docs/lineage.md ───────────────────────────────────────────────────────
    lineage_body = render_mermaid_lineage(methods)
    lineage_doc = (
        "> Auto-generated by `scripts/build_readme.py`. Do not edit directly.\n\n"
        + lineage_body.replace("## Lineage Graph", "# Lineage Graph", 1)
    )
    (ROOT / "docs" / "lineage.md").write_text(lineage_doc, encoding="utf-8")
    print("Wrote docs/lineage.md")

    # ── docs/timeline.md ─────────────────────────────────────────────────────
    timeline_text = render_timeline(methods)
    (ROOT / "docs" / "timeline.md").write_text(timeline_text, encoding="utf-8")
    print("Wrote docs/timeline.md")

    # ── README.md — minimal, like llm-architecture-gallery ───────────────────
    readme_parts = []
    readme_parts.append("# LLM Quantization Gallery\n")
    readme_parts.append(
        "**Live gallery:** https://arpitsinghgautam.me/llm-quantization-gallery/\n"
    )
    readme_parts.append(
        f"A curated, visual reference for LLM quantization methods — "
        f"**{len(methods)} methods** across **{n_cats} categories**, "
        f"each with a flowchart diagram, fact sheet, and cross-references.\n"
    )
    readme_parts.append(
        "Modeled after Sebastian Raschka's "
        "[llm-architecture-gallery](https://github.com/rasbt/llm-architecture-gallery).\n"
    )
    readme_parts.append("**Browse:**\n")
    readme_parts.append(
        "- [Full method cards](docs/methods.md) — fact sheets, diagrams, key ideas\n"
        "- [Timeline](docs/timeline.md) — all methods sorted by date\n"
        "- [Lineage graph](docs/lineage.md) — builds-on relationships\n"
        "- [Notation guide](docs/notation.md) — `W4A16`, `W8A8KV4`, group sizes\n"
        "- [Glossary](docs/glossary.md)\n"
        "- [Contributing](CONTRIBUTING.md)\n"
    )
    readme_parts.append("\n## Preview\n")
    readme_parts.append(render_preview_grid(methods))
    readme_parts.append(f"\n\n---\n\n*{len(methods)} methods · {n_cats} categories · updated {today}*")

    readme_text = "\n".join(readme_parts)
    (ROOT / "README.md").write_text(readme_text, encoding="utf-8")
    print(f"Wrote README.md ({len(readme_text):,} chars)")


if __name__ == "__main__":
    main()
