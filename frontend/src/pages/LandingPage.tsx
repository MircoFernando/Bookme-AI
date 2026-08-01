import { Link } from "react-router-dom";
import {
  SignInButton,
  SignUpButton,
  useAuth,
} from "@clerk/clerk-react";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Hotel,
  Plane,
  Search,
  ShieldCheck,
  Sparkles,
  Workflow,
} from "lucide-react";
import { BookMeLogo } from "@/components/BookMeLogo";
import { AnimatedGradientBackground } from "@/components/ui/animated-gradient-background";
import { AuroraField } from "@/components/landing/AuroraField";
import { LandingNav } from "@/components/landing/LandingNav";
import { Reveal, Stagger, StaggerItem } from "@/components/landing/Reveal";

type AuthMode = "dev" | "clerk";

function ArrowIcon() {
  return (
    <ArrowRight
      size={16}
      className="transition-transform group-hover:translate-x-0.5"
    />
  );
}

function DevPrimaryCta({ label }: { label: string }) {
  return (
    <Link to="/app" className="landing-btn-primary landing-btn-lg group">
      {label}
      <ArrowIcon />
    </Link>
  );
}

function ClerkPrimaryCta({ label }: { label: string }) {
  const { isSignedIn } = useAuth();

  if (isSignedIn) {
    return (
      <Link to="/app" className="landing-btn-primary landing-btn-lg group">
        Open assistant
        <ArrowIcon />
      </Link>
    );
  }

  return (
    <SignUpButton mode="modal" forceRedirectUrl="/" fallbackRedirectUrl="/">
      <button type="button" className="landing-btn-primary landing-btn-lg group">
        {label}
        <ArrowIcon />
      </button>
    </SignUpButton>
  );
}

function DevSecondaryCta() {
  return (
    <a href="#how" className="landing-btn-ghost landing-btn-lg">
      See how it works
    </a>
  );
}

function ClerkSecondaryCta() {
  const { isSignedIn } = useAuth();

  if (isSignedIn) {
    return (
      <a href="#capabilities" className="landing-btn-ghost landing-btn-lg">
        Explore capabilities
      </a>
    );
  }

  return (
    <SignInButton mode="modal" forceRedirectUrl="/" fallbackRedirectUrl="/">
      <button type="button" className="landing-btn-ghost landing-btn-lg">
        Sign in
      </button>
    </SignInButton>
  );
}

function ClosingSignIn() {
  const { isSignedIn } = useAuth();
  if (isSignedIn) return null;
  return (
    <SignInButton mode="modal" forceRedirectUrl="/" fallbackRedirectUrl="/">
      <button type="button" className="landing-btn-ghost landing-btn-lg">
        Sign in
      </button>
    </SignInButton>
  );
}

const steps = [
  {
    icon: ShieldCheck,
    title: "Scope the request",
    body: "A parallel guardrail checks travel intent before anything else runs — off-topic noise never reaches your tools.",
  },
  {
    icon: Workflow,
    title: "Route the work",
    body: "A decision graph fans queries to hotel, flight, web search, or general Q&A agents — only the specialists you need.",
  },
  {
    icon: Sparkles,
    title: "Stream the plan",
    body: "Watch chain-of-thought live while BookMe merges results into a clear itinerary you can act on.",
  },
];

const capabilities = [
  {
    icon: Plane,
    title: "Flights",
    body: "Search and book routes with live availability through MCP-backed flight tools.",
  },
  {
    icon: Hotel,
    title: "Hotels",
    body: "Find stays that match dates, budget, and location — then book without leaving chat.",
  },
  {
    icon: Search,
    title: "Live research",
    body: "Tavily-powered web search for neighborhoods, events, weather, and trip context.",
  },
];

export default function LandingPage({ authMode }: { authMode: AuthMode }) {
  const primaryLabel = "Plan a trip";

  return (
    <div className="landing-root min-h-full text-slate-100">
      <LandingNav authMode={authMode} />

      <section className="relative min-h-[100svh] flex items-end overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="/images/hero-dusk.jpg"
            alt=""
            className="h-full w-full object-cover object-center scale-105 animate-hero-drift"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-[#050816]/55 via-[#050816]/35 to-[#050816]" />
          <div className="absolute inset-0 bg-gradient-to-r from-[#050816]/80 via-[#0b1230]/35 to-transparent" />
          <AuroraField className="opacity-50 mix-blend-screen" />
        </div>

        <div className="relative z-10 w-full mx-auto max-w-6xl px-4 sm:px-6 pb-16 pt-32 sm:pb-24">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={{
              hidden: {},
              visible: { transition: { staggerChildren: 0.11 } },
            }}
            className="max-w-2xl"
          >
            <motion.div
              variants={{
                hidden: { opacity: 0, y: 18 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
                },
              }}
              className="mb-6"
            >
              <BookMeLogo size="hero" />
            </motion.div>
            <motion.p
              variants={{
                hidden: { opacity: 0, y: 18 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
                },
              }}
              className="font-display text-5xl sm:text-7xl md:text-8xl tracking-tight text-white leading-[0.95]"
            >
              BookMe
              <span className="block bg-gradient-to-r from-violet-300 via-blue-200 to-sky-300 bg-clip-text text-transparent">
                AI
              </span>
            </motion.p>

            <motion.h1
              variants={{
                hidden: { opacity: 0, y: 18 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
                },
              }}
              className="mt-6 text-xl sm:text-2xl font-medium text-slate-100/95 tracking-tight max-w-xl"
            >
              Multi-agent travel planning that books flights, finds hotels, and
              researches the trip — in one conversation.
            </motion.h1>

            <motion.p
              variants={{
                hidden: { opacity: 0, y: 18 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
                },
              }}
              className="mt-4 text-base sm:text-lg text-slate-300/90 max-w-lg leading-relaxed"
            >
              Built on a parallel decision graph and MCP tool servers — so every
              answer stays on-scope, fast, and grounded in live data.
            </motion.p>

            <motion.div
              variants={{
                hidden: { opacity: 0, y: 18 },
                visible: {
                  opacity: 1,
                  y: 0,
                  transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] },
                },
              }}
              className="mt-9 flex flex-wrap items-center gap-3"
            >
              {authMode === "dev" ? (
                <DevPrimaryCta label={primaryLabel} />
              ) : (
                <ClerkPrimaryCta label={primaryLabel} />
              )}
              {authMode === "dev" ? <DevSecondaryCta /> : <ClerkSecondaryCta />}
            </motion.div>
          </motion.div>
        </div>
      </section>

      <section id="how" className="relative py-24 sm:py-32">
        <div className="absolute inset-0 bg-[#070b18]" />
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-violet-500/40 to-transparent" />
        <div className="relative mx-auto max-w-6xl px-4 sm:px-6">
          <Reveal>
            <p className="text-sm font-medium tracking-wide text-violet-300/90 uppercase">
              How it works
            </p>
            <h2 className="mt-3 font-display text-3xl sm:text-5xl tracking-tight text-white max-w-xl">
              Guard. Route. Deliver.
            </h2>
            <p className="mt-4 text-slate-400 max-w-xl text-base sm:text-lg leading-relaxed">
              BookMe doesn’t dump every query into one model. A decision graph
              runs scope filtering and intent routing in parallel, then fans out
              only the agents that matter.
            </p>
          </Reveal>

          <Stagger className="mt-14 grid gap-10 sm:grid-cols-3">
            {steps.map((step, i) => (
              <StaggerItem key={step.title}>
                <div className="relative">
                  <div className="flex items-center gap-3 mb-4">
                    <span className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500/20 to-blue-600/20 border border-white/10 text-blue-200">
                      <step.icon size={18} />
                    </span>
                    <span className="font-mono text-xs text-slate-500">
                      0{i + 1}
                    </span>
                  </div>
                  <h3 className="font-display text-xl text-white tracking-tight">
                    {step.title}
                  </h3>
                  <p className="mt-2 text-sm sm:text-[15px] text-slate-400 leading-relaxed">
                    {step.body}
                  </p>
                </div>
              </StaggerItem>
            ))}
          </Stagger>
        </div>
      </section>

      <section
        id="capabilities"
        className="relative py-24 sm:py-32 overflow-hidden"
      >
        <div className="absolute inset-0 bg-[#050816]" />
        <AnimatedGradientBackground
          className="opacity-70"
          breathing
          startingGap={130}
          breathingRange={8}
        />
        <div className="relative mx-auto max-w-6xl px-4 sm:px-6">
          <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
            <Reveal>
              <p className="text-sm font-medium tracking-wide text-blue-300/90 uppercase">
                Capabilities
              </p>
              <h2 className="mt-3 font-display text-3xl sm:text-5xl tracking-tight text-white">
                Everything a trip needs — without leaving chat.
              </h2>
              <p className="mt-4 text-slate-400 text-base sm:text-lg leading-relaxed">
                Specialized MCP servers for flights, hotels, and live web search
                plug into a LangGraph orchestrator. You ask; BookMe coordinates.
              </p>

              <ul className="mt-10 space-y-8">
                {capabilities.map((cap) => (
                  <li key={cap.title} className="flex gap-4">
                    <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-lg border border-white/10 bg-white/[0.04] text-violet-200">
                      <cap.icon size={16} />
                    </span>
                    <div>
                      <h3 className="font-display text-lg text-white">
                        {cap.title}
                      </h3>
                      <p className="mt-1 text-sm text-slate-400 leading-relaxed">
                        {cap.body}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            </Reveal>

            <Reveal delay={0.12} className="relative">
              <div className="relative overflow-hidden rounded-2xl border border-white/10 shadow-[0_40px_80px_-40px_rgba(79,70,229,0.55)]">
                <img
                  src="/images/product-visual.jpg"
                  alt="Abstract view of BookMe coordinating flights and hotels"
                  className="w-full aspect-[16/10] object-cover"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#050816]/70 via-transparent to-transparent" />
              </div>
              <div
                className="pointer-events-none absolute -inset-8 -z-10 rounded-full bg-violet-600/20 blur-3xl"
                aria-hidden
              />
            </Reveal>
          </div>
        </div>
      </section>

      <section className="relative py-24 sm:py-28">
        <div className="absolute inset-0 bg-[#070b18]" />
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-blue-500/35 to-transparent" />
        <div className="relative mx-auto max-w-3xl px-4 sm:px-6 text-center">
          <Reveal>
            <h2 className="font-display text-3xl sm:text-5xl tracking-tight text-white">
              Ready when you are.
            </h2>
            <p className="mt-4 text-slate-400 text-base sm:text-lg leading-relaxed">
              Sign in, open the assistant, and start with a destination — BookMe
              handles the rest.
            </p>
            <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
              {authMode === "dev" ? (
                <DevPrimaryCta label="Get started" />
              ) : (
                <>
                  <ClerkPrimaryCta label="Get started" />
                  <ClosingSignIn />
                </>
              )}
            </div>
          </Reveal>
        </div>
      </section>

      <footer className="relative border-t border-white/[0.06] bg-[#050816] py-10">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-slate-500">
          <p className="font-display text-slate-300">
            BookMe<span className="text-violet-300"> AI</span>
          </p>
          <p>Travel planning with agents, tools, and live data.</p>
        </div>
      </footer>
    </div>
  );
}
