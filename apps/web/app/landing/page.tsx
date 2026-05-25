"use client";

import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Bot,
  BrainCircuit,
  BriefcaseBusiness,
  Cpu,
  FileText,
  GitBranch,
  Radar,
  ScanLine,
  Search,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

const capabilities = [
  { icon: FileText, title: "Ingest resumes", description: "Upload PDFs and DOCX files into a tracked candidate intelligence pipeline." },
  { icon: Search, title: "Search semantically", description: "Query skills, intent, experience, and context beyond simple keywords." },
  { icon: BrainCircuit, title: "Extract signals", description: "Turn documents into profiles, skills, summaries, and match-ready records." },
  { icon: Bot, title: "Orchestrate AI", description: "Expose candidate reasoning, ranking signals, interview prep, and operational context." },
];

const flow = ["Document intake", "OCR scan", "Profile parse", "Embedding", "Index ready"];

export default function LandingPage() {
  return (
    <div className="neural-bg min-h-screen text-foreground">
      <div className="pointer-events-none fixed inset-0 ops-grid opacity-70" />
      <nav className="sticky top-0 z-50 border-b border-white/10 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 lg:px-8">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 shadow-glow">
              <Radar className="h-5 w-5 text-accent" />
            </div>
            <div>
              <div className="font-semibold tracking-wide">NEURAL OPS</div>
              <div className="text-[10px] uppercase tracking-[0.28em] text-foreground-subtle">Recruiting Command</div>
            </div>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login" className="rounded-lg px-3 py-2 text-sm text-foreground-muted hover:text-foreground">
              Sign In
            </Link>
            <Link href="/signup" className="ops-button inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <main className="relative">
        <section className="mx-auto grid min-h-[calc(100vh-4rem)] max-w-7xl items-center gap-10 px-5 py-16 lg:grid-cols-[1fr_0.92fr] lg:px-8">
          <div>
            <div className="ops-chip inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs uppercase tracking-[0.22em]">
              <ShieldCheck className="h-3.5 w-3.5 text-accent" />
              AI recruiting operations system
            </div>
            <h1 className="mt-7 max-w-4xl text-5xl font-semibold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
              NEURAL OPS
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-foreground-muted">
              A cyberpunk recruiting command center for document ingestion, semantic talent search, AI candidate intelligence, and live hiring operations.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link href="/signup" className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-6 py-3 text-sm font-semibold">
                Enter Command Center
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link href="/login" className="ops-button-secondary inline-flex items-center justify-center rounded-lg px-6 py-3 text-sm font-semibold">
                Operator Sign In
              </Link>
            </div>
          </div>

          <div className="ops-panel-strong scanline holo-border rounded-xl p-5">
            <div className="mb-5 flex items-center justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.24em] text-foreground-subtle">Mission preview</div>
                <div className="mt-1 text-lg font-semibold">Recruiting Mission Control</div>
              </div>
              <div className="rounded-full border border-success/30 bg-success/10 px-3 py-1 text-xs text-success">LIVE</div>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {[
                ["Pipeline", "backend"],
                ["Search", "semantic"],
                ["Copilot", "online"],
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg border border-white/10 bg-white/[0.035] p-4">
                  <div className="text-xs text-foreground-subtle">{label}</div>
                  <div className="mt-2 text-sm font-medium text-accent">{value}</div>
                </div>
              ))}
            </div>
            <div className="mt-4 rounded-lg border border-white/10 bg-background/60 p-4">
              <div className="mb-4 flex items-center gap-2 text-sm font-medium">
                <ScanLine className="h-4 w-4 text-accent" />
                Candidate intelligence flow
              </div>
              <div className="space-y-3">
                {flow.map((step, index) => (
                  <div key={step} className="flex items-center gap-3">
                    <div className="flex h-7 w-7 items-center justify-center rounded-md border border-accent/20 bg-accent/10 text-xs text-accent">
                      {index + 1}
                    </div>
                    <div className="flex-1 rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-foreground-muted">{step}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="border-y border-white/10 bg-background/40 px-5 py-20 backdrop-blur-md lg:px-8">
          <div className="mx-auto max-w-7xl">
            <div className="max-w-2xl">
              <div className="text-xs uppercase tracking-[0.28em] text-accent">AI recruiting capabilities</div>
              <h2 className="mt-3 text-3xl font-semibold">Built for operational recruiters, not demo dashboards.</h2>
            </div>
            <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {capabilities.map((capability) => {
                const Icon = capability.icon;
                return (
                  <div key={capability.title} className="ops-panel holo-border rounded-xl p-5 transition-transform hover:-translate-y-1">
                    <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-accent/20 bg-accent/10">
                      <Icon className="h-5 w-5 text-accent" />
                    </div>
                    <h3 className="mt-5 font-semibold">{capability.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-foreground-muted">{capability.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        <section className="px-5 py-20 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-3">
            <div className="ops-panel rounded-xl p-6 lg:col-span-2">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-foreground-subtle">
                <Search className="h-4 w-4 text-accent" />
                Semantic search showcase
              </div>
              <div className="mt-5 rounded-lg border border-accent/20 bg-background/70 p-4 font-mono text-sm text-accent">
                find senior backend engineers with distributed systems, python, and hiring-stage readiness
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-3">
                {["Context match", "Skill vector", "Role signal"].map((label, index) => (
                  <div key={label} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                    <div className="text-xs text-foreground-subtle">{label}</div>
                    <div className="mt-3 h-1.5 rounded-full bg-white/10">
                      <div className="h-full rounded-full bg-accent" style={{ width: `${84 - index * 12}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="ops-panel rounded-xl p-6">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.24em] text-foreground-subtle">
                <GitBranch className="h-4 w-4 text-violet" />
                Orchestration
              </div>
              <div className="mt-5 space-y-3">
                {["Upload", "Parse", "Rank", "Brief recruiter"].map((item) => (
                  <div key={item} className="rounded-lg border border-white/10 bg-white/[0.03] px-4 py-3 text-sm text-foreground-muted">
                    {item}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="border-t border-white/10 px-5 py-20 text-center lg:px-8">
          <Sparkles className="mx-auto h-7 w-7 text-accent" />
          <h2 className="mt-4 text-3xl font-semibold">Activate the recruiting operating system.</h2>
          <p className="mx-auto mt-3 max-w-2xl text-foreground-muted">
            Sign up, upload resumes, and let Neural Ops populate the command center from real backend workflows.
          </p>
          <Link href="/signup" className="ops-button mt-8 inline-flex items-center justify-center gap-2 rounded-lg px-6 py-3 text-sm font-semibold">
            Launch Neural Ops
            <Cpu className="h-4 w-4" />
          </Link>
        </section>
      </main>
    </div>
  );
}
