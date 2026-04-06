import { lazy, Suspense, useMemo } from 'react'
import { useMethods } from '../data/useMethods'
import { FactTable } from '../components/FactTable'
import { categoryColor, CATEGORY_LABELS, CATEGORY_TITLES, CATEGORY_ORDER } from '../lib/categoryColors'
import { navigateTo } from '../router'
import type { Method } from '../data/schema'

const MermaidView = lazy(() =>
  import('../components/MermaidView').then(m => ({ default: m.MermaidView })),
)

interface MethodViewProps {
  id: string
}

function LineageMermaid({ method, byId }: { method: Method; byId: Map<string, Method> }) {
  const neighbors = useMemo(() => {
    const seen = new Set<string>()
    const edges: string[] = []

    const addEdge = (from: string, to: string, label: string) => {
      const key = `${from}→${to}`
      if (!seen.has(key)) { seen.add(key); edges.push(`    ${from} -->|${label}| ${to}`) }
    }

    const nodeName = (id: string) => byId.get(id)?.name ?? id

    for (const dep of method.builds_on) {
      if (dep && dep !== method.id) addEdge(dep.replace(/-/g, '_'), method.id.replace(/-/g, '_'), 'basis')
    }
    for (const sup of method.superseded_by) {
      if (sup && sup !== method.id) addEdge(method.id.replace(/-/g, '_'), sup.replace(/-/g, '_'), 'superseded by')
    }
    for (const rel of method.related) {
      if (rel && rel !== method.id) addEdge(method.id.replace(/-/g, '_'), rel.replace(/-/g, '_'), 'related')
    }

    if (edges.length === 0) return null

    // Build node labels
    const allIds = new Set<string>([
      method.id,
      ...method.builds_on,
      ...method.superseded_by,
      ...method.related,
    ])
    const nodeLines = [...allIds]
      .filter(id => id && id !== '')
      .map(id => `    ${id.replace(/-/g, '_')}["${nodeName(id).replace(/"/g, "'")}"]`)

    return `flowchart LR\n${nodeLines.join('\n')}\n${edges.join('\n')}`
  }, [method, byId])

  if (!neighbors) return null

  return (
    <div className="mt-8">
      <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Lineage</h2>
      <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 overflow-x-auto bg-gray-50 dark:bg-gray-900">
        <Suspense fallback={<div className="h-16 flex items-center justify-center text-sm text-gray-400">Loading…</div>}>
          <MermaidView source={neighbors} />
        </Suspense>
      </div>
    </div>
  )
}

export function MethodView({ id }: MethodViewProps) {
  const { methods, byId } = useMethods()
  const method = byId.get(id)

  if (!method) {
    return (
      <main className="mx-auto max-w-screen-2xl px-4 py-16 text-center">
        <p className="text-lg text-gray-500 dark:text-gray-400 mb-4">
          Method <code className="text-sm bg-gray-100 dark:bg-gray-800 px-1 rounded">{id}</code> not found.
        </p>
        <button onClick={() => navigateTo('#/')} className="btn-primary">
          ← Back to gallery
        </button>
      </main>
    )
  }

  const color = categoryColor(method.category)
  const catLabel = CATEGORY_LABELS[method.category] ?? method.category
  const catTitle = CATEGORY_TITLES[method.category] ?? method.category
  const svgUrl = `${import.meta.env.BASE_URL}assets/diagrams/${method.id}.svg`

  // Prev/next within same category, sorted by year
  const catMethods = useMemo(() => {
    return methods
      .filter(m => m.category === method.category)
      .sort((a, b) => a.year - b.year || a.name.localeCompare(b.name))
  }, [methods, method.category])

  const idx = catMethods.findIndex(m => m.id === method.id)
  const prev = idx > 0 ? catMethods[idx - 1] : null
  const next = idx < catMethods.length - 1 ? catMethods[idx + 1] : null

  return (
    <main className="mx-auto max-w-screen-2xl px-4 py-6">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="text-xs text-gray-500 dark:text-gray-400 mb-4 flex items-center gap-1">
        <button onClick={() => navigateTo('#/')} className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
          Gallery
        </button>
        <span>/</span>
        <button
          onClick={() => {
            window.dispatchEvent(new CustomEvent('filter-category', { detail: method.category }))
            navigateTo('#/')
          }}
          className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          {catLabel}
        </button>
        <span>/</span>
        <span className="text-gray-700 dark:text-gray-300">{method.name}</span>
      </nav>

      {/* Header */}
      <div className="mb-6 flex flex-col sm:flex-row sm:items-start justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div
              className="w-1 h-8 rounded-full shrink-0"
              style={{ backgroundColor: color }}
              aria-hidden="true"
            />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{method.name}</h1>
          </div>
          {method.full_name && method.full_name !== method.name && (
            <p className="text-sm text-gray-500 dark:text-gray-400 pl-3">{method.full_name}</p>
          )}
          <div className="mt-2 pl-3 flex flex-wrap gap-2">
            <span className="badge bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300">
              {method.year}
            </span>
            <span className="badge" style={{ backgroundColor: color + '20', color }}>
              {catLabel}
            </span>
            {method.precision && method.precision !== 'n/a' && (
              <code className="badge bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 font-mono text-[11px]">
                {method.precision.split('(')[0].trim()}
              </code>
            )}
          </div>
        </div>

        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => {
              const other = prompt('Enter method ID to compare with (e.g. gptq, awq):')
              if (other) navigateTo(`#/compare/${method.id}/${other.trim()}`)
            }}
            className="btn-ghost text-sm"
          >
            Compare with…
          </button>
          <button onClick={() => navigateTo('#/')} className="btn-ghost text-sm">
            ← Gallery
          </button>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="flex flex-col lg:flex-row gap-8">
        {/* Left: diagrams + prose */}
        <div className="flex-1 min-w-0 space-y-6">
          {/* SVG diagram */}
          <section aria-label="Architecture diagram">
            <img
              src={svgUrl}
              alt={method.diagram_caption || `${method.name} diagram`}
              role="img"
              aria-label={`${method.name}: ${method.diagram_caption}`}
              decoding="async"
              loading="eager"
              className="w-full rounded-lg border border-gray-200 dark:border-gray-800"
              onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
            />
          </section>

          {/* Mermaid flowchart */}
          <section aria-label="Method flowchart">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Flowchart</h2>
            <div className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-gray-50 dark:bg-gray-900">
              <Suspense fallback={<div className="h-24 flex items-center justify-center text-sm text-gray-400">Loading…</div>}>
                <MermaidView methodId={method.id} />
              </Suspense>
            </div>
          </section>

          {/* TL;DR */}
          <section aria-label="Summary">
            <blockquote className="border-l-4 pl-4 text-sm text-gray-700 dark:text-gray-300 leading-relaxed italic"
              style={{ borderColor: color }}>
              {method.tldr}
            </blockquote>
          </section>

          {/* Key idea */}
          {method.key_idea && (
            <section aria-label="How it works">
              <h2 className="text-base font-semibold text-gray-900 dark:text-white mb-2">How it works</h2>
              <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                {method.key_idea}
              </p>
            </section>
          )}
        </div>

        {/* Right: fact table (sticky on desktop) */}
        <aside
          className="w-full lg:w-80 xl:w-96 shrink-0"
          aria-label="Method fact sheet"
        >
          <div className="lg:sticky lg:top-20">
            <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Fact Sheet</h2>
            <FactTable method={method} byId={byId} />
          </div>
        </aside>
      </div>

      {/* Lineage graph */}
      <LineageMermaid method={method} byId={byId} />

      {/* Prev / Next */}
      <nav
        aria-label="Previous and next methods in category"
        className="mt-10 pt-6 border-t border-gray-200 dark:border-gray-800
                   flex items-center justify-between text-sm"
      >
        {prev ? (
          <button
            onClick={() => navigateTo(`#/method/${prev.id}`)}
            className="flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            ← {prev.name}
          </button>
        ) : <span />}
        {next ? (
          <button
            onClick={() => navigateTo(`#/method/${next.id}`)}
            className="flex items-center gap-1 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
          >
            {next.name} →
          </button>
        ) : <span />}
      </nav>
    </main>
  )
}
