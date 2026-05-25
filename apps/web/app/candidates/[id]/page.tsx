"use client";

import { use, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Bot, FileText, Loader2, Sparkles, Menu, X, LogOut, Home, UserSearch, MessageSquare, UploadCloud, BriefcaseBusiness, BarChart3, Target } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { aiApi, atsApi, candidatesApi } from "@/lib/api";
import { fadeInUp } from "@/lib/animations";

export default function CandidateProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { user, logout } = useAuth();
  const { id } = use(params);
  const [candidate, setCandidate] = useState<any>(null);
  const [summary, setSummary] = useState("");
  const [atsScore, setAtsScore] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = (await candidatesApi.get(id)) as any;
        setCandidate(data);
      } catch (err: any) {
        setError(err.message || "Failed to load candidate");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id]);

  const generateSummary = async () => {
    setAiLoading(true);
    setError("");
    try {
      const response = (await aiApi.summary(id)) as any;
      setSummary(response.answer);
    } catch (err: any) {
      setError(err.message || "Failed to generate summary");
    } finally {
      setAiLoading(false);
    }
  };

  const scoreResume = async () => {
    if (!candidate?.latest_resume_id) return;
    setAiLoading(true);
    setError("");
    try {
      setAtsScore(await atsApi.scoreResume(candidate.latest_resume_id));
    } catch (err: any) {
      setError(err.message || "Failed to score resume");
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="border-b border-background-border px-6 py-4">
          <div className="text-lg font-semibold text-foreground">Resume AI</div>
          <div className="text-sm text-foreground-muted">Candidates</div>
        </div>
        <nav className="space-y-1 p-4">
          {[
            { href: "/dashboard", label: "Dashboard", icon: Home },
            { href: "/candidates", label: "Candidates", icon: UserSearch },
            { href: "/search", label: "Search", icon: Target },
            { href: "/resumes", label: "Uploads", icon: UploadCloud },
            { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
            { href: "/analytics", label: "Analytics", icon: BarChart3 },
            { href: "/copilot", label: "Copilot", icon: MessageSquare }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm transition-colors ${
                  item.href === "/candidates" ? "bg-accent text-white" : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </a>
            );
          })}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 border-t border-background-border p-4">
          <button
            onClick={() => logout()}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm text-foreground-muted hover:bg-background-elevated hover:text-foreground transition-colors"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </motion.div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      {/* Main content */}
      <main className="lg:pl-72">
        <div className="border-b border-background-border bg-background-card px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-background-elevated transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h1 className="text-xl font-semibold text-foreground">{candidate?.full_name || "Candidate Profile"}</h1>
        </div>

        <section className="p-6">
          <motion.div {...fadeInUp} className="grid gap-6 lg:grid-cols-[1fr_360px]">
            {loading ? (
              <div className="rounded-xl bg-background-card border border-background-border p-8 text-sm text-foreground-muted">
                <Loader2 className="mr-2 inline animate-spin" size={16} />
                Loading candidate
              </div>
            ) : error ? (
              <div className="rounded-xl bg-error/10 border border-error/20 p-5 text-sm text-error">{error}</div>
            ) : (
            <article className="rounded-xl bg-background-card border border-background-border p-5">
              <div className="flex items-center justify-between gap-3">
                <h2 className="text-lg font-semibold text-foreground">Candidate intelligence</h2>
                <div className="flex gap-2">
                  <button
                    onClick={generateSummary}
                    disabled={aiLoading}
                    className="inline-flex items-center gap-2 rounded-lg bg-accent px-3 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60 transition-colors"
                  >
                    {aiLoading ? <Loader2 className="animate-spin" size={16} /> : <Bot size={16} />}
                    Summarize
                  </button>
                  <button
                    onClick={scoreResume}
                    disabled={aiLoading || !candidate?.latest_resume_id}
                    className="inline-flex items-center gap-2 rounded-lg border border-background-border px-3 py-2 text-sm hover:border-accent/50 disabled:opacity-60 transition-colors"
                  >
                    <FileText size={16} className="text-foreground-muted" />
                    ATS
                  </button>
                </div>
              </div>
              <p className="mt-3 text-sm leading-6 text-foreground-muted">
                {summary || candidate?.summary || "Generate an AI summary to review this candidate."}
              </p>
              {atsScore && (
                <div className="mt-4 rounded-lg border border-accent/20 bg-accent/10 p-3 text-sm">
                  <div className="flex items-center gap-2 font-medium">
                    <Sparkles size={16} className="text-accent" />
                    ATS score: {Math.round(atsScore.ats_score)}
                  </div>
                </div>
              )}
              <div className="mt-5 grid gap-3 md:grid-cols-3">
                {(candidate?.skills || []).slice(0, 9).map((skill: string) => (
                  <span key={skill} className="rounded-lg bg-background-elevated px-3 py-2 text-sm text-foreground-muted">{skill}</span>
                ))}
              </div>
              {candidate?.resume_text_preview && (
                <div className="mt-5 rounded-lg border border-background-border bg-background-elevated p-4">
                  <h3 className="text-sm font-semibold text-foreground">Resume preview</h3>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-foreground-muted">
                    {candidate.resume_text_preview}
                  </p>
                </div>
              )}
            </article>
            )}
            <div className="rounded-xl bg-background-card border border-background-border p-6">
              <h3 className="text-sm font-semibold text-foreground mb-4">AI ranking composition</h3>
              <div className="space-y-3">
                {[
                  { label: "Semantic", value: 38, color: "bg-accent" },
                  { label: "Skills", value: 24, color: "bg-accent/70" },
                  { label: "Experience", value: 14, color: "bg-accent/50" },
                  { label: "ATS", value: 11, color: "bg-accent/30" }
                ].map((segment) => (
                  <div key={segment.label} className="flex items-center justify-between text-sm">
                    <span className="text-foreground">{segment.label}</span>
                    <span className="font-medium text-accent">{segment.value}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 flex h-3 overflow-hidden rounded-full bg-background-border">
                {[
                  { width: "38%", color: "bg-accent" },
                  { width: "24%", color: "bg-accent/70" },
                  { width: "14%", color: "bg-accent/50" },
                  { width: "11%", color: "bg-accent/30" }
                ].map((bar, i) => (
                  <div key={i} className={`h-full ${bar.color}`} style={{ width: bar.width }} />
                ))}
              </div>
            </div>
          </motion.div>
        </section>
      </main>
    </div>
  );
}
