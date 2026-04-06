/**
 * deploy.mjs — local fallback deployment to gh-pages branch.
 * Preferred path: GitHub Actions workflow (.github/workflows/deploy-site.yml).
 *
 * Usage: node scripts/deploy.mjs
 */

import { execSync } from 'child_process'
import { resolve, dirname } from 'path'
import { fileURLToPath } from 'url'
import ghPages from 'gh-pages'

const __dir = dirname(fileURLToPath(import.meta.url))
const SITE  = resolve(__dir, '..')
const DIST  = resolve(SITE, 'dist')

console.log('[deploy] Building site...')
execSync('npm run build', { cwd: SITE, stdio: 'inherit' })

console.log('[deploy] Publishing dist/ to gh-pages branch...')
ghPages.publish(DIST, {
  branch: 'gh-pages',
  message: 'chore: deploy site [skip ci]',
}, (err) => {
  if (err) { console.error('[deploy] Failed:', err); process.exit(1) }
  console.log('[deploy] Done. Check your repo\'s GitHub Pages settings.')
})
