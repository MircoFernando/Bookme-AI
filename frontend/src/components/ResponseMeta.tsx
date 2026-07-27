import { useState } from "react";
import clsx from "clsx";
import {
  Building2,
  ChevronRight,
  Globe,
  LayoutList,
  Plane,
  ShieldOff,
  Sparkles,
  Timer,
  type LucideIcon,
} from "lucide-react";
import type { Route, UIMessage } from "@/types";

interface Props {
  meta: NonNullable<UIMessage["meta"]>;
}

const ROUTE_LABELS: Record<Route, string> = {
  hotel: "Hotel agent",
  flight: "Flight agent",
  general_qa: "Travel Q&A",
  web_search: "Web · Tavily",
  multi: "Multi-intent fan-out",
  out_of_scope: "Guardrail · out of scope",
};

const ROUTE_ICONS: Record<Route, LucideIcon> = {
  hotel: Building2,
  flight: Plane,
  general_qa: Sparkles,
  web_search: Globe,
  multi: LayoutList,
  out_of_scope: ShieldOff,
};

export function ResponseMeta({ meta }: Props) {
  const [open, setOpen] = useState(false);
  const Icon = ROUTE_ICONS[meta.route] ?? Sparkles;
  const fast = meta.latency_ms < 300;
  const slow = meta.latency_ms > 2000;

  return (
    <div className="text-[11px] text-slate-400 flex flex-wrap gap-1.5 pl-1 items-center">
      <span className="chip bg-bg-soft border border-border text-slate-300">
        <Icon size={11} />
        {ROUTE_LABELS[meta.route] ?? meta.route}
      </span>

      {meta.routes.length > 1 && (
        <span className="chip bg-bg-soft border border-border text-slate-300">
          <LayoutList size={11} /> {meta.routes.length} routes
        </span>
      )}

      <span
        className={clsx(
          "chip bg-bg-soft border border-border",
          fast ? "text-success" : slow ? "text-warn" : "text-slate-300",
        )}
        title="End-to-end latency"
      >
        <Timer size={11} /> {meta.latency_ms} ms
      </span>

      {meta.verdict === "out_of_scope" && (
        <span className="chip bg-warn/10 border border-warn/30 text-warn">
          out of scope
        </span>
      )}

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="chip border border-border text-slate-400 hover:text-slate-200 hover:bg-bg-soft"
      >
        <ChevronRight
          size={11}
          className={clsx("transition-transform", open && "rotate-90")}
        />
        details
      </button>

      {meta.timings && Object.keys(meta.timings).length > 0 && (
        <div className="basis-full flex flex-wrap gap-1 pt-1">
          {Object.entries(meta.timings).map(([k, v]) => (
            <span
              key={k}
              className="chip bg-bg-soft border border-border text-slate-400 text-[10px]"
              title={`${k} stage latency`}
            >
              {k} <span className="text-slate-300 ml-0.5">{v}ms</span>
            </span>
          ))}
        </div>
      )}

      {open && (
        <div className="basis-full mt-2 card px-3 py-2 font-mono text-[11px] text-slate-400 space-y-1">
          <Row label="route" value={meta.route} />
          {meta.routes.length > 0 && (
            <Row label="routes" value={meta.routes.join(", ")} />
          )}
          <Row label="verdict" value={meta.verdict} />
          <Row label="latency_ms" value={String(meta.latency_ms)} />
          {meta.trace_id && <Row label="trace_id" value={meta.trace_id} />}
          {meta.session_id && <Row label="session_id" value={meta.session_id} />}
          {meta.timings && Object.keys(meta.timings).length > 0 && (
            <>
              <div className="pt-1 text-slate-500">timings (ms)</div>
              {Object.entries(meta.timings).map(([k, v]) => (
                <Row key={k} label={`  ${k}`} value={String(v)} />
              ))}
            </>
          )}
        </div>
      )}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex gap-3">
      <span className="text-slate-500 w-24 shrink-0">{label}</span>
      <span className="text-slate-300 break-all">{value}</span>
    </div>
  );
}
