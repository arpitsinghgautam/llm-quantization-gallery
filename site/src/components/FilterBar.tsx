import { useState, useRef, useEffect } from 'react'
import type { FilterState, SortOrder } from '../lib/filters'
import { filterSummary, isDefaultFilters, defaultFilters } from '../lib/filters'
import { categoryColor, CATEGORY_LABELS, CATEGORY_ORDER } from '../lib/categoryColors'
import { ALL_W_BITS, ALL_A_BITS, ALL_KV_BITS } from '../lib/precision'
import type { MetaCategory } from '../data/schema'

interface FilterBarProps {
  filters: FilterState
  sort: SortOrder
  yearMin: number
  yearMax: number
  categories: MetaCategory[]
  total: number
  shown: number
  onChange: (f: FilterState) => void
  onSort: (s: SortOrder) => void
  onReset: () => void
}

function TriState({ value, onChange }: {
  value: 'yes' | 'no' | 'any'
  onChange: (v: 'yes' | 'no' | 'any') => void
}) {
  const cycle = () => {
    const next: Record<string, 'yes' | 'no' | 'any'> = { any: 'yes', yes: 'no', no: 'any' }
    onChange(next[value])
  }
  const label = { any: 'Either', yes: 'Yes', no: 'No' }[value]
  const active = value !== 'any'
  return (
    <button
      onClick={cycle}
      className={`badge cursor-pointer select-none transition-colors ${
        active
          ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
          : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
      }`}
    >
      {label}
    </button>
  )
}

function BitChips({ selected, all, onChange, label }: {
  selected: number[]
  all: number[]
  onChange: (bits: number[]) => void
  label: string
}) {
  const toggle = (bit: number) => {
    onChange(selected.includes(bit) ? selected.filter(b => b !== bit) : [...selected, bit])
  }
  return (
    <div className="flex flex-wrap gap-1 items-center">
      <span className="text-xs text-gray-500 dark:text-gray-400 w-6 shrink-0">{label}</span>
      {all.map(bit => (
        <button
          key={bit}
          onClick={() => toggle(bit)}
          aria-pressed={selected.includes(bit)}
          className={`chip text-xs px-2 py-0.5 ${
            selected.includes(bit)
              ? 'chip-active bg-blue-600 dark:bg-blue-500'
              : 'chip-inactive'
          }`}
        >
          {bit}
        </button>
      ))}
      {selected.length > 0 && (
        <button onClick={() => onChange([])} className="text-xs text-gray-400 hover:text-red-500 ml-1">✕</button>
      )}
    </div>
  )
}

export function FilterBar({
  filters, sort, yearMin, yearMax, categories, total, shown, onChange, onSort, onReset,
}: FilterBarProps) {
  const [localSearch, setLocalSearch] = useState(filters.search)
  const timerRef = useRef<ReturnType<typeof setTimeout>>()
  const isDirty = !isDefaultFilters(filters, yearMin, yearMax)
  const summary = filterSummary(filters, yearMin, yearMax)

  // Keep local search in sync when reset externally
  useEffect(() => {
    setLocalSearch(filters.search)
  }, [filters.search])

  const set = (patch: Partial<FilterState>) => onChange({ ...filters, ...patch })

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setLocalSearch(val)
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => set({ search: val }), 150)
  }

  // Listen for external reset (from empty state button)
  useEffect(() => {
    const handler = () => onReset()
    window.addEventListener('reset-filters', handler)
    return () => window.removeEventListener('reset-filters', handler)
  }, [onReset])

  const toggleCategory = (cat: string) => {
    const cats = filters.categories.includes(cat)
      ? filters.categories.filter(c => c !== cat)
      : [...filters.categories, cat]
    set({ categories: cats })
  }

  return (
    <div className="filter-bar" role="search">
      <form
        className="mx-auto max-w-screen-2xl px-4 py-3 space-y-3"
        onSubmit={e => e.preventDefault()}
        aria-label="Filter methods"
      >
        {/* Row 1: search + sort */}
        <div className="flex gap-3 items-center">
          <div className="relative flex-1 max-w-sm">
            <label htmlFor="search" className="sr-only">Search methods</label>
            <svg className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
            </svg>
            <input
              id="search"
              type="search"
              placeholder="Search methods, authors…"
              value={localSearch}
              onChange={handleSearch}
              className="w-full pl-8 pr-3 py-1.5 text-sm rounded-lg border border-gray-200
                         dark:border-gray-700 bg-white dark:bg-gray-900 text-gray-900
                         dark:text-gray-100 placeholder-gray-400 focus:outline-none
                         focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <label htmlFor="sort" className="sr-only">Sort</label>
          <select
            id="sort"
            value={sort}
            onChange={e => onSort(e.target.value as SortOrder)}
            className="text-sm rounded-lg border border-gray-200 dark:border-gray-700
                       bg-white dark:bg-gray-900 text-gray-700 dark:text-gray-300
                       px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
            <option value="alpha">Alphabetical</option>
            <option value="category">By category</option>
          </select>

          {isDirty && (
            <button type="button" onClick={onReset} className="btn-ghost text-sm text-red-500 dark:text-red-400">
              Reset
            </button>
          )}
        </div>

        {/* Row 2: category chips */}
        <div className="flex flex-wrap gap-1.5" role="group" aria-label="Filter by category">
          {CATEGORY_ORDER.map(cat => {
            const meta = categories.find(c => c.id === cat)
            const active = filters.categories.includes(cat)
            const color = categoryColor(cat)
            return (
              <button
                key={cat}
                type="button"
                onClick={() => toggleCategory(cat)}
                aria-pressed={active}
                className={`chip text-xs ${active ? 'chip-active' : 'chip-inactive'}`}
                style={active ? { backgroundColor: color, color: '#fff' } : {}}
              >
                {CATEGORY_LABELS[cat]} {meta ? `(${meta.count})` : ''}
              </button>
            )
          })}
        </div>

        {/* Row 3: bit filters */}
        <div className="flex flex-wrap gap-x-6 gap-y-2">
          <BitChips label="W" selected={filters.wBits} all={ALL_W_BITS} onChange={v => set({ wBits: v })} />
          <BitChips label="A" selected={filters.aBits} all={ALL_A_BITS} onChange={v => set({ aBits: v })} />
          <BitChips label="KV" selected={filters.kvBits} all={ALL_KV_BITS} onChange={v => set({ kvBits: v })} />
        </div>

        {/* Row 4: toggles + year range */}
        <div className="flex flex-wrap gap-x-6 gap-y-2 items-center text-xs text-gray-600 dark:text-gray-400">
          <div className="flex items-center gap-2">
            <span>Calibration data:</span>
            <TriState value={filters.calibration} onChange={v => set({ calibration: v })} />
          </div>
          <div className="flex items-center gap-2">
            <span>Requires training:</span>
            <TriState value={filters.training} onChange={v => set({ training: v })} />
          </div>
          <div className="flex items-center gap-2">
            <label htmlFor="year-min">Year:</label>
            <input
              id="year-min"
              type="number"
              min={yearMin}
              max={filters.yearMax}
              value={filters.yearMin}
              onChange={e => set({ yearMin: Math.max(yearMin, Number(e.target.value)) })}
              className="w-16 rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900
                         px-1 py-0.5 text-xs text-center focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            <span>–</span>
            <label htmlFor="year-max" className="sr-only">to year</label>
            <input
              id="year-max"
              type="number"
              min={filters.yearMin}
              max={yearMax}
              value={filters.yearMax}
              onChange={e => set({ yearMax: Math.min(yearMax, Number(e.target.value)) })}
              className="w-16 rounded border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900
                         px-1 py-0.5 text-xs text-center focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Results count + active pill summary */}
        <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500 dark:text-gray-400 pt-0.5">
          <span>
            Showing <strong className="text-gray-900 dark:text-white">{shown}</strong> of{' '}
            <strong className="text-gray-900 dark:text-white">{total}</strong> methods
          </span>
          {summary.map(s => (
            <span key={s} className="badge bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              {s}
            </span>
          ))}
        </div>
      </form>
    </div>
  )
}
