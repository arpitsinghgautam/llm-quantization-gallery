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
    <main className="mx-auto max-w-4xl px-4 py-12">

      {/* ── Author header ── */}
      <div className="mb-10 text-center">
        <a
          href="https://arpitsinghgautam.me/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-2xl font-bold text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
        >
          Arpit Singh Gautam
        </a>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-3">
          Data Scientist · Researcher
        </p>
        {/* Social icons row */}
        <div className="flex items-center justify-center gap-4 text-gray-500 dark:text-gray-400">
          {/* Website */}
          <a href="https://arpitsinghgautam.me/" target="_blank" rel="noopener noreferrer"
            title="Website" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
            </svg>
          </a>
          {/* Google Scholar */}
          <a href="https://scholar.google.com/citations?hl=en&user=BqFcF_IAAAAJ" target="_blank" rel="noopener noreferrer"
            title="Google Scholar" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 24a7 7 0 1 1 0-14 7 7 0 0 1 0 14zm0-24L0 9.5l4.838 3.94A8 8 0 0 1 12 10a8 8 0 0 1 7.162 3.44L24 9.5 12 0z"/>
            </svg>
          </a>
          {/* GitHub */}
          <a href="https://github.com/arpitsinghgautam" target="_blank" rel="noopener noreferrer"
            title="GitHub" className="hover:text-gray-900 dark:hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
            </svg>
          </a>
          {/* LinkedIn */}
          <a href="https://linkedin.com/in/arpitsinghgautam" target="_blank" rel="noopener noreferrer"
            title="LinkedIn" className="hover:text-blue-700 dark:hover:text-blue-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
          </a>
          {/* Twitter / X */}
          <a href="https://twitter.com/Asg_Wolverine" target="_blank" rel="noopener noreferrer"
            title="Twitter / X" className="hover:text-gray-900 dark:hover:text-white transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.253 5.622 5.91-5.622zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
            </svg>
          </a>
          {/* Email */}
          <a href="mailto:arpitsinghgautam777@gmail.com"
            title="Email" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
          </a>
        </div>
      </div>

      {/* ── Page title ── */}
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white text-center mb-2">
        LLM Quantization Gallery
      </h1>

      {/* ── Meta line ── */}
      <p className="text-sm text-center text-gray-500 dark:text-gray-400 mb-6">
        Last updated: {meta.lastUpdated} ·{' '}
        <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer"
          className="underline-offset-2 hover:underline hover:text-blue-600 dark:hover:text-blue-400">
          view changes
        </a>
      </p>

      {/* ── Description ── */}
      <div className="max-w-2xl mx-auto mb-4 space-y-3 text-gray-700 dark:text-gray-300 leading-relaxed">
        <p>
          This page collects fact sheets and flowchart diagrams for LLM quantization methods —
          every major algorithm from 2022 to the present, organized by category, with consistent
          precision specs, architecture diagrams, and cross-references. Click a diagram to open
          its full detail card, or use the{' '}
          <button onClick={() => navigateTo('#/gallery')}
            className="underline hover:text-blue-600 dark:hover:text-blue-400">
            interactive gallery
          </button>{' '}
          to filter and compare methods.
        </p>
        <p>
          I built this while working on{' '}
          <a href="https://arxiv.org/abs/2503.00595" target="_blank" rel="noopener noreferrer"
            className="underline hover:text-blue-600 dark:hover:text-blue-400">
            RAMP
          </a>
          , a mixed-precision quantization method that assigns per-layer bit-widths by retrieving
          from a sensitivity database — without per-model re-optimization. Surveying the landscape
          for related work, I kept wishing a reference like Sebastian Raschka's{' '}
          <a href="https://github.com/rasbt/llm-architecture-gallery" target="_blank" rel="noopener noreferrer"
            className="underline hover:text-blue-600 dark:hover:text-blue-400">
            LLM Architecture Gallery
          </a>{' '}
          existed for quantization methods. So I made one.
        </p>
        <p>
          If you spot an inaccurate entry, a missing method, or a broken link, please{' '}
          <a href={`${GITHUB_URL}/issues`} target="_blank" rel="noopener noreferrer"
            className="underline hover:text-blue-600 dark:hover:text-blue-400">
            file an issue
          </a>.
        </p>
      </div>

      {/* ── Browse button ── */}
      <div className="text-center mb-12">
        <button
          onClick={() => navigateTo('#/gallery')}
          className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Browse &amp; filter all {meta.count} methods →
        </button>
      </div>

      {/* ── Thumbnail grid grouped by category ── */}
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
