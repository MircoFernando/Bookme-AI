# Clerk production auth (BookMe AI)

BookMe uses **stateless JWT verification** on the API — no webhooks and no user database.

## Flow

1. User signs in on the React app (`@clerk/clerk-react`).
2. Each chat request calls `getToken()` and sends `Authorization: Bearer <session JWT>`.
3. FastAPI `deps._clerk_user_id()` verifies the token and uses JWT `sub` as `user_id`.
4. `session_id` remains a client UUID per sidebar thread.

## 1. Clerk Dashboard

1. [Clerk Dashboard](https://dashboard.clerk.com/) → **Add application** (or use an existing one).
2. **API keys** — copy:
   - **Publishable key** → `VITE_CLERK_PUBLISHABLE_KEY` (frontend)
   - **Secret key** → `CLERK_SECRET_KEY` (API only; never in the frontend)
3. **Configure → Paths / URLs** (names vary by Clerk version):
   - Sign-in / after sign-in: `http://localhost:5173/` (landing page)
   - Allowed redirect / origin for dev: `http://localhost:5173`, `http://127.0.0.1:5173`
   - The React app forces post-auth redirect to `/` (landing). Chat lives at `/app`.
4. **User & authentication** — enable at least one method (Email, Google, etc.).

## 2. Environment

### API (repo root `.env`)

```bash
AUTH_DISABLED=0
CLERK_SECRET_KEY=sk_test_...
CLERK_AUTHORIZED_PARTIES=http://localhost:5173,http://127.0.0.1:5173
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`CLERK_AUTHORIZED_PARTIES` must list the **browser origin** where the SPA runs (Vite default **5173**), not the API port.

### Frontend (`frontend/.env`)

```bash
VITE_API_URL=http://127.0.0.1:8000
VITE_AUTH_DISABLED=false
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

Restart **both** processes after changing env:

```bash
make run-api   # terminal 1
make run-ui    # terminal 2
```

## 3. Verify

```bash
make check-clerk
```

Then sign in at http://localhost:5173 and send a chat message. In API logs you should **not** see body `user_id` used for auth; LangFuse/metadata should show Clerk `sub`.

## Troubleshooting

### `CLERK_SECRET_KEY is required` / API won't start

Root `.env` has `AUTH_DISABLED=0` but `CLERK_SECRET_KEY=` is empty. The **publishable** key (`pk_test_…`) only goes in `frontend/.env`; the API needs the **secret** key (`sk_test_…`) from the **same** Clerk application.

### Chat returns 401 after sign-in

- Confirm `CLERK_AUTHORIZED_PARTIES` includes `http://localhost:5173`
- Confirm `CORS_ORIGINS` matches
- Restart API after env changes

## 4. Deploy (Phase 8)

Add production frontend URL to **both**:

- `CLERK_AUTHORIZED_PARTIES` and `CORS_ORIGINS` on the API
- Clerk Dashboard allowed origins / redirect URLs for the deployed SPA

## Dev bypass (optional)

For quick backend-only testing without Clerk:

| API | Frontend |
|-----|----------|
| `AUTH_DISABLED=1` | `VITE_AUTH_DISABLED=true` |

Do not use this for production or submission demos that require sign-in.
