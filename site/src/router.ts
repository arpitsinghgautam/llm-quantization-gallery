import { useState, useEffect } from 'react'

export type Route =
  | { view: 'home' }
  | { view: 'gallery' }
  | { view: 'method'; id: string }
  | { view: 'compare'; ids: string[] }
  | { view: 'docs'; page: string }

function parseHash(hash: string): Route {
  const path = hash.replace(/^#\/?/, '') || ''
  if (!path || path === '/') return { view: 'home' }

  const parts = path.split('/').filter(Boolean)

  if (parts[0] === 'gallery') return { view: 'gallery' }
  if (parts[0] === 'method' && parts[1]) {
    return { view: 'method', id: parts[1] }
  }
  if (parts[0] === 'compare' && parts.length >= 2) {
    return { view: 'compare', ids: parts.slice(1).slice(0, 4) }
  }
  if (parts[0] === 'docs' && parts[1]) {
    return { view: 'docs', page: parts[1] }
  }

  return { view: 'home' }
}

export function useRouter(): [Route, (hash: string) => void] {
  const [route, setRoute] = useState<Route>(() => parseHash(window.location.hash))

  useEffect(() => {
    const onHash = () => setRoute(parseHash(window.location.hash))
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const navigate = (hash: string) => {
    window.location.hash = hash
  }

  return [route, navigate]
}

export function navigateTo(hash: string) {
  window.location.hash = hash
}
