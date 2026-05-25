"use client";

import { 
  Search, 
  FileText, 
  MessageSquare, 
  Scan, 
  ArrowRight,
  Check,
  Terminal,
  Database,
  Layers,
  Shield,
  Activity
} from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navbar */}
      <nav className="sticky top-0 z-50 border-b border-background-border bg-background/95 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <Terminal className="h-6 w-6 text-foreground-muted" />
              <span className="text-xl font-semibold tracking-tight">Resume Intelligence</span>
            </div>
            <div className="flex items-center gap-6">
              <Link
                href="/sign-in"
                className="text-sm text-foreground-muted hover:text-foreground transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="inline-flex items-center justify-center rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-6 py-32 lg:px-8">
        <div className="mx-auto max-w-4xl">
          <div className="text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-md bg-background-card border border-background-border px-3 py-1.5 text-sm text-foreground-muted">
              <Activity className="h-4 w-4" />
              <span>Operational Intelligence for Recruiting</span>
            </div>
            
            <h1 className="mb-6 text-5xl font-semibold tracking-tight lg:text-6xl">
              Intelligence infrastructure for modern recruiting teams
            </h1>
            
            <p className="mx-auto mb-10 max-w-2xl text-lg text-foreground-muted leading-relaxed">
              Semantic search, AI-powered candidate ranking, and intelligent document analysis. 
              Built for enterprise recruiting operations.
            </p>
            
            <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
              <Link
                href="/sign-up"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-foreground text-background px-8 py-3 text-base font-medium hover:bg-foreground/90 transition-colors"
              >
                Start Building
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="#capabilities"
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-background-card border border-background-border px-8 py-3 text-base font-medium hover:bg-background-elevated transition-colors"
              >
                View Capabilities
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Product Capabilities */}
      <section id="capabilities" className="px-6 py-24 lg:px-8">
        <div className="mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-semibold mb-4">Core Capabilities</h2>
            <p className="text-lg text-foreground-muted max-w-2xl mx-auto">
              Enterprise-grade infrastructure for recruiting operations
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: Search,
                title: "Semantic Search",
                description: "Find candidates by intent, not keywords. Natural language queries with vector-based matching."
              },
              {
                icon: Database,
                title: "Candidate Intelligence",
                description: "AI-powered ranking, skill extraction, and experience parsing from resume documents."
              },
              {
                icon: Scan,
                title: "Document Processing",
                description: "OCR and intelligent extraction from PDF, DOCX, and image-based resumes."
              },
              {
                icon: MessageSquare,
                title: "AI Copilot",
                description: "Context-aware assistance for candidate evaluation, interview prep, and hiring decisions."
              },
              {
                icon: Layers,
                title: "Pipeline Management",
                description: "Structured hiring funnel with stage tracking, workflow automation, and analytics."
              },
              {
                icon: Shield,
                title: "Enterprise Security",
                description: "SSO, role-based access, audit logging, and data encryption for team collaboration."
              }
            ].map((capability, i) => (
              <div
                key={i}
                className="rounded-lg bg-background-card border border-background-border p-6 hover:border-background-border/80 transition-colors"
              >
                <div className="mb-4 inline-flex h-10 w-10 items-center justify-center rounded-md bg-background-elevated">
                  <capability.icon className="h-5 w-5 text-foreground-muted" />
                </div>
                <h3 className="mb-2 text-base font-medium">{capability.title}</h3>
                <p className="text-sm text-foreground-muted leading-relaxed">{capability.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Infrastructure Section */}
      <section className="px-6 py-24 lg:px-8 border-t border-background-border">
        <div className="mx-auto max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-semibold mb-4">Infrastructure</h2>
            <p className="text-base text-foreground-muted">
              Built for scale, security, and reliability
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <h3 className="text-base font-medium mb-4">Data Processing</h3>
              <ul className="space-y-3 text-sm text-foreground-muted">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>Vector embeddings for semantic search</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>OCR pipeline for document extraction</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>Async worker queues for processing</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>PostgreSQL for structured data</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-base font-medium mb-4">Security & Compliance</h3>
              <ul className="space-y-3 text-sm text-foreground-muted">
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>End-to-end encryption in transit</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>Role-based access control</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>Audit logging for all operations</span>
                </li>
                <li className="flex items-start gap-2">
                  <Check className="h-4 w-4 text-foreground-muted flex-shrink-0 mt-0.5" />
                  <span>SSO integration ready</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="px-6 py-24 lg:px-8 border-t border-background-border">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-semibold mb-4">Get Started</h2>
          <p className="text-lg text-foreground-muted mb-8">
            Deploy your recruiting intelligence infrastructure
          </p>
          <Link
            href="/sign-up"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-foreground text-background px-8 py-3 text-base font-medium hover:bg-foreground/90 transition-colors"
          >
            Start Building
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="px-6 py-12 lg:px-8 border-t border-background-border">
        <div className="mx-auto max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Terminal className="h-5 w-5 text-foreground-muted" />
              <span className="text-sm text-foreground-muted">Resume Intelligence</span>
            </div>
            <div className="text-sm text-foreground-muted">
              © 2025 Resume Intelligence. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
