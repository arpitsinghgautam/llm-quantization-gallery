import type { Method } from '../data/schema'
import { parsePrecision, bitsMatch } from './precision'
import { CATEGORY_ORDER } from './categoryColors'

export interface FilterState {
  categories: string[]
  wBits: number[]
  aBits: number[]
  kvBits: number[]          // numeric selected
  kvNa: boolean             // include methods with no KV bits
  calibration: 'yes' | 'no' | 'any'
  training: 'yes' | 'no' | 'any'
  yearMin: number
  yearMax: number
  search: string
}

export type SortOrder = 'newest' | 'oldest' | 'alpha' | 'category'

export function defaultFilters(yearMin: number, yearMax: number): FilterState {
  return {
    categories: [],
    wBits: [],
    aBits: [],
    kvBits: [],
    kvNa: true,
    calibration: 'any',
    training: 'any',
    yearMin,
    yearMax,
    search: '',
  }
}

export function applyFilters(
  methods: Method[],
  filters: FilterState,
  sort: SortOrder,
): Method[] {
  let result = methods.filter(m => matchesFilters(m, filters))
  result = sortMethods(result, sort)
  return result
}

function matchesFilters(m: Method, f: FilterState): boolean {
  // Category filter
  if (f.categories.length > 0 && !f.categories.includes(m.category)) return false

  // Precision filters
  const parsed = parsePrecision(m.precision)

  if (f.wBits.length > 0 && !bitsMatch(parsed.wBits, f.wBits)) return false

  if (f.aBits.length > 0 && !bitsMatch(parsed.aBits, f.aBits)) return false

  if (f.kvBits.length > 0 || !f.kvNa) {
    const hasKv = parsed.kvBits.length > 0
    if (!hasKv && !f.kvNa) return false
    if (hasKv && f.kvBits.length > 0 && !bitsMatch(parsed.kvBits, f.kvBits)) return false
  }

  // Calibration filter
  if (f.calibration !== 'any') {
    const want = f.calibration === 'yes'
    if (m.requires_calibration_data !== want) return false
  }

  // Training filter
  if (f.training !== 'any') {
    const want = f.training === 'yes'
    if (m.requires_training !== want) return false
  }

  // Year range
  if (m.year < f.yearMin || m.year > f.yearMax) return false

  // Text search
  if (f.search) {
    const q = f.search.toLowerCase()
    const searchable = [m.name, m.full_name, m.tldr, m.key_idea, m.authors.join(' ')].join(' ').toLowerCase()
    if (!searchable.includes(q)) return false
  }

  return true
}

function sortMethods(methods: Method[], sort: SortOrder): Method[] {
  const arr = [...methods]
  switch (sort) {
    case 'newest':
      return arr.sort((a, b) => b.year - a.year || a.name.localeCompare(b.name))
    case 'oldest':
      return arr.sort((a, b) => a.year - b.year || a.name.localeCompare(b.name))
    case 'alpha':
      return arr.sort((a, b) => a.name.localeCompare(b.name))
    case 'category':
      return arr.sort((a, b) => {
        const ai = CATEGORY_ORDER.indexOf(a.category)
        const bi = CATEGORY_ORDER.indexOf(b.category)
        return (ai - bi) || a.year - b.year
      })
    default:
      return arr
  }
}

/** Returns a human-readable summary of active filters. */
export function filterSummary(f: FilterState, totalYearMin: number, totalYearMax: number): string[] {
  const parts: string[] = []
  if (f.categories.length > 0) parts.push(f.categories.map(c => c.replace(/_/g, ' ')).join(', '))
  if (f.wBits.length > 0) parts.push(`W${f.wBits.join('/')}`)
  if (f.aBits.length > 0) parts.push(`A${f.aBits.join('/')}`)
  if (f.kvBits.length > 0) parts.push(`KV${f.kvBits.join('/')}`)
  if (f.calibration !== 'any') parts.push(`calib: ${f.calibration}`)
  if (f.training !== 'any') parts.push(`training: ${f.training}`)
  if (f.yearMin !== totalYearMin || f.yearMax !== totalYearMax) {
    parts.push(`${f.yearMin}–${f.yearMax}`)
  }
  if (f.search) parts.push(`"${f.search}"`)
  return parts
}

export function isDefaultFilters(f: FilterState, totalYearMin: number, totalYearMax: number): boolean {
  return (
    f.categories.length === 0 &&
    f.wBits.length === 0 &&
    f.aBits.length === 0 &&
    f.kvBits.length === 0 &&
    f.kvNa &&
    f.calibration === 'any' &&
    f.training === 'any' &&
    f.yearMin === totalYearMin &&
    f.yearMax === totalYearMax &&
    f.search === ''
  )
}
