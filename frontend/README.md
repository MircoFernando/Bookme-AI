# BookMe AI — React UI

BookMe AI chat UI (Vite + React + Tailwind) with travel routes and Clerk auth.

Full local setup (API + env + Docker): see the root [README.md](../README.md#getting-started).

## One-time setup (from repo root)

```bash
make setup
cp .env.example .env
cp frontend/.env.example frontend/.env
# edit both .env files (keys + auth mode)
```

## Run locally (two terminals, repo root)

Terminal 1:

```bash
source .venv/bin/activate
make run-api
```

Terminal 2:

```bash
make run-ui
```

Open http://127.0.0.1:5173 — landing at `/`, chat at `/app`. Vite proxies `/api/*` to `VITE_API_URL` (default `http://127.0.0.1:8000`).

## Auth modes

| Mode | Frontend env | API env |
|------|----------------|---------|
| **Local dev** | `VITE_AUTH_DISABLED=true` | `AUTH_DISABLED=1` |
| **Production** | `VITE_AUTH_DISABLED=false`, `VITE_CLERK_PUBLISHABLE_KEY=pk_…` | `AUTH_DISABLED=0`, `CLERK_SECRET_KEY`, `CLERK_AUTHORIZED_PARTIES` |

See [docs/CLERK_SETUP.md](../docs/CLERK_SETUP.md) for Dashboard steps and deploy URLs.

## Deploy (Vercel)

1. Import repo → set **Root Directory** to `frontend`.
2. Production env: `VITE_API_URL=https://<your-render-service>.onrender.com`, Clerk keys as above.
3. Full checklist: [docs/DEPLOY_RENDER_VERCEL.md](../docs/DEPLOY_RENDER_VERCEL.md).

## Structure

- `/` — marketing landing (Clerk Sign in / Get started → redirect back to `/`)
- `/app` — chat assistant (requires sign-in when Clerk is enabled)
- `src/api/client.ts` — `/chat`, `/chat/stream`, health
- `src/hooks/useChatStream.ts` — SSE chain-of-thought
- `src/hooks/useSessions.ts` — localStorage threads (no DB)
