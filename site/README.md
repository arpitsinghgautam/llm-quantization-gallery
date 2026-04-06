# LLM Quantization Gallery — Website

Interactive visual gallery for [LLM Quantization Gallery](../README.md).
Built with Vite + React + TypeScript + Tailwind CSS. Deployed to GitHub Pages.

Live site: **https://arpitsinghgautam.github.io/quantization_gallery/**

## Prerequisites

- [Node.js](https://nodejs.org/) v18 or newer (includes npm)
- The repo root's `methods.yml`, `assets/`, and `docs/` must exist

## Development

```bash
# From the repo root, cd into the site directory
cd site

# Install dependencies (first time only)
npm install

# Start the dev server (auto-runs the YAML→JSON converter first)
npm run dev
```

The dev server runs at `http://localhost:5173/quantization_gallery/`.

Whenever you edit `methods.yml` at the repo root, restart the dev server — the
`predev` script re-runs `scripts/yaml-to-json.mjs` automatically.

## Production build

```bash
npm run build
# Output in site/dist/
```

Preview the production build locally:
```bash
npm run preview
```

## Deployment

### Automatic (recommended)

Push to `main` any change under `methods.yml`, `assets/`, `docs/`, or `site/`.
The GitHub Actions workflow at `.github/workflows/deploy-site.yml` builds and
deploys automatically.

**Required one-time setup in the repo:**
1. Settings → Pages → Source: **GitHub Actions**
2. Settings → Pages → Custom domain: (optional)

### Manual fallback

```bash
npm run build && node scripts/deploy.mjs
```

This pushes `site/dist/` to the `gh-pages` branch.

## Adding a new quantization method

1. Edit `methods.yml` at the **repo root** (not inside `site/`).
2. Run `python scripts/generate_diagrams.py --id <your-id>` to generate the SVG.
3. Run `python scripts/generate_mermaid.py --id <your-id>` to generate the `.mmd`.
4. Run `python scripts/build_readme.py` to regenerate `README.md`.
5. Restart the dev server (`npm run dev`) — the site picks up the new method automatically.

## Running tests

```bash
npm test
```

Tests cover `precision.ts` (parsing precision strings) and `filters.ts` (filter/sort pipeline).

## File layout

```
site/
├── scripts/
│   ├── yaml-to-json.mjs   ← converts methods.yml → src/data/methods.json + copies assets
│   └── deploy.mjs         ← manual deploy fallback
├── src/
│   ├── data/
│   │   ├── schema.ts      ← Zod schema + TypeScript types
│   │   ├── useMethods.ts  ← data hook
│   │   ├── methods.json   ← generated (gitignored)
│   │   └── meta.json      ← generated (gitignored)
│   ├── lib/
│   │   ├── categoryColors.ts
│   │   ├── precision.ts   ← parses "W4A16KV4" → {wBits, aBits, kvBits}
│   │   └── filters.ts     ← pure filter/sort functions
│   ├── components/        ← reusable UI
│   ├── views/             ← page-level views (Gallery, Method, Compare, Docs)
│   └── router.ts          ← tiny hash router (~30 lines)
└── public/
    ├── assets/            ← copied from repo root (gitignored)
    └── docs/              ← copied from repo root (gitignored)
```

## Architecture notes

- **No backend.** Everything is static — `methods.yml` is the source of truth, converted to JSON at build time.
- **Hash routing** (`#/method/gptq`, `#/compare/gptq/awq`) — works on GitHub Pages without SPA rewrites.
- **Mermaid is lazy-loaded** — only imported on the method detail view, not the gallery index.
- **System font stack** — no web fonts, no Google Fonts.
- **Dark mode** — respects `prefers-color-scheme` on first visit, then persists to `localStorage`.
