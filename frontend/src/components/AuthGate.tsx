import { Plane } from "lucide-react";
import { SignIn, SignedOut } from "@clerk/clerk-react";
import { isApiAuthDisabled } from "@/api/auth";

interface DevGateProps {
  onContinue: () => void;
}

/**
 * Identity gate — same layout as Week 13 PatientGate, Clerk SignIn in prod,
 * one-click dev continue when `VITE_AUTH_DISABLED=true`.
 */
export function AuthGate({ onContinue }: DevGateProps) {
  const devMode = isApiAuthDisabled();

  return (
    <div className="h-full flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="mx-auto size-14 rounded-2xl bg-brand-500/15 border border-brand-500/40 flex items-center justify-center mb-3">
            <Plane size={26} className="text-brand-400" />
          </div>
          <h1 className="text-xl font-semibold text-slate-100">BookMe AI</h1>
          <p className="text-sm text-slate-400 mt-1">
            Flights, hotels, and travel planning — sign in to continue.
          </p>
        </div>

        {devMode ? (
          <div className="card p-5 space-y-4">
            <p className="text-sm text-slate-400">
              Local dev: API auth is disabled. Continue with a dev user id (sent in
              the request body).
            </p>
            <button type="button" className="btn-primary w-full" onClick={onContinue}>
              Continue to chat
            </button>
          </div>
        ) : (
          <div className="card p-4 flex justify-center [&_.cl-rootBox]:mx-auto">
            <SignedOut>
              <SignIn routing="hash" />
            </SignedOut>
          </div>
        )}

        <p className="text-[10px] text-slate-600 text-center mt-4">
          {devMode
            ? "Set AUTH_DISABLED=0 and add Clerk keys for production-style auth."
            : "Secured with Clerk — the API verifies your JWT; never trust client user ids."}
        </p>
      </div>
    </div>
  );
}
