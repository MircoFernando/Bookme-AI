import { useEffect, useRef } from "react";
import { MapPin, Plane } from "lucide-react";
import type { UIMessage } from "@/types";
import type { ThoughtItem } from "@/hooks/useChatStream";
import { ChainOfThought } from "./ChainOfThought";
import { MessageBubble } from "./MessageBubble";

interface Props {
  messages: UIMessage[];
  loading: boolean;
  thoughts: ThoughtItem[];
  error: string | null;
  onTrySample?: (text: string) => void;
}

const SAMPLE_PROMPTS = [
  "Find flights from Colombo to Dubai in November",
  "Hotels in Kandy for 3 nights — search and compare",
  "Tourist spots and food in Barcelona (live web search)",
  "Flight BOM to CMB plus a hotel near the coast",
];

export function ChatWindow({
  messages,
  loading,
  thoughts,
  error,
  onTrySample,
}: Props) {
  const end = useRef<HTMLDivElement>(null);

  useEffect(() => {
    end.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, thoughts.length]);

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6">
      {messages.length === 0 && !loading && (
        <EmptyState onTrySample={onTrySample} disabled={loading} />
      )}

      <div className="space-y-4 max-w-3xl mx-auto w-full">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}

        {loading && <ChainOfThought items={thoughts} />}

        {error && (
          <div className="text-xs text-danger px-2">
            Connection error: {error}
          </div>
        )}

        <div ref={end} />
      </div>
    </div>
  );
}

function EmptyState({
  onTrySample,
  disabled,
}: {
  onTrySample?: (text: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="max-w-2xl mx-auto text-center py-12 space-y-6 animate-fade-in">
      <div className="inline-flex items-center justify-center size-14 rounded-2xl bg-brand-500/10 border border-brand-500/30">
        <Plane className="text-brand-400" size={26} />
      </div>
      <div>
        <h2 className="text-xl font-semibold text-slate-100 tracking-tight">
          BookMe<span className="text-brand-400"> AI</span>
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-md mx-auto">
          Your travel copilot — search flights and hotels, ask trip questions, or
          get destination tips. We route each message through guardrail + router,
          then MCP agents (Convex + Tavily).
        </p>
      </div>
      <div className="grid sm:grid-cols-2 gap-2 text-left">
        {SAMPLE_PROMPTS.map((s) => (
          <button
            key={s}
            type="button"
            disabled={disabled || !onTrySample}
            onClick={() => onTrySample?.(s)}
            className="card px-3 py-2.5 text-sm text-slate-300 text-left hover:border-brand-500/40 hover:bg-bg-soft/80 transition-colors disabled:opacity-60 disabled:cursor-default flex gap-2 items-start"
          >
            <MapPin size={14} className="shrink-0 text-brand-400 mt-0.5" />
            <span>{s}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
