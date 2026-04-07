import { useEffect, useRef, useState } from 'react'

interface MermaidViewProps {
  methodId?: string   // shows pre-rendered SVG from assets/mermaid-rendered/
  source?: string     // raw mermaid source — rendered client-side (lineage graph only)
  className?: string
}

// ── Pre-rendered static SVG (used for all method flowcharts) ─────────────────
function StaticMermaid({ methodId, className }: { methodId: string; className?: string }) {
  const url = `${import.meta.env.BASE_URL}assets/mermaid-rendered/${methodId}.svg`
  return (
    <img
      src={url}
      alt={`${methodId} flowchart`}
      className={`w-full h-auto ${className ?? ''}`}
    />
  )
}

// ── Dynamic renderer — only used for lineage mini-graphs (raw source) ─────────
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
  }
  return mermaidModule
}

let idCounter = 0

function DynamicMermaid({ source, className }: { source: string; className?: string }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [error, setError]     = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const idRef = useRef(`mermaid-${++idCounter}`)

  useEffect(() => {
    let cancelled = false
    async function render() {
      setLoading(true)
      setError(null)
      try {
        const mermaid = await getMermaid()
        if (cancelled) return
        const { svg } = await mermaid.default.render(idRef.current, source.trim())
        if (cancelled) return
        if (containerRef.current) containerRef.current.innerHTML = svg
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
  }, [source])

  if (loading) return (
    <div className={`flex items-center justify-center h-24 text-sm text-gray-400 ${className}`}>
      Loading…
    </div>
  )
  if (error) return null

  return (
    <div
      ref={containerRef}
      className={`mermaid-wrapper overflow-x-auto ${className ?? ''}`}
      aria-label="Lineage diagram"
    />
  )
}

// ── Public component ──────────────────────────────────────────────────────────
export function MermaidView({ methodId, source, className }: MermaidViewProps) {
  if (methodId) return <StaticMermaid methodId={methodId} className={className} />
  if (source)   return <DynamicMermaid source={source} className={className} />
  return null
}
