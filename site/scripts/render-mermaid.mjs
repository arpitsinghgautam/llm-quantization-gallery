/**
 * render-mermaid.mjs
 * Pre-renders all assets/mermaid/*.mmd → assets/mermaid-rendered/*.svg
 * using the kroki.io public API (same engine as GitLab diagrams).
 *
 * Run: node scripts/render-mermaid.mjs
 * Requires Node 18+ (built-in fetch).
 */

import { readFileSync, writeFileSync, readdirSync, existsSync, mkdirSync } from 'fs'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'

const __dir = dirname(fileURLToPath(import.meta.url))
const ROOT    = resolve(__dir, '..', '..')
const MMD_DIR = resolve(ROOT, 'assets', 'mermaid')
const OUT_DIR = resolve(ROOT, 'assets', 'mermaid-rendered')

mkdirSync(OUT_DIR, { recursive: true })

const files = readdirSync(MMD_DIR).filter(f => f.endsWith('.mmd')).sort()
let ok = 0, skipped = 0, failed = 0

// Optional: re-render all even if file exists (set FORCE=1)
const force = process.env.FORCE === '1'

async function renderOne(file) {
  const id     = file.replace('.mmd', '')
  const output = resolve(OUT_DIR, `${id}.svg`)

  if (!force && existsSync(output)) {
    skipped++
    return
  }

  const src = readFileSync(resolve(MMD_DIR, file), 'utf-8').trim()

  try {
    const res = await fetch('https://kroki.io/mermaid/svg', {
      method:  'POST',
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
      body:    src,
      signal:  AbortSignal.timeout(15_000),
    })

    if (!res.ok) throw new Error(`HTTP ${res.status}: ${await res.text()}`)

    const svg = await res.text()
    writeFileSync(output, svg, 'utf-8')
    ok++
    console.log(`  [ok]   ${id}`)
  } catch (e) {
    failed++
    console.warn(`  [fail] ${id}: ${e.message}`)
  }
}

// Run in batches of 6 to avoid hammering the API
const BATCH = 6
for (let i = 0; i < files.length; i += BATCH) {
  const batch = files.slice(i, i + BATCH)
  await Promise.all(batch.map(renderOne))
  // Brief pause between batches
  if (i + BATCH < files.length) await new Promise(r => setTimeout(r, 300))
}

console.log(`\nDone: ${ok} rendered, ${skipped} skipped, ${failed} failed`)
if (failed > 0) process.exit(1)
