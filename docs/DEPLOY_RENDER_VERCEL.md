# Deploy BookMe AI on Render + Vercel (free tier)

Split layout:

| Piece | Platform | URL |
|--------|-----------|-----|
| FastAPI + MCP | **Render** web service (Docker) | `https://bookme-ai-api.onrender.com` |
| React UI | **Vercel** (static Vite build) | `https://your-project.vercel.app` |

The UI calls the API directly in production (`VITE_API_URL` at build time). Enable CORS and Clerk on the API for your Vercel origin.

---

## 1. Render — API

1. Push this repo to GitHub.
2. [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint** → select the repo (uses root `render.yaml`).
3. When prompted, set **secret** env vars (at minimum):
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY`
   - `CLERK_SECRET_KEY`
   - `GOOGLE_API_KEY` (if merge route uses Gemini)
4. After the first deploy, copy the service URL (e.g. `https://bookme-ai-api.onrender.com`).
5. Set on Render (replace with your real Vercel URL once it exists):
   - `CORS_ORIGINS` = `https://your-project.vercel.app,https://your-project-*.vercel.app`
   - `CLERK_AUTHORIZED_PARTIES` = same list (Clerk JWT `azp` / authorized parties)

**Notes**

- **Free plan** spins down when idle; first request after sleep can take 30–60s (MCP warmup).
- Health check uses `/ready` (MCP tools loaded).
- Optional: set `AUTH_DISABLED=1` on Render and `VITE_AUTH_DISABLED=true` on Vercel for a no-Clerk demo (not for production).

---

## 2. Vercel — frontend

1. [Vercel Dashboard](https://vercel.com/new) → import the same GitHub repo.
2. **Root Directory:** `frontend` (required).
3. Framework preset: **Vite** (or use existing `frontend/vercel.json`).
4. **Environment variables** (Production):

   | Name | Example |
   |------|---------|
   | `VITE_API_URL` | `https://bookme-ai-api.onrender.com` |
   | `VITE_CLERK_PUBLISHABLE_KEY` | `pk_live_…` or `pk_test_…` |
   | `VITE_AUTH_DISABLED` | `false` |

5. Deploy. Open the Vercel URL and test chat (SSE).

6. Update Render `CORS_ORIGINS` and `CLERK_AUTHORIZED_PARTIES` with the final Vercel URL if you used a placeholder.

**Clerk**

- Add Vercel URLs under Clerk → **Domains** / **Allowed origins** as in [CLERK_SETUP.md](./CLERK_SETUP.md).

---

## 3. Verify

```bash
curl -sS "https://bookme-ai-api.onrender.com/health"
curl -sS "https://bookme-ai-api.onrender.com/ready"
```

In the browser: Vercel app → sign in (if Clerk enabled) → send a chat message (streaming).

---

## 4. Docker Hub / compose (optional)

Local or VM deploy is unchanged: `docker compose` / `compose.prod.yaml`. Render builds from `docker/api/Dockerfile` on Git push; you do not need Docker Hub for Render+Vercel.

---

## 5. Limits (free tier)

| Provider | Limit |
|----------|--------|
| Render | Sleep on idle, 512 MB RAM — tight for 3 MCP subprocesses; upgrade if OOM |
| Vercel | Hobby bandwidth/build limits; fine for demos |
| LLM / Tavily | Billed by usage on your keys |

Alternative same-origin setup: keep `VITE_API_URL` unset and add a Vercel rewrite `/api/*` → Render (see [Vercel rewrites](https://vercel.com/docs/rewrites)); current repo uses direct API URL + CORS for simpler env wiring.
