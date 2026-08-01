import { useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth, useUser, UserButton, SignInButton } from "@clerk/clerk-react";
import { BookMeLogo } from "@/components/BookMeLogo";
import { setAuthTokenProvider } from "@/api/auth";
import { ChatWindow } from "@/components/ChatWindow";
import { InputBox } from "@/components/InputBox";
import { Sidebar } from "@/components/Sidebar";
import { StatusBar } from "@/components/StatusBar";
import { useChatStream } from "@/hooks/useChatStream";
import { useHealth } from "@/hooks/useHealth";
import { useSessions } from "@/hooks/useSessions";

const DEV_USER_ID = import.meta.env.VITE_DEV_USER_ID || "dev-user";

type AuthMode = "dev" | "clerk";

export default function ChatApp({ authMode }: { authMode: AuthMode }) {
  if (authMode === "dev") {
    return <ChatAppDev />;
  }
  return <ChatAppClerk />;
}

function ChatAppDev() {
  return (
    <AppShell userId={DEV_USER_ID} displayName="Dev user" authMode="dev" />
  );
}

function ChatAppClerk() {
  const { isLoaded, isSignedIn, userId, getToken } = useAuth();
  const { user } = useUser();

  useEffect(() => {
    setAuthTokenProvider(() => getToken());
    return () => setAuthTokenProvider(null);
  }, [getToken, isSignedIn]);

  if (!isLoaded) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500 text-sm">
        Loading…
      </div>
    );
  }

  if (!isSignedIn || !userId) {
    return <ChatAuthRequired />;
  }

  const displayName =
    user?.firstName || user?.primaryEmailAddress?.emailAddress || userId;

  return (
    <AppShell
      userId={userId}
      displayName={String(displayName)}
      authMode="clerk"
    />
  );
}

function ChatAuthRequired() {
  return (
    <div className="h-full flex items-center justify-center px-4 bg-bg">
      <div className="w-full max-w-md text-center space-y-5">
        <BookMeLogo size="lg" className="mx-auto" />
        <div>
          <h1 className="font-display text-2xl text-white tracking-tight">
            Sign in to use the assistant
          </h1>
          <p className="text-sm text-slate-400 mt-2">
            Your chat sessions are tied to your Clerk account.
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-3">
          <SignInButton
            mode="modal"
            forceRedirectUrl="/app"
            fallbackRedirectUrl="/app"
          >
            <button type="button" className="landing-btn-primary">
              Sign in
            </button>
          </SignInButton>
          <Link to="/" className="landing-btn-ghost">
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}

function AppShell({
  userId,
  displayName,
  authMode,
}: {
  userId: string;
  displayName: string;
  authMode: AuthMode;
}) {
  const health = useHealth();
  const sessions = useSessions(userId);
  const chat = useChatStream({
    userId,
    sessionId: sessions.activeId,
    onSessionActivity: sessions.touchSession,
  });

  const activeSession = sessions.sessions.find(
    (s) => s.session_id === sessions.activeId,
  );

  if (!sessions.loaded || !sessions.activeId) {
    return (
      <div className="h-full flex items-center justify-center text-slate-500 text-sm">
        Loading…
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-bg">
      <header className="shrink-0 h-14 border-b border-border flex items-center gap-3 px-4 bg-bg-soft">
        <Link
          to="/"
          className="flex items-center justify-center rounded-lg hover:opacity-80 transition-opacity"
          title="Home"
        >
          <BookMeLogo size="xs" />
        </Link>
        <div className="flex-1 min-w-0">
          <h1 className="text-sm font-semibold text-slate-100 truncate tracking-tight font-display">
            BookMe<span className="text-violet-300"> AI</span>
          </h1>
          <div className="text-[11px] text-slate-500 truncate">
            {activeSession?.title ?? sessions.activeId}
          </div>
        </div>
        {authMode === "clerk" && (
          <UserButton
            afterSignOutUrl="/"
            appearance={{ elements: { avatarBox: "size-8" } }}
          />
        )}
        <StatusBar
          status={health.status}
          readiness={health.readiness}
          config={health.config}
        />
      </header>

      <div className="flex-1 flex min-h-0">
        <Sidebar
          sessions={sessions.sessions}
          activeId={sessions.activeId}
          onSelect={sessions.setActiveId}
          onCreate={() => sessions.create()}
          onDelete={sessions.remove}
          displayName={displayName}
          userId={userId}
          activeSessionId={sessions.activeId}
        />

        <main className="flex-1 flex flex-col min-w-0">
          <ChatWindow
            key={`${userId}::${sessions.activeId}`}
            messages={chat.messages}
            loading={chat.loading}
            thoughts={chat.thoughts}
            error={chat.error}
            onTrySample={chat.send}
          />
          <div className="shrink-0 border-t border-border p-3 bg-bg-soft">
            <div className="max-w-3xl mx-auto">
              <InputBox
                disabled={chat.loading || health.status === "offline"}
                onSend={chat.send}
                onReset={chat.reset}
                placeholder={
                  health.status === "offline"
                    ? "API offline — start the backend with `make run-api`"
                    : `Plan a trip, ${displayName.split(" ")[0]}…`
                }
              />
              <div className="flex items-center justify-between text-[10px] text-slate-500 mt-2 px-1">
                <span>
                  session=
                  <code className="text-slate-300">{sessions.activeId}</code>
                </span>
                <span>
                  <kbd className="kbd">Enter</kbd> send ·{" "}
                  <kbd className="kbd">Shift+Enter</kbd> newline
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
