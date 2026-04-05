# Contributing to the LLM Quantization Gallery

Thank you for helping keep this gallery accurate and up to date.

## The one rule: never hand-edit README.md or docs/timeline.md

These two files are **auto-generated** from `methods.yml` by `scripts/build_readme.py`.
Any manual edits will be overwritten the next time the script runs.
The only workflow is:

1. Edit `methods.yml`  
2. Add a diagram  
3. Run the build scripts  
4. Open a pull request  

---

## Adding a new method

### 1. Verify the paper exists

Before writing a single line of YAML, confirm that:
- The arxiv / OpenReview / ACM / ACL URL resolves to a real paper page
- You have the correct authors, date, and title from the abstract page (not from a secondary summary)

Never add a `paper_url` you cannot manually open.

### 2. Add an entry to `methods.yml`

Copy the template below and fill in **every** field. Use `null` for optional URL fields
that genuinely don't exist (blog post, code, etc.).  
Use the literal string `"unknown"` for required fields you cannot determine.

```yaml
- id: your-method-id          # kebab-case, lowercase, stable — becomes the #anchor
  name: YourMethodName
  full_name: "Full Paper Title"
  category: ptq_weight_only   # see valid values below
  subcategory: free-form      # e.g. "second-order", "rotation-based", "codebook"
  year: 2024
  date: 2024-06-15            # arxiv v1 date, YYYY-MM-DD
  authors: ["Alice Smith", "Bob Jones"]
  affiliation: ["MIT", "Stanford"]
  paper_url: https://arxiv.org/abs/XXXX.XXXXX
  code_url: https://github.com/org/repo   # or null
  blog_url: null
  venue: "NeurIPS 2024"       # or null

  precision: "W4A16"          # use WxAyKVz notation from docs/notation.md
  granularity: "per-group, g=128"
  calibration: "128 sequences × 2048 tokens, unlabeled"
  symmetric: asymmetric       # symmetric | asymmetric | mixed | n/a
  handles_outliers_via: "description of technique"
  hardware_target: "GPU (CUDA)"
  requires_training: false
  requires_calibration_data: true
  typical_degradation: "< 0.5 ppl on LLaMA-3-8B at 4-bit"

  tldr: >
    One paragraph in plain English. What it does, why it works, what it costs.
    Write this in your own words — do not copy the abstract.
  key_idea: >
    2–4 sentences on the actual mechanism.

  builds_on: []               # list of method ids this builds on
  superseded_by: []
  related: []

  diagram: assets/diagrams/your-method-id.svg
  diagram_caption: "One sentence describing the diagram."
```

### Valid category values

| Value | Meaning |
|-------|---------|
| `ptq_weight_only` | PTQ, weights only quantized |
| `ptq_weight_activation` | PTQ, both weights and activations |
| `qat` | QAT or quantized fine-tuning (involves gradient updates) |
| `extreme_lowbit` | Sub-2-bit, binary, ternary |
| `kv_cache` | KV-cache quantization |
| `low_precision_training` | Low-precision training / numerical formats |
| `moe` | MoE-specific quantization |
| `systems` | Runtimes, kernels, inference engines |

### 3. Add a diagram

Create `assets/diagrams/your-method-id.svg` (800×500 viewBox, transparent or light background).
For consistency with the gallery style:
- Use the category accent color (see `scripts/generate_diagrams.py → CATEGORY_COLORS`)
- Include a title bar at top with the method name and precision
- Show the core algorithmic idea (a schematic, not marketing)

You can run the auto-generator for a starter diagram:

```bash
python scripts/generate_diagrams.py --id your-method-id
```

The generated diagram will use a generic template. Replace or refine the SVG content manually
if you want a method-specific schematic.

### 4. Add sources

In `docs/sources.md`, add a block under your method id:

```markdown
## your-method-id
- https://arxiv.org/abs/XXXX.XXXXX
- https://github.com/org/repo
- (any other URLs you consulted)
```

### 5. Validate and build

```bash
# Check schema, cross-references, and diagram file existence
python scripts/validate.py

# Also check that all URLs resolve (optional, slower)
python scripts/validate.py --check-urls

# Regenerate README.md and docs/timeline.md
python scripts/build_readme.py
```

Both scripts must pass without errors before opening a PR.

### 6. Open a pull request

- Title: `feat(<category>): add <MethodName>`
- Include a brief description of the method and why it belongs in the gallery
- Link the paper

---

## Fixing an existing entry

Edit the relevant fields in `methods.yml`, then re-run the build scripts. If you're fixing
a factual error, please include the source URL that corrects the record in your PR description.

## Updating a diagram

Replace or modify `assets/diagrams/<id>.svg`, then re-run `scripts/build_readme.py`.
SVG edits alone do not require running `validate.py`.

## Reporting errors without a PR

Open a GitHub issue. Include the method id, the incorrect field, the correct value,
and a URL that supports the correction.

---

## Style guidelines

- **WxAyKVz notation** always, everywhere. See [docs/notation.md](docs/notation.md).
- **No marketing language** in `tldr` or `key_idea`: no "state-of-the-art," "revolutionary," "breakthrough."
- **Perplexity** comparisons: always specify dataset (WikiText-2 or C4) and model.
- **Group size**: always written as "group size *g*" or "g=128", not "block size."
- **No copy-pasted abstracts.** The `tldr` must be written in your own words.
