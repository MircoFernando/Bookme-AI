# =============================================================================
# BookMe AI — Web container (Node builder + nginx runtime)
#
#   1. builder — npm ci + vite build (Clerk keys via build-args)
#   2. runtime — nginx-alpine serves dist/ and proxies /api → api:8000
# =============================================================================

# syntax=docker/dockerfile:1

# ── Stage 1 — build SPA ───────────────────────────────────────────────────────
FROM node:22-alpine AS builder

WORKDIR /app

ARG VITE_CLERK_PUBLISHABLE_KEY=
ARG VITE_AUTH_DISABLED=false
ENV VITE_CLERK_PUBLISHABLE_KEY=$VITE_CLERK_PUBLISHABLE_KEY \
    VITE_AUTH_DISABLED=$VITE_AUTH_DISABLED

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --no-fund

COPY frontend/ ./
RUN npm run build

# ── Stage 2 — nginx ───────────────────────────────────────────────────────────
FROM nginx:alpine AS runtime

RUN rm /etc/nginx/conf.d/default.conf
COPY docker/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD wget -q --spider http://localhost/healthz || exit 1

CMD ["nginx", "-g", "daemon off;"]
