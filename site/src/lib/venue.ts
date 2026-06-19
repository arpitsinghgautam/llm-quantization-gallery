// Helpers for displaying publication / acceptance status.
// Three states per method:
//   - accepted at a real venue (conference / journal)
//   - arXiv preprint (has an arXiv paper but no venue yet)
//   - no paper (software / tool / baseline with only a repo)

export function isAcceptedVenue(venue?: string | null): boolean {
  if (!venue) return false
  const v = venue.trim().toLowerCase()
  return v !== '' && v !== 'null' && !v.startsWith('arxiv')
}

function isArxiv(paperUrl?: string | null): boolean {
  return !!paperUrl && /arxiv\.org/i.test(paperUrl)
}

/** Full label for fact sheets. */
export function publicationLabel(venue?: string | null, paperUrl?: string | null): string {
  if (isAcceptedVenue(venue)) return (venue as string).trim()
  if (isArxiv(paperUrl)) return 'arXiv (preprint)'
  return 'n/a (no paper)'
}

/** Compact label for badges. */
export function venueShort(venue?: string | null, paperUrl?: string | null): string {
  if (isAcceptedVenue(venue)) return (venue as string).split('(')[0].trim()
  if (isArxiv(paperUrl)) return 'arXiv'
  return 'n/a'
}
