# Deploy BookMe AI API on DigitalOcean (Docker Hub + GitHub Actions)

Same pattern as **booking-platform-api**: multi-stage `docker/api/Dockerfile` → Docker Hub → droplet runs `compose.prod.api.yaml` (pull only, no build on server). Frontend on Vercel comes later; this doc is **API only**.

| booking-platform-api | BookMe AI |
|--------------------|-----------|
| `Dockerfile` (repo root) | `docker/api/Dockerfile` |
| `compose.prod.yaml` | `compose.prod.api.yaml` |
| Image `…/booking-platform-api:latest` | `…/bookme-ai-api:latest` |
| Droplet path `~/booking-platform-api` | Droplet path `~/bookme-ai` |
| `.github/workflows/docker-publish.yml` | Same layout (build → SSH deploy) |

---

## Same droplet as booking-platform-api (end-to-end)

Use this when booking-platform **already runs** on your DO droplet and you add BookMe beside it (no second VM).

**Layout on one machine**

| App | Directory | Compose | Listens (internal) | Public URL (example) |
|-----|-----------|---------|--------------------|----------------------|
| booking-platform-api | `~/booking-platform-api` | `compose.prod.yaml` | `:3000` (+ Postgres) | `https://api.yourbooking.com` |
| BookMe AI API | `~/bookme-ai` | `compose.prod.api.yaml` | `127.0.0.1:8000` | `https://YOUR-IP.sslip.io` (no domain) or custom domain |

Ports do not clash. Caddy gets a **second site block** (do not remove booking’s block).

**No domain?** Skip DNS below — use **[No custom domain](#no-custom-domain-https-without-buying-a-domain)** (`sslip.io` + Caddy).

### A. Local — commit BookMe deploy files

Ensure `main` includes: `docker/api/Dockerfile`, `compose.prod.api.yaml`, `.github/workflows/docker-publish.yml`, and this doc. Push to GitHub.

### B. BookMe GitHub repo — Actions secrets

**Settings → Secrets and variables → Actions** on the **BookMe AI** repo:

| Secret | Value |
|--------|--------|
| `DOCKER_USERNAME` | Same Hub user as booking-platform (e.g. `mircofernando`) |
| `DOCKER_TOKEN` | Same Hub token (or a new token with read/write) |
| `DROPLET_HOST` | **Same IP** as booking-platform’s `DROPLET_HOST` |
| `SSH_PRIVATE_KEY` | **Same private key** as booking-platform’s deploy key |

You do **not** need new SSH keys if booking deploy already works — reuse secrets.

Optional (for `push_web` job only, Vercel later): `VITE_CLERK_PUBLISHABLE_KEY`.

### C. Droplet — one-time BookMe setup (SSH as root)

**C.1 — Skip Docker install** if booking already uses Docker.

**C.2 — Clone BookMe** (path must match the workflow):

```bash
git clone https://github.com/YOUR_GITHUB_USER/YOUR_BOOKME_REPO.git ~/bookme-ai
cd ~/bookme-ai
```

**C.3 — Create `.env`** (never commit this file):

```bash
cp .env.example .env
nano .env
```

Set at minimum:

- `OPENAI_API_KEY`, `TAVILY_API_KEY`, `GOOGLE_API_KEY` (if used)
- `DOCKER_REGISTRY_USER` = same as `DOCKER_USERNAME` on GitHub
- For a quick test: `AUTH_DISABLED=1` (switch to Clerk before Vercel)
- For production: `AUTH_DISABLED=0`, `CLERK_SECRET_KEY`, `CLERK_AUTHORIZED_PARTIES`, `CORS_ORIGINS` (Vercel URLs later)

**C.4 — First API start** (after Hub has an image — step D):

```bash
cd ~/bookme-ai
docker compose -f compose.prod.api.yaml pull
docker compose -f compose.prod.api.yaml up -d
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/ready
```

If `pull` fails with “denied”, run `docker login` on the droplet (private Hub repo).

**C.5 — DNS** *(skip if you have no domain — see [below](#no-custom-domain-https-without-buying-a-domain))*

Add an **A record** for a **new** hostname (not booking’s), e.g. `bookme-api.yourdomain.com` → droplet IP.

**C.6 — Caddy (add BookMe, keep booking)** *(skip if using sslip.io block in the no-domain section instead)*

Edit `/etc/caddy/Caddyfile`. **Append** a block; leave the existing booking block unchanged:

```text
# existing booking block stays, e.g.:
# api.yourbooking.com {
#     reverse_proxy 127.0.0.1:3000
# }

bookme-api.yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
curl -sS https://bookme-api.yourdomain.com/ready
```

**C.7 — Memory check** (same droplet = shared RAM):

```bash
free -h
docker stats --no-stream
```

If BookMe OOMs, resize the droplet to **2 GB+** in the DO control panel.

### D. First image on Docker Hub

**Option 1 — GitHub Actions:** Push to `main` on BookMe, or run workflow **Publish & Deploy Docker Image** manually.

**Option 2 — Laptop:**

```bash
cd "/path/to/Bookme AI"
docker login
export DOCKER_REGISTRY_USER=mircofernando
docker compose build api
docker tag bookme/bookme-ai-api:local $DOCKER_REGISTRY_USER/bookme-ai-api:latest
docker push $DOCKER_REGISTRY_USER/bookme-ai-api:latest
```

Then on the droplet run **C.4** again if the container was never started.

### E. Automated deploys (both repos, one droplet)

| Repo | On push to `main` | On droplet |
|------|-------------------|------------|
| booking-platform-api | SSH → `~/booking-platform-api` + `compose.prod.yaml` | Nest + Postgres |
| BookMe AI | SSH → `~/bookme-ai` + `compose.prod.api.yaml` | FastAPI + MCP |

Deploys are independent; they only share the VM, Caddy, and optionally the same GitHub secrets values.

### F. Verify end-to-end

```bash
# From your laptop
curl -sS https://bookme-api.yourdomain.com/health
curl -sS https://bookme-api.yourdomain.com/ready
curl -sS https://bookme-api.yourdomain.com/docs   # optional OpenAPI UI
```

Booking should still work on its own URL unchanged.

### G. Before Vercel (later)

1. Vercel `VITE_API_URL=https://bookme-api.yourdomain.com`
2. Update droplet `.env`: `CORS_ORIGINS` and `CLERK_AUTHORIZED_PARTIES` with Vercel URL(s)
3. `docker compose -f compose.prod.api.yaml up -d` on the droplet

See [DEPLOY_DO_VERCEL.md](./DEPLOY_DO_VERCEL.md).

---

## No custom domain (HTTPS without buying a domain)

You still need **HTTPS** for a **Vercel** UI (`https://…vercel.app`) talking to your API. Browsers block `https` pages calling `http://YOUR_DROPLET_IP`.

**Recommended: [sslip.io](https://sslip.io)** — free hostname that points at your droplet IP; **Let’s Encrypt** works with Caddy (no DNS purchase).

### 1. Build your hostname from the droplet IP

Replace dots with dashes and add `.sslip.io`:

| Droplet IP | BookMe API URL |
|------------|----------------|
| `159.65.123.45` | `https://159-65-123-45.sslip.io` |

Traffic to that name resolves to your IP automatically.

### 2. Caddy on the same droplet (second block)

If Caddy is not installed: `apt update && apt install -y caddy`.

Edit `/etc/caddy/Caddyfile` — **keep booking’s existing block**, add:

```text
159-65-123-45.sslip.io {
    reverse_proxy 127.0.0.1:8000
}
```

Use **your** IP-dashed name. BookMe still listens on `127.0.0.1:8000` only (`compose.prod.api.yaml`).

```bash
caddy validate --config /etc/caddy/Caddyfile
systemctl reload caddy
curl -sS https://159-65-123-45.sslip.io/ready
```

Open **80** and **443** on the droplet firewall if not already (`ufw allow 80`, `ufw allow 443`).

### 3. Same droplet checklist (no domain)

1. GitHub secrets on BookMe repo (same `DROPLET_HOST` / SSH key as booking).  
2. `git clone … ~/bookme-ai`, `.env` with keys + `DOCKER_REGISTRY_USER`.  
3. Push `bookme-ai-api:latest` to Hub → `docker compose -f compose.prod.api.yaml pull && up -d`.  
4. Caddy sslip.io block → `curl https://YOUR-IP-DASHED.sslip.io/ready`.  
5. **Vercel** (later): `VITE_API_URL=https://YOUR-IP-DASHED.sslip.io`  
6. Droplet `.env`:  
   - `CORS_ORIGINS=https://your-app.vercel.app`  
   - `CLERK_AUTHORIZED_PARTIES=https://your-app.vercel.app`  
   - Clerk Dashboard: add the same Vercel origin (+ sslip.io if Clerk requires API origin — usually frontend origin is enough)

### 4. Alternative: Cloudflare Quick Tunnel (no Caddy, random URL)

On the droplet (API running on `127.0.0.1:8000`):

```bash
# one-off install + tunnel (URL changes each run unless you sign up for a named tunnel)
curl -L "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb" -o /tmp/cloudflared.deb
apt install -y /tmp/cloudflared.deb
cloudflared tunnel --url http://127.0.0.1:8000
```

Use the printed `https://….trycloudflare.com` as `VITE_API_URL`. Good for a quick demo; URL is not stable unless you configure a free Cloudflare account + named tunnel.

### 5. What not to do

- **`VITE_API_URL=http://DROPLET_IP:8000`** from Vercel — mixed content blocked.  
- **Raw IP HTTPS** — no public cert for bare IPs in most setups; use sslip.io or a tunnel.

---

## Prerequisites (new droplet only)

- GitHub repo pushed to `main`
- [Docker Hub](https://hub.docker.com) account (same namespace as booking-platform, e.g. `mircofernando`)
- DigitalOcean droplet (Ubuntu 24.04, **≥ 1 GB RAM** recommended)
- Domain optional for first test (use Caddy + DNS when you go public / Vercel)

---

## Step 1 — GitHub secrets

In the repo: **Settings → Secrets and variables → Actions**:

| Secret | Purpose |
|--------|---------|
| `DOCKER_USERNAME` | Docker Hub username (must match `DOCKER_REGISTRY_USER` on droplet) |
| `DOCKER_TOKEN` | Hub access token ([Create token](https://hub.docker.com/settings/security)) |
| `DROPLET_HOST` | Droplet public IP or hostname |
| `SSH_PRIVATE_KEY` | Private key that can `ssh root@DROPLET_HOST` |

Generate a deploy key (if you do not already use one for booking-platform):

```bash
ssh-keygen -t ed25519 -C "github-actions-bookme" -f ~/.ssh/bookme_do_deploy -N ""
cat ~/.ssh/bookme_do_deploy.pub   # add to droplet ~/.ssh/authorized_keys
cat ~/.ssh/bookme_do_deploy       # paste into GitHub secret SSH_PRIVATE_KEY
```

---

## Step 2 — One-time droplet setup

SSH into the droplet as `root`.

### 2.1 Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

### 2.2 Clone repo (path must match the workflow)

```bash
git clone https://github.com/YOUR_GITHUB_USER/YOUR_REPO.git ~/bookme-ai
cd ~/bookme-ai
```

Use the same clone path **`~/bookme-ai`** — `.github/workflows/docker-publish.yml` runs `cd ~/bookme-ai`.

### 2.3 Configure environment

```bash
cp .env.example .env
nano .env
```

Required for a running API:

- `OPENAI_API_KEY`, `TAVILY_API_KEY` (and `GOOGLE_API_KEY` if merge uses Gemini)
- `AUTH_DISABLED=0`, `CLERK_SECRET_KEY` (or `AUTH_DISABLED=1` for a quick smoke test)
- **`DOCKER_REGISTRY_USER`** — same as `DOCKER_USERNAME` in GitHub (e.g. `mircofernando`)

Optional now; set before Vercel:

- `CORS_ORIGINS`, `CLERK_AUTHORIZED_PARTIES` — your future Vercel URL(s)

### 2.4 Pull and start API (first deploy)

Ensure the image exists on Hub (Step 3) **or** push once from your laptop:

```bash
# From your machine (once), after docker login:
# export DOCKER_REGISTRY_USER=mircofernando
# make docker-push   # pushes bookme-ai-api:latest
```

On the droplet:

```bash
cd ~/bookme-ai
docker compose -f compose.prod.api.yaml pull
docker compose -f compose.prod.api.yaml up -d
docker compose -f compose.prod.api.yaml ps
docker compose -f compose.prod.api.yaml logs -f api
```

Smoke test **on the droplet** (API is bound to localhost only):

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS http://127.0.0.1:8000/ready
```

### 2.5 HTTPS (before browsers / Vercel)

Browsers need **HTTPS** for production Clerk. Point `api.yourdomain.com` to the droplet IP, then:

```bash
apt update && apt install -y caddy
```

```text
# /etc/caddy/Caddyfile
api.yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```

```bash
systemctl reload caddy
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

Verify:

```bash
curl -sS https://api.yourdomain.com/ready
```

---

## Step 3 — First image on Docker Hub

**Option A — GitHub Actions (after secrets are set)**

Push to `main` (or **Actions → Publish & Deploy Docker Image → Run workflow**). The `push_to_registry` job builds `docker/api/Dockerfile` and pushes:

- `DOCKER_USERNAME/bookme-ai-api:latest`
- `DOCKER_USERNAME/bookme-ai-api:SHA`

**Option B — Local (same as booking-platform manual push)**

```bash
docker login
export DOCKER_REGISTRY_USER=your_dockerhub_username
docker compose build api   # uses docker-compose.yml locally
make docker-push           # tags :local → :latest and pushes API (+ web if built)
```

Hub image must be **public** or run `docker login` on the droplet before `compose pull`.

---

## Step 4 — Automated deploy (booking-platform parity)

Every push to `main`:

1. **Build & Push API Image to Docker Hub** — `docker/build-push-action`, GHA cache (`cache-from` / `cache-to` type=gha)
2. **Deploy API to DigitalOcean Droplet** — `appleboy/ssh-action`:

```bash
cd ~/bookme-ai
git pull origin main
docker compose -f compose.prod.api.yaml pull
docker compose -f compose.prod.api.yaml up -d
docker image prune -f
```

The `deploy` job runs only after `push_to_registry` succeeds. The **web** image still builds in parallel (`push_web`) but is not deployed on DO when you use Vercel.

---

## Step 5 — Troubleshooting

| Symptom | Check |
|---------|--------|
| `pull` 404 / denied | Image name vs `DOCKER_REGISTRY_USER`; Hub login on droplet for private repos |
| `/ready` fails | `docker compose logs api` — missing API keys, MCP OOM (upgrade droplet RAM) |
| Deploy SSH fails | `DROPLET_HOST`, key in `authorized_keys`, firewall port 22 |
| Workflow skips deploy | `deploy` needs `push_to_registry`; fix build job first |

---

## Files reference

- **Dockerfile:** `docker/api/Dockerfile` (Python 3.11 slim, venv builder, `PORT` for PaaS; on DO compose uses internal port 8000)
- **Production compose:** `compose.prod.api.yaml`
- **Workflow:** `.github/workflows/docker-publish.yml`
- **Vercel + CORS:** [DEPLOY_DO_VERCEL.md](./DEPLOY_DO_VERCEL.md)
