/**
 * yaml-to-json.mjs
 * Converts ../methods.yml → src/data/methods.json + src/data/meta.json
 * and copies assets/diagrams/ + assets/mermaid/ + docs/*.md into public/.
 *
 * Run: node scripts/yaml-to-json.mjs
 */

import { readFileSync, writeFileSync, cpSync, mkdirSync, existsSync, readdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import yaml from 'js-yaml'

const __dir = dirname(fileURLToPath(import.meta.url))
const ROOT  = resolve(__dir, '..', '..')        // repo root
const SITE  = resolve(__dir, '..')              // site/

// ─── Paths ───────────────────────────────────────────────────────────────────
const METHODS_YML     = resolve(ROOT,  'methods.yml')
const METHODS_JSON    = resolve(SITE,  'src/data/methods.json')
const META_JSON       = resolve(SITE,  'src/data/meta.json')
const SRC_DIAGRAMS          = resolve(ROOT,  'assets/diagrams')
const SRC_MERMAID           = resolve(ROOT,  'assets/mermaid')
const SRC_MERMAID_RENDERED  = resolve(ROOT,  'assets/mermaid-rendered')
const SRC_DOCS              = resolve(ROOT,  'docs')
const DEST_ASSETS     = resolve(SITE,  'public/assets')
const DEST_DOCS       = resolve(SITE,  'public/docs')

// ─── Category metadata (mirrors build_readme.py) ──────────────────────────
const CATEGORY_META = {
  ptq_weight_only:        { title: 'Post-Training Quantization — Weight-Only',        abbr: 'PTQ W-only',   color: '#4A90D9' },
  ptq_weight_activation:  { title: 'Post-Training Quantization — Weights + Activations', abbr: 'PTQ W+A',   color: '#E87D3E' },
  qat:                    { title: 'Quantization-Aware Training & Quantized Fine-Tuning', abbr: 'QAT / QFT', color: '#7B68EE' },
  extreme_lowbit:         { title: 'Extreme Low-Bit & Binary/Ternary Quantization',   abbr: 'Sub-2-bit',    color: '#E84393' },
  kv_cache:               { title: 'KV-Cache Quantization',                           abbr: 'KV Quant',     color: '#3DAD78' },
  low_precision_training: { title: 'Low-Precision Training & Numerical Formats',      abbr: 'LP Training',  color: '#D4A027' },
  moe:                    { title: 'MoE-Specific Quantization',                       abbr: 'MoE Quant',    color: '#9B59B6' },
  systems:                { title: 'Systems, Kernels & Runtimes',                     abbr: 'Systems',      color: '#607D8B' },
}

const REQUIRED_FIELDS = [
  'id', 'name', 'full_name', 'category', 'year',
  'precision', 'requires_training', 'requires_calibration_data', 'tldr',
]

// ─── Load & validate ─────────────────────────────────────────────────────────
console.log('[yaml-to-json] Reading', METHODS_YML)
const raw = readFileSync(METHODS_YML, 'utf-8')
const methods = yaml.load(raw)

if (!Array.isArray(methods)) {
  console.error('methods.yml must be a YAML list')
  process.exit(1)
}

const errors = []

const cleaned = methods.map((m, idx) => {
  const id = m.id ?? `entry-${idx}`

  // Required field check
  for (const field of REQUIRED_FIELDS) {
    if (m[field] === undefined || m[field] === null) {
      errors.push(`[${id}] missing required field: ${field}`)
    }
  }

  // Category check
  if (m.category && !CATEGORY_META[m.category]) {
    errors.push(`[${id}] unknown category: ${m.category}`)
  }

  // Normalize date: yaml parses YYYY-MM-DD as JS Date; convert to string
  const dateVal = m.date instanceof Date
    ? m.date.toISOString().slice(0, 10)
    : (m.date ?? `${m.year ?? 2020}-01-01`)

  return {
    id:                       String(id),
    name:                     String(m.name ?? ''),
    full_name:                String(m.full_name ?? ''),
    category:                 String(m.category ?? ''),
    subcategory:              String(m.subcategory ?? ''),
    year:                     Number(m.year ?? 2020),
    date:                     String(dateVal),
    authors:                  Array.isArray(m.authors) ? m.authors.map(String) : [],
    affiliation:              Array.isArray(m.affiliation) ? m.affiliation.map(String) : [],
    paper_url:                m.paper_url ? String(m.paper_url) : null,
    code_url:                 m.code_url  ? String(m.code_url)  : null,
    blog_url:                 m.blog_url  ? String(m.blog_url)  : null,
    venue:                    String(m.venue ?? ''),
    precision:                String(m.precision ?? ''),
    granularity:              String(m.granularity ?? ''),
    calibration:              String(m.calibration ?? ''),
    symmetric:                m.symmetric != null ? String(m.symmetric) : 'unknown',
    handles_outliers_via:     String(m.handles_outliers_via ?? ''),
    hardware_target:          String(m.hardware_target ?? ''),
    requires_training:        Boolean(m.requires_training),
    requires_calibration_data: Boolean(m.requires_calibration_data),
    typical_degradation:      String(m.typical_degradation ?? ''),
    tldr:                     String(m.tldr ?? ''),
    key_idea:                 String(m.key_idea ?? ''),
    builds_on:                Array.isArray(m.builds_on) ? m.builds_on.map(String) : [],
    superseded_by:            Array.isArray(m.superseded_by) ? m.superseded_by.map(String) : [],
    related:                  Array.isArray(m.related) ? m.related.map(String) : [],
    diagram:                  String(m.diagram ?? ''),
    diagram_caption:          String(m.diagram_caption ?? ''),
  }
})

if (errors.length > 0) {
  console.error('\n[yaml-to-json] Validation errors:')
  errors.forEach(e => console.error(' ', e))
  process.exit(1)
}

// ─── Write methods.json ───────────────────────────────────────────────────────
mkdirSync(dirname(METHODS_JSON), { recursive: true })
writeFileSync(METHODS_JSON, JSON.stringify(cleaned, null, 2))
console.log(`[yaml-to-json] Wrote methods.json (${cleaned.length} methods)`)

// ─── Write meta.json ─────────────────────────────────────────────────────────
const categoryCounts = {}
for (const m of cleaned) {
  categoryCounts[m.category] = (categoryCounts[m.category] ?? 0) + 1
}

const categories = Object.entries(CATEGORY_META).map(([id, meta]) => ({
  id,
  title: meta.title,
  abbr:  meta.abbr,
  color: meta.color,
  count: categoryCounts[id] ?? 0,
}))

const meta = {
  count: cleaned.length,
  lastUpdated: new Date().toISOString().slice(0, 10),
  categories,
}
writeFileSync(META_JSON, JSON.stringify(meta, null, 2))
console.log('[yaml-to-json] Wrote meta.json')

// ─── Copy assets ─────────────────────────────────────────────────────────────
function copyDir(src, dest) {
  if (!existsSync(src)) { console.warn(`[yaml-to-json] skipping missing dir: ${src}`); return }
  mkdirSync(dest, { recursive: true })
  cpSync(src, dest, { recursive: true })
  const count = readdirSync(dest).length
  console.log(`[yaml-to-json] Copied ${src} → ${dest} (${count} files)`)
}

copyDir(SRC_DIAGRAMS,         resolve(DEST_ASSETS, 'diagrams'))
copyDir(SRC_MERMAID,         resolve(DEST_ASSETS, 'mermaid'))
copyDir(SRC_MERMAID_RENDERED, resolve(DEST_ASSETS, 'mermaid-rendered'))
copyDir(SRC_DOCS,            DEST_DOCS)

console.log('[yaml-to-json] Done.')
