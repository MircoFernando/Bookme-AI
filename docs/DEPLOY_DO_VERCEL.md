# Deploy BookMe AI — DigitalOcean (API) + Vercel (frontend)

Same split as Render + Vercel: **browser → Vercel UI**, **API calls → your DO host**. The frontend already uses `VITE_API_URL` in production (`frontend/src/api/client.ts`).

| Piece | Platform | Typical URL |
|--------|-----------|-------------|
| FastAPI + MCP | **DO Droplet** (Docker) | `https://api.yourdomain.com` |
| React UI | **Vercel** | `https://your-project.vercel.app` |

**Cost:** Droplet is **not free** (~$4–6/mo and up). You get no Render-style sleep, more RAM for MCP subprocesses, and the same CI/CD pattern as [booking-platform-api](https://github.com/) (Docker Hub + SSH `compose pull`).

---

## Why this vs Render?

| | Render (free) | DO Droplet |
|--|----------------|------------|
| Idle sleep | Yes | No |
| RAM | 512 MB (tight) | You pick (1 GB+ recommended) |
| HTTPS | Included | You add Caddy/nginx + domain |
| Ops | Low | You manage VM updates |

---

## 1. DigitalOcean — API on a Droplet

### One-time server setup

1. Create an **Ubuntu 24.04** Droplet (≥ **1 GB RAM** recommended for API + 3 MCP stdio servers).
2. Install Docker: [DO Docker guide](https://docs.digitalocean.com/products/droplets/how-to/install-docker/).
3. Point DNS **`api.yourdomain.com`** → droplet IP.
4. Install **Caddy** (or nginx) for TLS and reverse proxy to the container:

```text
# /etc/caddy/Caddyfile — example
api.yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```

5. Open firewall: **22**, **80**, **443** — do **not** expose 8000 publicly (`compose.prod.api.yaml` binds API to `127.0.0.1` only).

### App deploy (pull image)

On the droplet:

```bash
git clone https://github.com/YOU/bookme-ai.git ~/bookme-ai
cd ~/bookme-ai
cp .env.example .env
# Edit .env: API keys, plus:
#   CORS_ORIGINS=https://your-project.vercel.app
#   CLERK_AUTHORIZED_PARTIES=https://your-project.vercel.app
export DOCKER_REGISTRY_USER=your_dockerhub_username
docker compose -f compose.prod.api.yaml pull
docker compose -f compose.prod.api.yaml up -d
```

Images come from Docker Hub (`make docker-push` or `.github/workflows/docker-publish.yml`). You do **not** run the `web` service on DO when using Vercel.

### CI/CD (booking-platform-api pattern)

On push to `main`, `.github/workflows/docker-publish.yml` pushes `bookme-ai-api:latest` to Docker Hub and SSH-deploys to the droplet (`compose.prod.api.yaml`). **First-time API on DO:** [docs/DEPLOY_DO_API.md](docs/DEPLOY_DO_API.md).

## 2. Vercel — frontend (unchanged)

1. Import repo → **Root Directory:** `frontend`.
2. Production env:

| Name | Value |
|------|--------|
| `VITE_API_URL` | `https://api.yourdomain.com` |
| `VITE_CLERK_PUBLISHABLE_KEY` | `pk_…` |
| `VITE_AUTH_DISABLED` | `false` |

3. Redeploy after changing `VITE_API_URL` (build-time variable).

4. On the droplet `.env`, set **`CORS_ORIGINS`** and **`CLERK_AUTHORIZED_PARTIES`** to your Vercel URL(s), then `docker compose -f compose.prod.api.yaml up -d`.

Clerk: allow Vercel origins — [CLERK_SETUP.md](./CLERK_SETUP.md).

---

## 3. Verify

```bash
curl -sS https://api.yourdomain.com/health
curl -sS https://api.yourdomain.com/ready
```

Browser: Vercel app → sign in → chat (SSE must work through Caddy; default Caddy reverse_proxy handles streaming).

---

## 4. DO App Platform (alternative)

You can run the same `docker/api/Dockerfile` on **App Platform** instead of a Droplet (managed TLS, less SSH). Use a **Professional** or sufficiently sized instance for MCP memory; wire the same env vars and set Vercel `VITE_API_URL` to the App Platform URL.

---

## Related files

- `compose.prod.api.yaml` — API-only production compose
- `compose.prod.yaml` — API + nginx UI (use if you host both on one VM)
- [DEPLOY_RENDER_VERCEL.md](./DEPLOY_RENDER_VERCEL.md) — free-tier Render variant
