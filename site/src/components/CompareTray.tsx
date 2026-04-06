import { navigateTo } from '../router'
import type { Method } from '../data/schema'

interface CompareTrayProps {
  ids: string[]
  byId: Map<string, Method>
  onRemove: (id: string) => void
  onClear: () => void
}

export function CompareTray({ ids, byId, onRemove, onClear }: CompareTrayProps) {
  if (ids.length === 0) return null

  const compareUrl = `#/compare/${ids.join('/')}`

  return (
    <div
      className="compare-tray"
      role="region"
      aria-label="Compare tray"
      aria-live="polite"
    >
      <div className="mx-auto max-w-screen-2xl px-4 py-3 flex items-center gap-3 flex-wrap">
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300 shrink-0">
          Compare:
        </span>
        <div className="flex flex-wrap gap-2 flex-1">
          {ids.map(id => {
            const m = byId.get(id)
            return (
              <span
                key={id}
                className="inline-flex items-center gap-1 rounded-full bg-gray-100 dark:bg-gray-800
                           px-2.5 py-1 text-xs font-medium text-gray-700 dark:text-gray-300"
              >
                {m?.name ?? id}
                <button
                  onClick={() => onRemove(id)}
                  aria-label={`Remove ${m?.name ?? id} from compare`}
                  className="ml-0.5 text-gray-400 hover:text-red-500 leading-none"
                >
                  ×
                </button>
              </span>
            )
          })}
        </div>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => navigateTo(compareUrl)}
            disabled={ids.length < 2}
            className="btn-primary disabled:opacity-40 disabled:cursor-not-allowed text-xs"
          >
            Compare →
          </button>
          <button onClick={onClear} className="btn-ghost text-xs text-red-500 dark:text-red-400">
            Clear
          </button>
        </div>
      </div>
    </div>
  )
}
