import { Building2, Globe, Plane } from "lucide-react";

interface Props {
  sessionId: string;
}

/** Static tool overview — BookMe agents are invoked via chat, not REST tool routes. */
export function TravelToolsInfo({ sessionId }: Props) {
  return (
    <div className="space-y-3 text-xs text-slate-400">
      <p>
        Ask in chat — the router sends your request to MCP-backed hotel, flight,
        and web search agents for session{" "}
        <code className="text-slate-300">{sessionId.slice(0, 8)}…</code>.
      </p>
      <div className="card p-3 space-y-2">
        <Row icon={Building2} label="Hotels" hint="Search, list, book via Convex" />
        <Row icon={Plane} label="Flights" hint="Search and list routes" />
        <Row icon={Globe} label="Web search" hint="Tavily — destinations & tips" />
      </div>
    </div>
  );
}

function Row({
  icon: Icon,
  label,
  hint,
}: {
  icon: typeof Plane;
  label: string;
  hint: string;
}) {
  return (
    <div className="flex items-start gap-2">
      <Icon size={14} className="text-brand-400 shrink-0 mt-0.5" />
      <div>
        <div className="text-slate-200">{label}</div>
        <div className="text-[10px] text-slate-500">{hint}</div>
      </div>
    </div>
  );
}
