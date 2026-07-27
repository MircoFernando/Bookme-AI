import { useCallback, useEffect, useState } from "react";
import type { ChatSessionMeta } from "@/types";

export type SessionMeta = ChatSessionMeta;

const LS_SESSIONS = "bookme.chat.sessions";
const LS_ACTIVE = "bookme.chat.active";

function loadSessions(userId: string): SessionMeta[] {
  try {
    const raw = localStorage.getItem(`${LS_SESSIONS}:${userId}`);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SessionMeta[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveSessions(userId: string, list: SessionMeta[]) {
  try {
    localStorage.setItem(`${LS_SESSIONS}:${userId}`, JSON.stringify(list));
  } catch {
    /* ignore */
  }
}

function newSession(userId: string, title?: string): SessionMeta {
  const now = Date.now();
  const id = crypto.randomUUID();
  return {
    session_id: id,
    user_id: userId,
    title: title?.trim() || "New trip",
    created_at: now,
    updated_at: now,
    last_message_at: null,
  };
}

/**
 * Client-side conversation threads (Week 13 sidebar UX, no Supabase).
 * Server memory is keyed by `(user_id, session_id)` on the API.
 */
export function useSessions(userId: string | undefined | null) {
  const [sessions, setSessions] = useState<SessionMeta[]>([]);
  const [activeId, setActiveIdState] = useState("");
  const [loaded, setLoaded] = useState(false);

  const setActiveId = useCallback((id: string) => {
    setActiveIdState(id);
    if (userId) {
      try {
        localStorage.setItem(`${LS_ACTIVE}:${userId}`, id);
      } catch {
        /* ignore */
      }
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      setSessions([]);
      setActiveIdState("");
      setLoaded(true);
      return;
    }

    const list = loadSessions(userId);
    setSessions(list);

    let cached = "";
    try {
      cached = localStorage.getItem(`${LS_ACTIVE}:${userId}`) || "";
    } catch {
      cached = "";
    }

    const exists = list.some((s) => s.session_id === cached);
    if (exists && cached) {
      setActiveIdState(cached);
    } else if (list.length > 0) {
      setActiveIdState(list[0].session_id);
    } else {
      const first = newSession(userId);
      setSessions([first]);
      setActiveId(first.session_id);
    }
    setLoaded(true);
  }, [userId, setActiveId]);

  const create = useCallback(
    (title?: string) => {
      if (!userId) return null;
      const row = newSession(userId, title);
      setSessions((prev) => {
        const next = [row, ...prev];
        saveSessions(userId, next);
        return next;
      });
      setActiveId(row.session_id);
      return row;
    },
    [userId, setActiveId],
  );

  const remove = useCallback(
    (session_id: string) => {
      if (!userId) return;
      setSessions((prev) => {
        const next = prev.filter((s) => s.session_id !== session_id);
        saveSessions(userId, next);
        if (session_id === activeId) {
          const fallback = next[0]?.session_id ?? "";
          if (fallback) setActiveId(fallback);
          else {
            const fresh = newSession(userId);
            saveSessions(userId, [fresh]);
            setActiveId(fresh.session_id);
            return [fresh];
          }
        }
        return next;
      });
    },
    [userId, activeId, setActiveId],
  );

  const touchSession = useCallback(
    (session_id: string, preview: string) => {
      if (!userId) return;
      setSessions((prev) => {
        const now = Date.now();
        const next = prev.map((s) => {
          if (s.session_id !== session_id) return s;
          const title =
            s.title === "New trip" && preview
              ? preview.slice(0, 48)
              : s.title;
          return {
            ...s,
            title,
            updated_at: now,
            last_message_at: now,
          };
        });
        saveSessions(userId, next);
        return next;
      });
    },
    [userId],
  );

  return {
    sessions,
    activeId,
    setActiveId,
    create,
    remove,
    touchSession,
    loaded,
  };
}
