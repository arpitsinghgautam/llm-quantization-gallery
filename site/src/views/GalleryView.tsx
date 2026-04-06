import { useState, useMemo, useCallback, useEffect } from 'react'
import { useMethods } from '../data/useMethods'
import { FilterBar } from '../components/FilterBar'
import { MethodGrid } from '../components/MethodGrid'
import { CompareTray } from '../components/CompareTray'
import { applyFilters, defaultFilters, FilterState, SortOrder } from '../lib/filters'
import { navigateTo } from '../router'

const SESSION_KEY = 'qgallery:compare'

function loadCompare(): string[] {
  try {
    return JSON.parse(sessionStorage.getItem(SESSION_KEY) ?? '[]')
  } catch { return [] }
}

function saveCompare(ids: string[]) {
  sessionStorage.setItem(SESSION_KEY, JSON.stringify(ids))
}

export function GalleryView() {
  const { methods, meta, byId } = useMethods()

  const yearMin = useMemo(() => Math.min(...methods.map(m => m.year)), [methods])
  const yearMax = useMemo(() => Math.max(...methods.map(m => m.year)), [methods])

  const [filters, setFilters] = useState<FilterState>(() => {
    const jumpCat = sessionStorage.getItem('qgallery:jump-category')
    if (jumpCat) {
      sessionStorage.removeItem('qgallery:jump-category')
      return { ...defaultFilters(yearMin, yearMax), categories: [jumpCat] }
    }
    return defaultFilters(yearMin, yearMax)
  })
  const [sort, setSort] = useState<SortOrder>('newest')
  const [compareIds, setCompareIds] = useState<string[]>(loadCompare)

  useEffect(() => { saveCompare(compareIds) }, [compareIds])

  const filtered = useMemo(
    () => applyFilters(methods, filters, sort),
    [methods, filters, sort],
  )

  const handleReset = useCallback(() => {
    setFilters(defaultFilters(yearMin, yearMax))
    setSort('newest')
  }, [yearMin, yearMax])

  const handleCompareToggle = useCallback((id: string) => {
    setCompareIds(prev => {
      if (prev.includes(id)) return prev.filter(x => x !== id)
      if (prev.length >= 4) return prev
      return [...prev, id]
    })
  }, [])

  return (
    <>
      {/* Sticky filter bar */}
      <FilterBar
        filters={filters}
        sort={sort}
        yearMin={yearMin}
        yearMax={yearMax}
        categories={meta.categories}
        total={methods.length}
        shown={filtered.length}
        onChange={setFilters}
        onSort={setSort}
        onReset={handleReset}
      />

      {/* Main content */}
      <main className="mx-auto max-w-screen-2xl px-4 py-6">
        {/* Intro */}
        <div className="mb-8 max-w-2xl">
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">
            A curated, filterable reference for LLM quantization methods — {meta.count} entries across{' '}
            {meta.categories.length} categories, each with a fact sheet, SVG diagram, and Mermaid flowchart.
            Generated from{' '}
            <code className="text-xs bg-gray-100 dark:bg-gray-800 px-1 rounded">methods.yml</code>{' '}
            · last updated {meta.lastUpdated}.
          </p>
          <div className="mt-3 rounded-lg border border-blue-100 dark:border-blue-900/50
                          bg-blue-50 dark:bg-blue-900/20 px-4 py-2.5 text-sm text-blue-800 dark:text-blue-200">
            New here? Start with the{' '}
            <button onClick={() => navigateTo('#/docs/notation')} className="underline font-medium">
              notation guide
            </button>{' '}
            and the{' '}
            <button onClick={() => navigateTo('#/docs/glossary')} className="underline font-medium">
              glossary
            </button>.
          </div>
        </div>

        <MethodGrid
          methods={filtered}
          total={methods.length}
          compareSet={new Set(compareIds)}
          onCompareToggle={handleCompareToggle}
        />
      </main>

      {/* Compare tray */}
      {compareIds.length > 0 && (
        <div className="pb-16">
          <CompareTray
            ids={compareIds}
            byId={byId}
            onRemove={id => setCompareIds(prev => prev.filter(x => x !== id))}
            onClear={() => setCompareIds([])}
          />
        </div>
      )}

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-6 text-center text-xs
                         text-gray-400 dark:text-gray-600">
        Generated from methods.yml · {meta.count} methods · last updated {meta.lastUpdated}
      </footer>
    </>
  )
}
