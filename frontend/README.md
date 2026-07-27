# BookMe AI — React UI

Week 13–style chat UI (Vite + React + Tailwind), adapted for BookMe travel routes and Clerk auth.

## Setup

```bash
cd frontend
cp .env.example .env
npm install
```

## Run (with API)

Terminal 1:

```bash
make run-api
```

Terminal 2:

```bash
make run-ui
# or: cd frontend && npm run dev
```

Open http://127.0.0.1:5173 — Vite proxies `/api/*` to `VITE_API_URL` (default `http://127.0.0.1:8000`).

## Auth modes

| Mode | Frontend env | API env |
|------|----------------|---------|
| **Local dev** | `VITE_AUTH_DISABLED=true` | `AUTH_DISABLED=1` |
| **Production** | `VITE_AUTH_DISABLED=false`, `VITE_CLERK_PUBLISHABLE_KEY=pk_…` | `AUTH_DISABLED=0`, `CLERK_SECRET_KEY`, `CLERK_AUTHORIZED_PARTIES` |

See [docs/CLERK_SETUP.md](../docs/CLERK_SETUP.md) for Dashboard steps and deploy URLs.

## Structure (from Week 13 `ui/`)

- `src/api/client.ts` — `/chat`, `/chat/stream`, health
- `src/hooks/useChatStream.ts` — SSE chain-of-thought
- `src/hooks/useSessions.ts` — localStorage threads (no DB)
- Same layout: header, sidebar, chat window, status bar
