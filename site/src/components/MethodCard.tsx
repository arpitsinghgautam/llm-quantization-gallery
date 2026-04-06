import { useRef, useEffect } from 'react'
import type { Method } from '../data/schema'
import { categoryColor, CATEGORY_LABELS } from '../lib/categoryColors'
import { navigateTo } from '../router'

interface MethodCardProps {
  method: Method
  inCompare: boolean
  onCompareToggle: (id: string) => void
  compareDisabled: boolean
}

export function MethodCard({ method: m, inCompare, onCompareToggle, compareDisabled }: MethodCardProps) {
  const color = categoryColor(m.category)
  const label = CATEGORY_LABELS[m.category] ?? m.category
  const svgUrl = `${import.meta.env.BASE_URL}assets/diagrams/${m.id}.svg`
  const truncTldr = m.tldr.length > 160 ? m.tldr.slice(0, 157).trimEnd() + '…' : m.tldr
  const checkRef = useRef<HTMLInputElement>(null)

  // Prevent card click when interacting with checkbox
  const handleCardClick = (e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('[data-no-navigate]')) return
    navigateTo(`#/method/${m.id}`)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      navigateTo(`#/method/${m.id}`)
    }
  }

  return (
    <article
      className="relative flex flex-col rounded-lg border border-gray-200 dark:border-gray-800
                 bg-white dark:bg-gray-900 overflow-hidden card-hover cursor-pointer
                 focus-within:ring-2 focus-within:ring-blue-500"
      onClick={handleCardClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="article"
      aria-label={`${m.name}: ${m.diagram_caption || m.tldr.slice(0, 80)}`}
    >
      {/* Category accent stripe */}
      <div
        className="absolute left-0 top-0 bottom-0 w-1 rounded-l-lg"
        style={{ backgroundColor: color }}
        aria-hidden="true"
      />

      {/* Compare checkbox */}
      <div
        data-no-navigate
        className="absolute top-2 right-2 z-10"
        onClick={e => e.stopPropagation()}
      >
        <label className="flex items-center gap-1 cursor-pointer select-none">
          <input
            ref={checkRef}
            type="checkbox"
            checked={inCompare}
            disabled={compareDisabled && !inCompare}
            onChange={() => onCompareToggle(m.id)}
            aria-label={`Add ${m.name} to compare`}
            className="w-3.5 h-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500
                       disabled:opacity-40 cursor-pointer"
          />
          <span className="text-xs text-gray-400 dark:text-gray-500 sr-only">Compare</span>
        </label>
      </div>

      {/* SVG diagram */}
      <div className="pl-1 aspect-[16/10] overflow-hidden bg-gray-50 dark:bg-gray-800/50">
        <img
          src={svgUrl}
          alt={m.diagram_caption || `${m.name} diagram`}
          loading="lazy"
          decoding="async"
          role="img"
          aria-label={`${m.name}: ${m.diagram_caption}`}
          className="w-full h-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = 'none'
          }}
        />
      </div>

      {/* Card body */}
      <div className="flex flex-col flex-1 pl-3 pr-3 pt-2.5 pb-3 gap-2">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white leading-tight">
            {m.name}
          </h3>
          <div className="flex items-center gap-1 shrink-0">
            <span className="badge bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400 font-mono text-[10px]">
              {m.year}
            </span>
          </div>
        </div>

        {/* Precision badge */}
        {m.precision && m.precision !== 'n/a' && (
          <span
            className="badge text-[10px] font-mono self-start"
            style={{ backgroundColor: color + '20', color }}
          >
            {m.precision.split('(')[0].trim().slice(0, 28)}
          </span>
        )}

        {/* TLDR */}
        <p className="text-xs text-gray-600 dark:text-gray-400 leading-relaxed line-clamp-3">
          {truncTldr}
        </p>

        {/* Footer */}
        <div className="mt-auto flex items-center justify-between gap-2 pt-1">
          <span
            className="badge text-[10px]"
            style={{ backgroundColor: color + '15', color }}
          >
            {label}
          </span>
          <div className="flex items-center gap-2" data-no-navigate onClick={e => e.stopPropagation()}>
            {m.paper_url && (
              <a
                href={m.paper_url}
                target="_blank"
                rel="noopener noreferrer"
                aria-label={`${m.name} paper`}
                className="text-xs text-gray-400 hover:text-blue-500 dark:hover:text-blue-400 transition-colors"
                tabIndex={-1}
              >
                paper ↗
              </a>
            )}
          </div>
          <button
            onClick={() => navigateTo(`#/method/${m.id}`)}
            className="text-xs text-blue-600 dark:text-blue-400 font-medium hover:underline"
            tabIndex={-1}
            aria-label={`View details for ${m.name}`}
          >
            Details →
          </button>
        </div>
      </div>
    </article>
  )
}
