import { useCallback, useEffect, useState } from "react";
import { chatApi, ApiError } from "@/api/client";
import type { StreamEvent, UIMessage } from "@/types";

export interface ThoughtItem {
  id: string;
  type: "stage" | "tool";
  label: string;
  status: "running" | "done" | "error";
  ms?: number;
  detail?: string;
  matchKey: string;
}

interface UseChatStreamArgs {
  userId: string;
  sessionId: string;
  onSessionActivity?: (sessionId: string, preview: string) => void;
}

export function useChatStream({
  userId,
  sessionId,
  onSessionActivity,
}: UseChatStreamArgs) {
  const [messages, setMessages] = useState<UIMessage[]>([]);
  const [thoughts, setThoughts] = useState<ThoughtItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setMessages([]);
    setThoughts([]);
    setError(null);
  }, [userId, sessionId]);

  const send = useCallback(
    async (text: string) => {
      if (!text.trim() || loading || !userId || !sessionId) return;
      setError(null);
      onSessionActivity?.(sessionId, text.trim());

      const userMsg: UIMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: text,
        ts: Date.now() / 1000,
      };
      setMessages((prev) => [...prev, userMsg]);
      setLoading(true);
      setThoughts([]);

      const onEvent = (event: StreamEvent) => {
        if (event.type === "stage_start") {
          const matchKey = `stage:${event.stage}`;
          setThoughts((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              type: "stage",
              matchKey,
              label: event.label,
              status: "running",
            },
          ]);
        } else if (event.type === "stage_done") {
          const matchKey = `stage:${event.stage}`;
          const detailStr = formatStageDetail(event.detail);
          setThoughts((prev) => {
            const idx = prev.findIndex(
              (p) => p.matchKey === matchKey && p.status === "running",
            );
            if (idx === -1) {
              return [
                ...prev,
                {
                  id: crypto.randomUUID(),
                  type: "stage",
                  matchKey,
                  label: stageLabelFromId(event.stage),
                  status: "done",
                  ms: event.ms,
                  detail: detailStr,
                },
              ];
            }
            const next = prev.slice();
            next[idx] = {
              ...next[idx],
              status: "done",
              ms: event.ms,
              detail: detailStr,
            };
            return next;
          });
        } else if (event.type === "tool_invoke") {
          const matchKey = `tool:${event.route}:${event.action ?? "_"}`;
          setThoughts((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              type: "tool",
              matchKey,
              label: event.label,
              status: "running",
            },
          ]);
        } else if (event.type === "tool_done") {
          const matchKey = `tool:${event.route}:${event.action ?? "_"}`;
          setThoughts((prev) => {
            const idx = prev.findIndex(
              (p) => p.matchKey === matchKey && p.status === "running",
            );
            if (idx === -1) return prev;
            const next = prev.slice();
            next[idx] = {
              ...next[idx],
              status: "done",
              ms: event.ms,
              detail: event.summary || undefined,
            };
            return next;
          });
        }
      };

      try {
        const res = await chatApi.stream(
          { session_id: sessionId, message: text },
          userId,
          onEvent,
        );
        const botMsg: UIMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: res.answer,
          ts: Date.now() / 1000,
          meta: {
            route: res.route,
            routes: res.routes,
            verdict: res.verdict,
            latency_ms: res.latency_ms,
            trace_id: res.trace_id,
            timings: res.timings,
            session_id: res.session_id,
          },
        };
        setMessages((prev) => [...prev, botMsg]);
        setThoughts([]);
      } catch (e) {
        const msg = e instanceof ApiError ? e.message : String(e);
        try {
          const res = await chatApi.send(
            { session_id: sessionId, message: text },
            userId,
          );
          const botMsg: UIMessage = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: res.answer,
            ts: Date.now() / 1000,
            meta: {
              route: res.route,
              routes: res.routes,
              verdict: res.verdict,
              latency_ms: res.latency_ms,
              trace_id: res.trace_id,
              timings: res.timings,
              session_id: res.session_id,
            },
          };
          setMessages((prev) => [...prev, botMsg]);
          setThoughts([]);
        } catch (e2) {
          const msg2 = e2 instanceof ApiError ? e2.message : String(e2);
          const friendly = friendlyError(msg2 || msg);
          setError(friendly);
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: "assistant",
              content: friendly,
              ts: Date.now() / 1000,
            },
          ]);
          setThoughts([]);
        }
      } finally {
        setLoading(false);
      }
    },
    [loading, userId, sessionId, onSessionActivity],
  );

  const reset = useCallback(async () => {
    try {
      await chatApi.reset(userId, sessionId);
    } catch {
      /* ignore */
    }
    setMessages([]);
    setThoughts([]);
    setError(null);
  }, [userId, sessionId]);

  return { messages, thoughts, loading, error, send, reset };
}

function friendlyError(raw: string): string {
  if (/401|Unauthorized/i.test(raw)) {
    return "Sign-in expired — refresh the page and try again.";
  }
  if (/503|MCP|not ready/i.test(raw)) {
    return "Travel services are warming up. Wait a moment and try again.";
  }
  return `Something went wrong: ${raw}`;
}

function stageLabelFromId(stage: string): string {
  const m: Record<string, string> = {
    decision: "Classifying request",
    guardrail: "Travel scope check",
    route: "Routing",
    orchestrator: "Travel agents",
    save: "Saving",
  };
  return m[stage] ?? stage;
}

function formatStageDetail(
  detail: Record<string, unknown> | undefined,
): string | undefined {
  if (!detail) return undefined;
  const parts: string[] = [];
  if ("verdict" in detail) parts.push(String(detail.verdict));
  if ("route" in detail) parts.push(String(detail.route));
  return parts.join(" · ") || undefined;
}
