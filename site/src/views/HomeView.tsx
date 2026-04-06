import { useMethods } from '../data/useMethods'
import { navigateTo } from '../router'

const CATEGORY_ORDER = [
  'ptq_weight_only',
  'ptq_weight_activation',
  'qat',
  'extreme_lowbit',
  'kv_cache',
  'low_precision_training',
  'moe',
  'systems',
]

const CATEGORY_LABEL: Record<string, string> = {
  ptq_weight_only:        'PTQ W-only',
  ptq_weight_activation:  'PTQ W+A',
  qat:                    'QAT / QFT',
  extreme_lowbit:         'Sub-2-bit',
  kv_cache:               'KV Quant',
  low_precision_training: 'LP Training',
  moe:                    'MoE Quant',
  systems:                'Systems',
}

const GITHUB_URL = 'https://github.com/arpitsinghgautam/llm-quantization-gallery'

export function HomeView() {
  const { methods, meta } = useMethods()

  const sorted = [...methods].sort((a, b) => {
    const ai = CATEGORY_ORDER.indexOf(a.category)
    const bi = CATEGORY_ORDER.indexOf(b.category)
    if (ai !== bi) return ai - bi
    return a.name.localeCompare(b.name)
  })

  return (
    <main className="mx-auto max-w-5xl px-4 py-10">
      {/* Title */}
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-1">
        LLM Quantization Gallery
      </h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
        Last updated {meta.lastUpdated} ·{' '}
        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
          className="underline hover:text-blue-600 dark:hover:text-blue-400">
          GitHub
        </a>
      </p>

      {/* Description */}
      <p className="text-gray-700 dark:text-gray-300 mb-3 leading-relaxed max-w-2xl">
        This page collects fact sheets and flowchart diagrams for LLM quantization methods.
        Click a diagram to open its full detail card, or use the gallery to filter and compare.
        If you spot an error or a missing method, please{' '}
        <a href={`${GITHUB_URL}/issues`} target="_blank" rel="noopener noreferrer"
          className="underline hover:text-blue-600 dark:hover:text-blue-400">
          file an issue
        </a>.
      </p>

      {/* Browse button */}
      <button
        onClick={() => navigateTo('#/gallery')}
        className="mb-10 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
      >
        Browse &amp; filter all {meta.count} methods →
      </button>

      {/* Thumbnail grid — grouped by category */}
      {CATEGORY_ORDER.map(cat => {
        const catMethods = sorted.filter(m => m.category === cat)
        if (!catMethods.length) return null
        return (
          <section key={cat} className="mb-10">
            <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-3">
              {CATEGORY_LABEL[cat]} — {catMethods.length}
            </h2>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-3">
              {catMethods.map(m => (
                <button
                  key={m.id}
                  onClick={() => navigateTo(`#/method/${m.id}`)}
                  className="group flex flex-col items-center gap-1 text-center hover:opacity-80 transition-opacity"
                  title={m.name}
                >
                  {m.diagram ? (
                    <img
                      src={m.diagram}
                      alt={m.name}
                      className="w-full rounded border border-gray-200 dark:border-gray-700 bg-white"
                      loading="lazy"
                    />
                  ) : (
                    <div className="w-full aspect-[4/3] rounded border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 flex items-center justify-center text-xs text-gray-400">
                      {m.name}
                    </div>
                  )}
                  <span className="text-[11px] text-gray-600 dark:text-gray-400 leading-tight group-hover:text-blue-600 dark:group-hover:text-blue-400">
                    {m.name}
                  </span>
                </button>
              ))}
            </div>
          </section>
        )
      })}
    </main>
  )
}
