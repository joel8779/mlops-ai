"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Loader2, Plus, RefreshCcw, Menu, X, LogOut, Home, UserSearch, MessageSquare, UploadCloud, BriefcaseBusiness, BarChart3, Target } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { jobsApi } from "@/lib/api";
import { fadeInUp } from "@/lib/animations";

export default function JobsPage() {
  const { user, logout } = useAuth();
  const [jobs, setJobs] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const loadJobs = async () => {
    setLoading(true);
    setError("");
    try {
      setJobs((await jobsApi.list()) as any[]);
    } catch (err: any) {
      setError(err.message || "Failed to load jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const createJob = async (event: React.FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await jobsApi.create({ title, description, status: "active" });
      setTitle("");
      setDescription("");
      await loadJobs();
    } catch (err: any) {
      setError(err.message || "Failed to create job");
    } finally {
      setSaving(false);
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
          <div className="text-sm text-foreground-muted">Jobs</div>
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
                  item.href === "/jobs" ? "bg-accent text-white" : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
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
          <h1 className="text-xl font-semibold text-foreground">Job Descriptions</h1>
        </div>

        <section className="p-6">
          <motion.div {...fadeInUp} className="grid gap-6 lg:grid-cols-[1fr_380px]">
            <div className="rounded-xl bg-background-card border border-background-border p-4">
              <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-foreground">Active roles</h2>
                <button onClick={loadJobs} className="rounded-lg border border-background-border p-2 hover:border-accent/50 transition-colors" aria-label="Refresh jobs">
                  <RefreshCcw size={16} className="text-foreground-muted" />
                </button>
              </div>
              {error && <div className="mt-3 rounded-lg bg-error/10 border border-error/20 p-3 text-sm text-error">{error}</div>}
              <div className="mt-3 divide-y divide-background-border text-sm">
                {loading ? (
                  <div className="flex items-center py-6 text-foreground-muted">
                    <Loader2 className="mr-2 animate-spin" size={16} />
                    Loading roles
                  </div>
                ) : jobs.length === 0 ? (
                  <div className="py-6 text-foreground-muted">No roles yet. Create one to rank candidates.</div>
                ) : (
                  jobs.map((job) => (
                    <div key={job.id} className="flex items-center justify-between gap-3 py-3">
                      <div>
                        <div className="font-medium text-foreground">{job.title}</div>
                        <div className="text-xs text-foreground-muted">
                          {(job.required_skills || []).slice(0, 4).join(", ") || "Parsing pending"}
                        </div>
                      </div>
                      <span className="rounded-lg bg-background-elevated px-2 py-1 text-xs text-foreground-muted">{job.status}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
            <form onSubmit={createJob} className="rounded-xl bg-background-card border border-background-border p-4">
              <h2 className="text-sm font-semibold text-foreground">Create job</h2>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                className="mt-3 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
                placeholder="Title"
                required
              />
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                className="mt-3 min-h-48 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
                placeholder="Paste job description"
                required
              />
              <button
                disabled={saving}
                className="mt-3 inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 disabled:opacity-60 transition-colors"
              >
                {saving ? <Loader2 className="animate-spin" size={16} /> : <Plus size={16} />}
                Parse and index
              </button>
            </form>
          </motion.div>
        </section>
      </main>
    </div>
  );
}
