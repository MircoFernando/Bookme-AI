/**
 * Thin fetch wrapper for the BookMe FastAPI backend.
 *
 * Dev/Docker: `/api` (Vite or nginx proxy). Vercel+Render: set `VITE_API_URL` to the Render API origin (production builds only).
 */

import { authHeaders, isApiAuthDisabled } from "@/api/auth";
import type {
  ChatRequest,
  ChatResponse,
  ConfigResponse,
  HealthResponse,
  ReadinessResponse,
  StreamEvent,
} from "@/types";

/** Dev/Docker: `/api` (Vite or nginx proxy). Vercel+Render: absolute `VITE_API_URL`. */
function resolveApiBase(): string {
  const url = import.meta.env.VITE_API_URL?.trim();
  if (import.meta.env.PROD && url && /^https?:\/\//i.test(url)) {
    return url.replace(/\/$/, "");
  }
  return "/api";
}

const BASE = resolveApiBase();

export class ApiError extends Error {
  constructor(
    public status: number,
    public body: unknown,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  init: RequestInit & { json?: unknown } = {},
): Promise<T> {
  const { json, headers, ...rest } = init;
  const auth = await authHeaders();
  const res = await fetch(`${BASE}${path}`, {
    ...rest,
    headers: {
      "content-type": "application/json",
      ...auth,
      ...(headers || {}),
    },
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });

  if (!res.ok) {
    let body: unknown = null;
    try {
      body = await res.json();
    } catch {
      /* ignore */
    }
    const detail = body as { detail?: string };
    const msg =
      typeof detail?.detail === "string"
        ? detail.detail
        : res.statusText || "Request failed";
    throw new ApiError(res.status, body, msg);
  }

  const text = await res.text();
  return (text ? JSON.parse(text) : null) as T;
}

function chatPayload(req: ChatRequest, userId: string): ChatRequest {
  const base: ChatRequest = {
    session_id: req.session_id,
    message: req.message,
  };
  if (isApiAuthDisabled()) {
    base.user_id = userId;
  }
  return base;
}

export const chatApi = {
  send: (req: ChatRequest, userId: string) =>
    request<ChatResponse>("/chat", {
      method: "POST",
      json: chatPayload(req, userId),
    }),

  reset: (userId: string, session_id: string) =>
    request<{ cleared: boolean; user_id: string; session_id: string }>(
      "/chat/reset",
      {
        method: "POST",
        json: isApiAuthDisabled()
          ? { user_id: userId, session_id }
          : { session_id },
      },
    ),

  stream: async (
    req: ChatRequest,
    userId: string,
    onEvent: (event: StreamEvent) => void,
    signal?: AbortSignal,
  ): Promise<ChatResponse> => {
    const auth = await authHeaders();
    const res = await fetch(`${BASE}/chat/stream`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "text/event-stream",
        ...auth,
      },
      body: JSON.stringify(chatPayload(req, userId)),
      signal,
    });
    if (!res.ok || !res.body) {
      let body: unknown = null;
      try {
        body = await res.json();
      } catch {
        /* ignore */
      }
      const detail = body as { detail?: string };
      throw new ApiError(
        res.status,
        body,
        detail?.detail || res.statusText,
      );
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
    let finalResponse: ChatResponse | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });

      let idx;
      while ((idx = buf.indexOf("\n\n")) !== -1) {
        const frame = buf.slice(0, idx).trim();
        buf = buf.slice(idx + 2);
        if (!frame || frame.startsWith(":")) continue;
        const dataLine = frame.split("\n").find((l) => l.startsWith("data:"));
        if (!dataLine) continue;
        const json = dataLine.slice("data:".length).trim();
        if (!json) continue;
        let event: StreamEvent;
        try {
          event = JSON.parse(json) as StreamEvent;
        } catch {
          continue;
        }
        onEvent(event);
        if (event.type === "final") {
          const { type: _t, ...rest } = event;
          finalResponse = rest as ChatResponse;
        } else if (event.type === "error") {
          throw new ApiError(event.status ?? 500, null, event.message);
        }
      }
    }

    if (!finalResponse) {
      throw new ApiError(0, null, "Stream ended without a final event");
    }
    return finalResponse;
  },
};

export const systemApi = {
  health: () => request<HealthResponse>("/health"),
  ready: () => request<ReadinessResponse>("/ready"),
  config: () => request<ConfigResponse>("/config"),
};
