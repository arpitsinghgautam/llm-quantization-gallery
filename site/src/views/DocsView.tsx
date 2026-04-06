import { MarkdownView } from '../components/MarkdownView'
import { navigateTo } from '../router'

const PAGES: Record<string, { title: string; file: string }> = {
  notation: { title: 'Notation Guide', file: 'notation.md' },
  glossary: { title: 'Glossary', file: 'glossary.md' },
  timeline: { title: 'Timeline', file: 'timeline.md' },
}

interface DocsViewProps {
  page: string
}

export function DocsView({ page }: DocsViewProps) {
  const meta = PAGES[page]

  if (!meta) {
    return (
      <main className="mx-auto max-w-screen-2xl px-4 py-16 text-center">
        <p className="text-gray-500 dark:text-gray-400 mb-4">
          Page <code className="text-sm bg-gray-100 dark:bg-gray-800 px-1 rounded">{page}</code> not found.
        </p>
        <button onClick={() => navigateTo('#/')} className="btn-primary">← Gallery</button>
      </main>
    )
  }

  const url = `${import.meta.env.BASE_URL}docs/${meta.file}`

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      {/* Breadcrumb */}
      <nav aria-label="Breadcrumb" className="text-xs text-gray-500 dark:text-gray-400 mb-6 flex items-center gap-1">
        <button onClick={() => navigateTo('#/')} className="hover:text-blue-600 dark:hover:text-blue-400">
          Gallery
        </button>
        <span>/</span>
        <span className="text-gray-700 dark:text-gray-300">{meta.title}</span>
      </nav>

      <MarkdownView url={url} className="max-w-none" />

      {/* Doc navigation */}
      <div className="mt-10 pt-6 border-t border-gray-200 dark:border-gray-800 flex flex-wrap gap-3 text-sm">
        {Object.entries(PAGES).filter(([k]) => k !== page).map(([k, v]) => (
          <button
            key={k}
            onClick={() => navigateTo(`#/docs/${k}`)}
            className="btn-ghost text-sm"
          >
            {v.title} →
          </button>
        ))}
        <button onClick={() => navigateTo('#/')} className="btn-ghost text-sm">← Gallery</button>
      </div>
    </main>
  )
}
