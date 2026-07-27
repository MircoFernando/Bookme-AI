import { useState } from "react";
import clsx from "clsx";
import { MessageSquare, Plus, Trash2, User, Wrench } from "lucide-react";
import type { SessionMeta } from "@/hooks/useSessions";
import { TravelToolsInfo } from "./TravelToolsInfo";

interface Props {
  sessions: SessionMeta[];
  activeId: string;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
  displayName: string;
  userId: string;
  activeSessionId: string;
}

export function Sidebar({
  sessions,
  activeId,
  onSelect,
  onCreate,
  onDelete,
  displayName,
  userId,
  activeSessionId,
}: Props) {
  const [tab, setTab] = useState<"sessions" | "tools">("sessions");

  return (
    <aside className="w-72 shrink-0 border-r border-border bg-bg-soft flex flex-col">
      <div className="p-3 border-b border-border">
        <div className="card p-2.5 flex items-center gap-2.5">
          <div className="size-9 rounded-full bg-brand-500/15 border border-brand-500/40 flex items-center justify-center text-brand-400">
            <User size={15} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm text-slate-100 truncate font-medium">
              {displayName}
            </div>
            <div className="text-[11px] text-slate-500 truncate font-mono">
              {userId.slice(0, 20)}
              {userId.length > 20 ? "…" : ""}
            </div>
          </div>
        </div>
      </div>

      <div className="flex text-xs border-b border-border">
        <TabButton
          active={tab === "sessions"}
          icon={<MessageSquare size={12} />}
          onClick={() => setTab("sessions")}
        >
          Sessions
        </TabButton>
        <TabButton
          active={tab === "tools"}
          icon={<Wrench size={12} />}
          onClick={() => setTab("tools")}
        >
          Tools
        </TabButton>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {tab === "sessions" ? (
          <>
            <button type="button" className="btn-primary w-full" onClick={onCreate}>
              <Plus size={14} /> New conversation
            </button>
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className={clsx(
                  "group flex items-center gap-2 px-2 py-1.5 rounded-lg border cursor-pointer",
                  s.session_id === activeId
                    ? "bg-bg-card border-brand-500/40"
                    : "border-transparent hover:bg-bg-card/60",
                )}
                onClick={() => onSelect(s.session_id)}
              >
                <MessageSquare size={13} className="shrink-0 text-slate-500" />
                <div className="flex-1 min-w-0">
                  <div className="text-sm truncate text-slate-200">{s.title}</div>
                  <div className="text-[10px] text-slate-500 truncate">
                    {s.session_id}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`Delete "${s.title}"?`)) onDelete(s.session_id);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-slate-500 hover:text-danger p-1"
                  aria-label="Delete session"
                >
                  <Trash2 size={13} />
                </button>
              </div>
            ))}
          </>
        ) : (
          <TravelToolsInfo sessionId={activeSessionId} />
        )}
      </div>
    </aside>
  );
}

function TabButton({
  active,
  icon,
  children,
  onClick,
}: {
  active: boolean;
  icon: React.ReactNode;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        "flex-1 flex items-center justify-center gap-1.5 py-2 border-b-2 transition-colors",
        active
          ? "border-brand-500 text-slate-100"
          : "border-transparent text-slate-400 hover:text-slate-200",
      )}
    >
      {icon}
      {children}
    </button>
  );
}
