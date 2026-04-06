import { lazy, Suspense, useMemo } from 'react'
import { useMethods } from '../data/useMethods'
import { categoryColor, CATEGORY_LABELS } from '../lib/categoryColors'
import { navigateTo } from '../router'
import type { Method } from '../data/schema'

const MermaidView = lazy(() =>
  import('../components/MermaidView').then(m => ({ default: m.MermaidView })),
)

// All field labels shown in the comparison table
const COMPARE_FIELDS: Array<{ key: keyof Method; label: string }> = [
  { key: 'category',               label: 'Category' },
  { key: 'year',                   label: 'Year' },
  { key: 'venue',                  label: 'Venue' },
  { key: 'precision',              label: 'Precision' },
  { key: 'granularity',            label: 'Granularity' },
  { key: 'calibration',            label: 'Calibration' },
  { key: 'symmetric',              label: 'Symmetric' },
  { key: 'handles_outliers_via',   label: 'Outlier handling' },
  { key: 'hardware_target',        label: 'Hardware target' },
  { key: 'requires_training',      label: 'Requires training' },
  { key: 'requires_calibration_data', label: 'Requires calib. data' },
  { key: 'typical_degradation',    label: 'Typical degradation' },
  { key: 'builds_on',              label: 'Builds on' },
  { key: 'superseded_by',          label: 'Superseded by' },
  { key: 'related',                label: 'Related' },
]

function valStr(v: unknown): string {
  if (v === null || v === undefined || v === '') return '—'
  if (typeof v === 'boolean') return v ? 'Yes' : 'No'
  if (Array.isArray(v)) return v.length === 0 ? '—' : v.join(', ')
  return String(v)
}

function valEq(a: unknown, b: unknown): boolean {
  return valStr(a) === valStr(b)
}

interface MethodColumnProps {
  method: Method
  field: keyof Method
  isDiff: boolean
  byId?: Map<string, Method>
}

function FieldCell({ method: m, field, isDiff, byId }: MethodColumnProps) {
  const value = m[field]
  const color = categoryColor(m.category)

  let display: React.ReactNode = valStr(value)

  if (field === 'category') {
    display = (
      <span className="badge" style={{ backgroundColor: color + '20', color }}>
        {CATEGORY_LABELS[m.category] ?? m.category}
      </span>
    )
  } else if (field === 'requires_training' || field === 'requires_calibration_data') {
    const v = Boolean(value)
    display = (
      <span className={`badge ${v
        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'
        : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'}`}>
        {v ? 'Yes' : 'No'}
      </span>
    )
  } else if ((field === 'builds_on' || field === 'superseded_by' || field === 'related') && Array.isArray(value)) {
    display = value.length === 0 ? '—' : (
      <div className="flex flex-wrap gap-1">
        {value.map(id => (
          <button
            key={id}
            onClick={() => navigateTo(`#/method/${id}`)}
            className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium
                       bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 hover:underline"
          >
            {byId?.get(id)?.name ?? id}
          </button>
        ))}
      </div>
    )
  } else if (field === 'precision') {
    display = <code className="text-[11px] font-mono">{valStr(value)}</code>
  }

  return (
    <td className={`py-2 px-3 text-xs text-gray-700 dark:text-gray-300 align-top border-b
                    border-gray-100 dark:border-gray-800 ${isDiff
                      ? 'bg-amber-50 dark:bg-amber-900/10 border-l-2 border-l-amber-400'
                      : ''}`}>
      {display}
    </td>
  )
}

interface CompareViewProps {
  ids: string[]
}

export function CompareView({ ids }: CompareViewProps) {
  const { byId } = useMethods()
  const methods = ids.map(id => byId.get(id)).filter((m): m is Method => !!m)

  if (methods.length < 2) {
    return (
      <main className="mx-auto max-w-screen-2xl px-4 py-16 text-center">
        <p className="text-gray-500 dark:text-gray-400 mb-4">
          Need at least 2 valid method IDs to compare. Got: {ids.join(', ')}
        </p>
        <button onClick={() => navigateTo('#/')} className="btn-primary">← Back to gallery</button>
      </main>
    )
  }

  const sharedLineage = useMemo(() => {
    const sets = methods.map(m => new Set([...m.builds_on, ...m.related]))
    return [...sets[0]].filter(id => sets.slice(1).every(s => s.has(id)))
  }, [methods])

  const swap = () => {
    if (methods.length === 2) {
      navigateTo(`#/compare/${methods[1].id}/${methods[0].id}`)
    }
  }

  return (
    <main className="mx-auto max-w-screen-2xl px-4 py-6">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Compare: {methods.map(m => m.name).join(' × ')}
          </h1>
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Rows highlighted in amber differ between methods.
          </p>
        </div>
        <div className="flex gap-2">
          {methods.length === 2 && (
            <button onClick={swap} className="btn-ghost text-sm">⇄ Swap</button>
          )}
          <button onClick={() => navigateTo('#/')} className="btn-ghost text-sm">
            Pick different methods
          </button>
        </div>
      </div>

      {/* SVG diagrams side by side */}
      <div className={`grid gap-4 mb-8 ${methods.length === 2 ? 'grid-cols-2' : methods.length === 3 ? 'grid-cols-3' : 'grid-cols-4'}`}>
        {methods.map(m => (
          <div key={m.id} className="space-y-2">
            <div className="flex items-center gap-2">
              <div className="w-1 h-5 rounded-full" style={{ backgroundColor: categoryColor(m.category) }} aria-hidden="true" />
              <button
                onClick={() => navigateTo(`#/method/${m.id}`)}
                className="text-sm font-semibold text-gray-900 dark:text-white hover:underline"
              >
                {m.name}
              </button>
              <span className="badge bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400 text-[10px]">
                {m.year}
              </span>
            </div>
            <img
              src={`${import.meta.env.BASE_URL}assets/diagrams/${m.id}.svg`}
              alt={`${m.name} diagram`}
              loading="lazy"
              decoding="async"
              className="w-full rounded border border-gray-200 dark:border-gray-800"
              onError={e => { (e.target as HTMLImageElement).style.display = 'none' }}
            />
          </div>
        ))}
      </div>

      {/* Comparison table */}
      <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-800">
        <table className="w-full border-collapse min-w-[600px]">
          <thead>
            <tr className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
              <th className="py-2 px-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 w-36">
                Field
              </th>
              {methods.map(m => (
                <th key={m.id} className="py-2 px-3 text-left text-xs font-semibold text-gray-900 dark:text-white">
                  <button
                    onClick={() => navigateTo(`#/method/${m.id}`)}
                    className="hover:underline"
                    style={{ color: categoryColor(m.category) }}
                  >
                    {m.name}
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {COMPARE_FIELDS.map(({ key, label }) => {
              const values = methods.map(m => m[key])
              const isDiff = values.length > 1 && !values.every(v => valEq(v, values[0]))
              return (
                <tr key={key}>
                  <th
                    scope="row"
                    className={`py-2 px-3 text-left text-xs font-medium align-top whitespace-nowrap
                               border-b border-gray-100 dark:border-gray-800
                               ${isDiff ? 'text-amber-700 dark:text-amber-400' : 'text-gray-500 dark:text-gray-400'}`}
                  >
                    {label}
                    {isDiff && <span className="ml-1 text-amber-400">●</span>}
                  </th>
                  {methods.map(m => (
                    <FieldCell key={m.id} method={m} field={key} isDiff={isDiff} byId={byId} />
                  ))}
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Shared lineage */}
      {sharedLineage.length > 0 && (
        <div className="mt-8 rounded-lg border border-gray-200 dark:border-gray-800 p-4">
          <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Shared lineage</h2>
          <div className="flex flex-wrap gap-2">
            {sharedLineage.map(id => (
              <button
                key={id}
                onClick={() => navigateTo(`#/method/${id}`)}
                className="badge bg-purple-50 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 hover:underline cursor-pointer"
              >
                {byId.get(id)?.name ?? id}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Flowcharts */}
      <div className="mt-8">
        <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">Flowcharts</h2>
        <div className={`grid gap-4 ${methods.length === 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1'}`}>
          {methods.map(m => (
            <div key={m.id} className="rounded-lg border border-gray-200 dark:border-gray-800 p-4 bg-gray-50 dark:bg-gray-900">
              <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-3">{m.name}</p>
              <Suspense fallback={<div className="h-16 flex items-center justify-center text-sm text-gray-400">Loading…</div>}>
                <MermaidView methodId={m.id} />
              </Suspense>
            </div>
          ))}
        </div>
      </div>
    </main>
  )
}
