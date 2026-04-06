import { useEffect, useRef, useState } from 'react'

interface MermaidViewProps {
  /** Either a method id (fetches /assets/mermaid/{id}.mmd) or raw source */
  methodId?: string
  source?: string
  className?: string
}

let mermaidReady = false
let mermaidModule: typeof import('mermaid') | null = null

async function getMermaid() {
  if (!mermaidModule) {
    mermaidModule = await import('mermaid')
    mermaidModule.default.initialize({
      startOnLoad: false,
      theme: document.documentElement.classList.contains('dark') ? 'dark' : 'default',
      securityLevel: 'loose',
      fontFamily: 'system-ui, sans-serif',
    })
    mermaidReady = true
  }
  return mermaidModule
}

let idCounter = 0

export function MermaidView({ methodId, source, className }: MermaidViewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const idRef = useRef(`mermaid-${++idCounter}`)

  useEffect(() => {
    let cancelled = false

    async function render() {
      setLoading(true)
      setError(null)

      try {
        let src = source

        if (!src && methodId) {
          const url = `${import.meta.env.BASE_URL}assets/mermaid/${methodId}.mmd`
          const res = await fetch(url)
          if (!res.ok) throw new Error(`Could not load diagram (${res.status})`)
          src = await res.text()
        }

        if (!src) { setLoading(false); return }

        const mermaid = await getMermaid()
        if (cancelled) return

        const id = idRef.current
        const { svg } = await mermaid.default.render(id, src.trim())

        if (cancelled) return
        if (containerRef.current) {
          containerRef.current.innerHTML = svg
        }
        setLoading(false)
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : String(e))
          setLoading(false)
        }
      }
    }

    render()
    return () => { cancelled = true }
  }, [methodId, source])

  if (loading) {
    return (
      <div className={`flex items-center justify-center h-32 text-sm text-gray-400 ${className}`}>
        Loading diagram…
      </div>
    )
  }

  if (error) {
    return (
      <div className={`rounded border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-900/10
                       px-4 py-3 text-xs text-red-700 dark:text-red-400 ${className}`}>
        Mermaid error: {error}
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className={`mermaid-wrapper overflow-x-auto ${className ?? ''}`}
      aria-label="Method flowchart diagram"
    />
  )
}
