"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  Bookmark, 
  Loader2, 
  MessageSquare, 
  RefreshCcw, 
  Star,
  Sparkles,
  TrendingUp,
  User,
  Briefcase,
  GraduationCap,
  ArrowUpRight,
  Search,
  Filter,
  MoreVertical,
  Menu,
  Home,
  FileText,
  Settings,
  BarChart3
} from "lucide-react";
import { candidatesApi, feedbackApi } from "@/lib/api";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function CandidatesPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [savingId, setSavingId] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [authLoading, user, router]);

  const loadCandidates = async () => {
    setLoading(true);
    setError("");
    try {
      setCandidates((await candidatesApi.list()) as any[]);
    } catch (err: any) {
      setError(err.message || "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user) {
      loadCandidates();
    }
  }, [user]);

  const recordFeedback = async (candidateId: string, action: string) => {
    setSavingId(candidateId);
    try {
      await feedbackApi.ranking({ candidate_id: candidateId, action });
    } catch (err: any) {
      setError(err.message || "Failed to save feedback");
    } finally {
      setSavingId(null);
    }
  };

  const sidebarItems = [
    { icon: Home, label: "Dashboard", href: "/dashboard", active: false },
    { icon: User, label: "Candidates", href: "/candidates", active: true },
    { icon: Briefcase, label: "Jobs", href: "/jobs", active: false },
    { icon: FileText, label: "Resumes", href: "/resumes", active: false },
    { icon: Search, label: "Search", href: "/search", active: false },
    { icon: MessageSquare, label: "AI Copilot", href: "/copilot", active: false },
    { icon: BarChart3, label: "Analytics", href: "/analytics", active: false },
    { icon: Settings, label: "Settings", href: "/settings", active: false },
  ];

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="flex h-full flex-col">
          <div className="flex items-center justify-between p-6 border-b border-background-border">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="font-bold text-lg">Resume AI</div>
                <div className="text-xs text-foreground-muted">Intelligent Hiring</div>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-foreground-muted hover:text-foreground"
            >
              <MoreVertical className="h-5 w-5" />
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                      item.active
                        ? "bg-accent/10 text-foreground border border-accent/30"
                        : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>

          <div className="p-4 border-t border-background-border">
            <div className="flex items-center gap-3 rounded-lg bg-background-elevated p-3">
              <div className="h-10 w-10 rounded-full bg-accent/20" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{user?.email || "User"}</div>
                <div className="text-xs text-foreground-muted">Recruiter</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 border-b border-background-border bg-background/80 backdrop-blur-xl">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-foreground-muted hover:text-foreground"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold">Candidates</h1>
                <p className="text-sm text-foreground-muted">AI-ranked profiles with semantic matching</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={loadCandidates}
                className="inline-flex items-center gap-2 rounded-lg bg-background-card border border-background-border px-4 py-2 hover:bg-background-elevated transition-colors"
              >
                <RefreshCcw className="h-4 w-4" />
                Refresh
              </button>
            </div>
          </div>
        </header>

        <main className="p-6">
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 rounded-xl bg-error/10 border border-error/20 px-6 py-4 text-sm text-error"
            >
              {error}
            </motion.div>
          )}

          {loading ? (
            <div className="flex items-center justify-center p-20">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent"
              />
            </div>
          ) : candidates.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-xl bg-background-card border border-background-border p-12 text-center"
            >
              <div className="inline-flex h-16 w-16 items-center justify-center rounded-lg bg-accent/10 mb-4">
                <User className="h-8 w-8 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-2">No candidates yet</h3>
              <p className="text-foreground-muted mb-6">Upload resumes to start building your AI-powered pipeline</p>
              <Link
                href="/resumes"
                className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 font-semibold hover:bg-accent/90 transition-colors"
              >
                Upload Resume
                <ArrowUpRight className="h-5 w-5" />
              </Link>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid gap-6"
            >
              {candidates.map((candidate, i) => (
                <motion.div
                  key={candidate.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="group rounded-xl bg-background-card border border-background-border p-6 hover:border-accent/50 transition-colors"
                >
                  <div className="flex gap-6">
                    {/* Avatar */}
                    <div className="flex-shrink-0">
                      <div className="h-16 w-16 rounded-lg bg-accent/20 flex items-center justify-center text-2xl font-bold text-accent">
                        {candidate.full_name?.charAt(0) || "?"}
                      </div>
                    </div>

                    {/* Main Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-3">
                        <div>
                          <Link
                            href={`/candidates/${candidate.id}`}
                            className="text-xl font-semibold text-foreground hover:text-accent transition-colors"
                          >
                            {candidate.full_name || "Unnamed candidate"}
                          </Link>
                          <div className="text-sm text-foreground-muted mt-1">
                            {candidate.headline || candidate.email}
                          </div>
                        </div>
                        
                        {/* AI Score */}
                        <div className="flex-shrink-0 text-right">
                          <div className="inline-flex items-center gap-2 rounded-lg bg-accent/10 border border-accent/20 px-4 py-2">
                            <Star className="h-5 w-5 text-accent fill-accent" />
                            <span className="text-2xl font-bold text-accent">
                              {candidate.best_match_score ? Math.round(candidate.best_match_score) : "N/A"}
                            </span>
                            <span className="text-sm text-accent-subtle">AI Score</span>
                          </div>
                        </div>
                      </div>

                      {/* Skills */}
                      <div className="mb-4">
                        <div className="text-sm text-foreground-muted mb-2">Skills</div>
                        <div className="flex flex-wrap gap-2">
                          {(candidate.skills?.slice(0, 8) || []).map((skill: string, j: number) => (
                            <span
                              key={j}
                              className="inline-flex items-center rounded-lg bg-background-elevated border border-background-border px-3 py-1 text-sm text-foreground"
                            >
                              {skill}
                            </span>
                          ))}
                          {(!candidate.skills || candidate.skills.length === 0) && (
                            <span className="text-sm text-foreground-subtle">Pending extraction</span>
                          )}
                        </div>
                      </div>

                      {/* Stage & Actions */}
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="inline-flex items-center gap-2 rounded-lg bg-background-elevated border border-background-border px-3 py-1.5 text-sm">
                            <TrendingUp className="h-4 w-4 text-accent" />
                            <span className="text-foreground">{candidate.current_stage || candidate.latest_resume_status || "New"}</span>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => recordFeedback(candidate.id, "shortlist")}
                            disabled={savingId === candidate.id}
                            className="inline-flex items-center gap-2 rounded-lg bg-background-card border border-background-border px-4 py-2 text-sm hover:bg-background-elevated hover:border-accent/50 transition-colors disabled:opacity-50"
                          >
                            {savingId === candidate.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Bookmark className="h-4 w-4" />
                            )}
                            Shortlist
                          </button>
                          <button
                            onClick={() => recordFeedback(candidate.id, "interview")}
                            disabled={savingId === candidate.id}
                            className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm hover:bg-accent/90 transition-colors disabled:opacity-50"
                          >
                            {savingId === candidate.id ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <MessageSquare className="h-4 w-4" />
                            )}
                            Interview
                          </button>
                          <Link
                            href={`/candidates/${candidate.id}`}
                            className="inline-flex items-center justify-center rounded-lg bg-background-card border border-background-border px-3 py-2 hover:bg-background-elevated transition-colors"
                          >
                            <ArrowUpRight className="h-5 w-5" />
                          </Link>
                        </div>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          )}
        </main>
      </div>
    </div>
  );
}
