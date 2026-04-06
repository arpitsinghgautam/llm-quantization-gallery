import type { Method } from '../data/schema'
import { MethodCard } from './MethodCard'
import { navigateTo } from '../router'

interface MethodGridProps {
  methods: Method[]
  total: number
  compareSet: Set<string>
  onCompareToggle: (id: string) => void
}

export function MethodGrid({ methods, total, compareSet, onCompareToggle }: MethodGridProps) {
  if (methods.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 text-center">
        <p className="text-lg text-gray-500 dark:text-gray-400 mb-4">
          No methods match your filters.
        </p>
        <button
          onClick={() => window.dispatchEvent(new CustomEvent('reset-filters'))}
          className="btn-primary"
        >
          Reset filters
        </button>
      </div>
    )
  }

  const compareDisabled = compareSet.size >= 4

  return (
    <div
      className="grid gap-4
        grid-cols-1
        sm:grid-cols-2
        lg:grid-cols-3
        2xl:grid-cols-4"
      role="list"
      aria-label={`${methods.length} of ${total} methods`}
    >
      {methods.map(m => (
        <div key={m.id} role="listitem">
          <MethodCard
            method={m}
            inCompare={compareSet.has(m.id)}
            onCompareToggle={onCompareToggle}
            compareDisabled={compareDisabled}
          />
        </div>
      ))}
    </div>
  )
}
