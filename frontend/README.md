# VidDownAI Frontend

Vue 3 + Vite SPA for VidDownAI video downloader & AI summarizer.

## Commands

```bash
npm install        # Install dependencies
npm run dev        # Dev server → localhost:5173
npm run build      # Production build → dist/
```

## Stack

- Vue 3 (Composition API, `<script setup>`)
- TailwindCSS 4
- Axios (HTTP + SSE streaming)
- marked (Markdown rendering)
- markmap (interactive mindmap SVG)

## Proxy

Vite dev server proxies `/api/*` to `http://localhost:8000` (Flask backend).
