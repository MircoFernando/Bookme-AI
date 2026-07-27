/**
 * Optional Bearer token for FastAPI (`resolve_user_id` / Clerk JWT).
 * Set from React via `setAuthTokenProvider` when the user is signed in.
 */

export type AuthTokenProvider = () => Promise<string | null>;

let tokenProvider: AuthTokenProvider | null = null;

export function setAuthTokenProvider(provider: AuthTokenProvider | null) {
  tokenProvider = provider;
}

export function isApiAuthDisabled(): boolean {
  return import.meta.env.VITE_AUTH_DISABLED === "true";
}

export async function authHeaders(): Promise<Record<string, string>> {
  if (isApiAuthDisabled()) return {};
  if (!tokenProvider) return {};
  const token = await tokenProvider();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}
