/**
 * TypeScript mirror of `src/api/schemas.py` (BookMe AI).
 */

export type Route =
  | "hotel"
  | "flight"
  | "general_qa"
  | "web_search"
  | "multi"
  | "out_of_scope";

export type Verdict = "proceed" | "out_of_scope";

export interface ChatRequest {
  session_id: string;
  message: string;
  /** Only when API `AUTH_DISABLED=1` — ignored when Bearer JWT is verified. */
  user_id?: string;
}

export interface ChatResponse {
  answer: string;
  route: Route;
  routes: string[];
  verdict: Verdict;
  latency_ms: number;
  trace_id: string | null;
  timings?: Record<string, number>;
  session_id: string;
  tool_output?: string;
}

export interface HealthResponse {
  status: "ok" | "starting" | "degraded";
}

export interface ReadinessCheck {
  name: string;
  ok: boolean;
  detail?: string | null;
}

export interface ReadinessResponse {
  ready: boolean;
  checks: ReadinessCheck[];
}

export interface ConfigResponse {
  chat_model: string;
  router_model: string;
  guardrail_model: string;
  merge_model: string;
  provider: string;
  mcp_tools_loaded: number;
  auth_disabled: boolean;
}

export type StageId = "decision" | "guardrail" | "route" | "orchestrator" | "save";

export interface StageStartEvent {
  type: "stage_start";
  stage: string;
  label: string;
  detail?: Record<string, unknown>;
}

export interface StageDoneEvent {
  type: "stage_done";
  stage: string;
  ms: number;
  detail?: Record<string, unknown>;
}

export interface ToolInvokeEvent {
  type: "tool_invoke";
  route: string;
  action: string | null;
  label: string;
}

export interface ToolDoneEvent {
  type: "tool_done";
  route: string;
  action: string | null;
  ms: number;
  summary?: string;
}

export interface FinalEvent {
  type: "final";
  answer: string;
  route: Route;
  routes: string[];
  verdict: Verdict;
  latency_ms: number;
  trace_id: string | null;
  timings?: Record<string, number>;
  session_id: string;
  tool_output?: string;
}

export interface ErrorEvent {
  type: "error";
  status?: number;
  message: string;
}

export type StreamEvent =
  | StageStartEvent
  | StageDoneEvent
  | ToolInvokeEvent
  | ToolDoneEvent
  | FinalEvent
  | ErrorEvent;

export interface UIMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  ts: number;
  meta?: {
    route: Route;
    routes: string[];
    verdict: Verdict;
    latency_ms: number;
    trace_id: string | null;
    timings?: Record<string, number>;
    session_id?: string;
  };
}

/** Local sidebar thread metadata (no DB — keyed by Clerk user id). */
export interface ChatSessionMeta {
  session_id: string;
  user_id: string;
  title: string;
  last_message_at: number | null;
  created_at: number;
  updated_at: number;
}
