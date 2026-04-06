import { useMemo } from 'react'
import type { Method, Meta } from './schema'
import methodsJson from './methods.json'
import metaJson from './meta.json'

// Cast the imported JSON to typed arrays
const METHODS = methodsJson as Method[]
const META = metaJson as Meta

export function useMethods() {
  const byId = useMemo(() => {
    const map = new Map<string, Method>()
    for (const m of METHODS) map.set(m.id, m)
    return map
  }, [])

  const byCategory = useMemo(() => {
    const map = new Map<string, Method[]>()
    for (const m of METHODS) {
      const list = map.get(m.category) ?? []
      list.push(m)
      map.set(m.category, list)
    }
    return map
  }, [])

  return { methods: METHODS, meta: META, byId, byCategory }
}
