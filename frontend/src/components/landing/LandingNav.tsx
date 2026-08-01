import { Link } from "react-router-dom";
import {
  SignInButton,
  SignUpButton,
  UserButton,
  useAuth,
} from "@clerk/clerk-react";
import { motion } from "framer-motion";
import { BookMeLogo } from "@/components/BookMeLogo";

function BrandMark({ compact = false }: { compact?: boolean }) {
  return (
    <Link to="/" className="group flex items-center gap-2.5 min-w-0">
      <BookMeLogo
        size="sm"
        className="transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:scale-105"
      />
      <span
        className={`font-display tracking-tight text-white ${
          compact ? "text-lg" : "text-xl"
        }`}
      >
        BookMe
        <span className="bg-gradient-to-r from-violet-300 to-blue-300 bg-clip-text text-transparent">
          {" "}
          AI
        </span>
      </span>
    </Link>
  );
}

function DevAuthActions() {
  return (
    <Link to="/app" className="landing-btn-primary">
      Open assistant
    </Link>
  );
}

function ClerkAuthActions() {
  const { isLoaded, isSignedIn } = useAuth();

  if (!isLoaded) {
    return (
      <div className="h-9 w-24 rounded-lg bg-white/5 animate-pulse" aria-hidden />
    );
  }

  if (isSignedIn) {
    return (
      <div className="flex items-center gap-3">
        <Link to="/app" className="landing-btn-primary">
          Open assistant
        </Link>
        <UserButton
          afterSignOutUrl="/"
          appearance={{
            elements: {
              avatarBox: "size-9 ring-1 ring-white/15",
            },
          }}
        />
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <SignInButton
        mode="modal"
        forceRedirectUrl="/"
        fallbackRedirectUrl="/"
      >
        <button type="button" className="landing-btn-ghost">
          Sign in
        </button>
      </SignInButton>
      <SignUpButton
        mode="modal"
        forceRedirectUrl="/"
        fallbackRedirectUrl="/"
      >
        <button type="button" className="landing-btn-primary">
          Get started
        </button>
      </SignUpButton>
    </div>
  );
}

export function LandingNav({ authMode }: { authMode: "dev" | "clerk" }) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
      className="fixed inset-x-0 top-0 z-50"
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6 pt-4">
        <nav className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-[#070b18]/70 px-4 py-3 backdrop-blur-xl shadow-[0_8px_40px_-20px_rgba(37,99,235,0.45)]">
          <BrandMark />
          <div className="hidden sm:flex items-center gap-6 text-sm text-slate-300">
            <a href="#how" className="hover:text-white transition-colors">
              How it works
            </a>
            <a href="#capabilities" className="hover:text-white transition-colors">
              Capabilities
            </a>
          </div>
          {authMode === "dev" ? <DevAuthActions /> : <ClerkAuthActions />}
        </nav>
      </div>
    </motion.header>
  );
}

export { BrandMark };
