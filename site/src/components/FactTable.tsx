import type { Method } from '../data/schema'
import { navigateTo } from '../router'
import { categoryColor, CATEGORY_LABELS } from '../lib/categoryColors'

interface FactTableProps {
  method: Method
  byId?: Map<string, Method>
  /** In compare mode, highlight cells that differ */
  diffValue?: string | boolean | string[] | null
  isDiff?: boolean
}

function Row({ label, children, isDiff }: { label: string; children: React.ReactNode; isDiff?: boolean }) {
  return (
    <tr className={isDiff ? 'bg-amber-50 dark:bg-amber-900/10' : undefined}>
      <th
        scope="row"
        className="py-1.5 pr-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 align-top whitespace-nowrap w-40"
      >
        {label}
      </th>
      <td className={`py-1.5 text-xs text-gray-800 dark:text-gray-200 ${isDiff ? 'border-l-2 border-amber-400 pl-2' : ''}`}>
        {children}
      </td>
    </tr>
  )
}

function PillLink({ id, byId }: { id: string; byId?: Map<string, Method> }) {
  const m = byId?.get(id)
  return (
    <button
      onClick={() => navigateTo(`#/method/${id}`)}
      className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium
                 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300
                 hover:bg-blue-100 dark:hover:bg-blue-800/40 transition-colors mr-1 mb-1"
    >
      {m?.name ?? id}
    </button>
  )
}

function BoolBadge({ value }: { value: boolean }) {
  return (
    <span className={`badge ${value
      ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'
      : 'bg-gray-100 text-gray-500 dark:bg-gray-800 dark:text-gray-400'
    }`}>
      {value ? 'Yes' : 'No'}
    </span>
  )
}

export function FactTable({ method: m, byId }: FactTableProps) {
  const color = categoryColor(m.category)

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 dark:border-gray-800">
      <table className="w-full border-collapse">
        <caption className="sr-only">Fact sheet for {m.name}</caption>
        <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
          <Row label="Category">
            <span className="badge" style={{ backgroundColor: color + '20', color }}>
              {CATEGORY_LABELS[m.category] ?? m.category}
            </span>
          </Row>
          {m.subcategory && (
            <Row label="Subcategory">
              <span className="text-gray-600 dark:text-gray-400">{m.subcategory}</span>
            </Row>
          )}
          <Row label="Year">{m.year}</Row>
          {m.venue && <Row label="Venue">{m.venue}</Row>}
          {m.authors.length > 0 && (
            <Row label="Authors">{m.authors.join(', ')}</Row>
          )}
          {m.affiliation.length > 0 && (
            <Row label="Affiliation">{m.affiliation.join('; ')}</Row>
          )}
          <Row label="Precision">
            <code className="text-[11px] font-mono">{m.precision}</code>
          </Row>
          {m.granularity && <Row label="Granularity">{m.granularity}</Row>}
          {m.calibration && <Row label="Calibration">{m.calibration}</Row>}
          {m.symmetric !== 'unknown' && <Row label="Symmetric">{m.symmetric}</Row>}
          {m.handles_outliers_via && (
            <Row label="Outlier handling">{m.handles_outliers_via}</Row>
          )}
          {m.hardware_target && (
            <Row label="Hardware target">{m.hardware_target}</Row>
          )}
          <Row label="Requires training">
            <BoolBadge value={m.requires_training} />
          </Row>
          <Row label="Requires calib. data">
            <BoolBadge value={m.requires_calibration_data} />
          </Row>
          {m.typical_degradation && (
            <Row label="Typical degradation">{m.typical_degradation}</Row>
          )}
          {m.builds_on.length > 0 && (
            <Row label="Builds on">
              <div className="flex flex-wrap">
                {m.builds_on.map(id => <PillLink key={id} id={id} byId={byId} />)}
              </div>
            </Row>
          )}
          {m.superseded_by.length > 0 && (
            <Row label="Superseded by">
              <div className="flex flex-wrap">
                {m.superseded_by.map(id => <PillLink key={id} id={id} byId={byId} />)}
              </div>
            </Row>
          )}
          {m.related.length > 0 && (
            <Row label="Related">
              <div className="flex flex-wrap">
                {m.related.map(id => <PillLink key={id} id={id} byId={byId} />)}
              </div>
            </Row>
          )}
          <Row label="Links">
            <div className="flex flex-wrap gap-2">
              {m.paper_url && (
                <a href={m.paper_url} target="_blank" rel="noopener noreferrer"
                   className="text-blue-600 dark:text-blue-400 hover:underline">
                  Paper ↗
                </a>
              )}
              {m.code_url && (
                <a href={m.code_url} target="_blank" rel="noopener noreferrer"
                   className="text-blue-600 dark:text-blue-400 hover:underline">
                  Code ↗
                </a>
              )}
              {m.blog_url && (
                <a href={m.blog_url} target="_blank" rel="noopener noreferrer"
                   className="text-blue-600 dark:text-blue-400 hover:underline">
                  Blog ↗
                </a>
              )}
            </div>
          </Row>
        </tbody>
      </table>
    </div>
  )
}
