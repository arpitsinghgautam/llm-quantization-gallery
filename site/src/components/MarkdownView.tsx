import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { MermaidView } from './MermaidView'

interface MarkdownViewProps {
  url: string
  className?: string
}

export function MarkdownView({ url, className }: MarkdownViewProps) {
  const [content, setContent] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetch(url)
      .then(r => {
        if (!r.ok) throw new Error(`Failed to fetch: ${r.status}`)
        return r.text()
      })
      .then(text => { if (!cancelled) setContent(text) })
      .catch(e => { if (!cancelled) setError(String(e)) })
    return () => { cancelled = true }
  }, [url])

  if (error) {
    return (
      <div className="text-sm text-red-600 dark:text-red-400 py-8 text-center">
        Could not load document: {error}
      </div>
    )
  }

  if (content === null) {
    return (
      <div className="flex items-center justify-center py-16 text-sm text-gray-400">
        Loading…
      </div>
    )
  }

  const base = import.meta.env.BASE_URL

  return (
    <div className={`prose dark:prose-invert max-w-none ${className ?? ''}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Rewrite relative ../assets/ paths to BASE_URL
          img({ src, alt }) {
            const resolved = src?.startsWith('../assets/')
              ? base + src.replace('../assets/', 'assets/')
              : src
            return <img src={resolved} alt={alt ?? ''} className="w-full h-auto" />
          },
          // Render mermaid fenced code blocks with MermaidView
          code({ node, className: cls, children, ...props }) {
            const lang = /language-(\w+)/.exec(cls ?? '')?.[1]
            if (lang === 'mermaid') {
              return <MermaidView source={String(children).trim()} className="my-4" />
            }
            return (
              <code className={cls} {...props}>
                {children}
              </code>
            )
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
