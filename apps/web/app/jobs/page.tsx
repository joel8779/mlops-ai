"use client";

import { FormEvent, useEffect, useState } from "react";
import { BriefcaseBusiness, Loader2, Plus, RefreshCcw } from "lucide-react";
import AppShell from "@/components/app-shell";
import { jobsApi, workspaceApi } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [workspace, setWorkspace] = useState<any>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const loadJobs = async () => {
    setLoading(true);
    setError("");
    try {
      const [jobData, workspaceData] = await Promise.all([jobsApi.list(), workspaceApi.activation()]);
      setJobs(jobData as any[]);
      setWorkspace(workspaceData);
    } catch (err: any) {
      setError(err.message || "Unable to load jobs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const createJob = async (event: FormEvent) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await jobsApi.create({ title, description, status: "active" });
      setTitle("");
      setDescription("");
      await loadJobs();
    } catch (err: any) {
      setError(err.message || "Unable to create job");
    } finally {
      setSaving(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="ops-panel-strong rounded-xl p-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.28em] text-accent">Role command deck</div>
            <h1 className="mt-2 text-xl font-semibold">Jobs</h1>
            <p className="text-sm text-foreground-muted">Create job descriptions for matching and ATS scoring context.</p>
          </div>
          <button onClick={loadJobs} className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm">
            <RefreshCcw className="h-4 w-4" />
            Refresh
          </button>
        </div>
        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
          <section className="ops-panel rounded-xl p-5">
            <h2 className="text-base font-semibold">Active roles</h2>
            {loading ? (
              <div className="mt-6 flex items-center gap-2 text-sm text-foreground-muted">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading jobs
              </div>
            ) : jobs.length === 0 ? (
              <div className="mt-6 rounded-lg border border-white/10 bg-white/[0.03] p-6 text-sm text-foreground-muted">
                No jobs yet. Create a role to rank candidates and generate matching context.
              </div>
            ) : (
              <div className="mt-4 divide-y divide-white/10">
                {jobs.map((job) => (
                  <div key={job.id} className="py-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-medium">{job.title}</div>
                        <div className="mt-1 text-xs text-foreground-muted">{job.status}</div>
                      </div>
                      <BriefcaseBusiness className="h-5 w-5 text-foreground-muted" />
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {(job.required_skills || []).slice(0, 8).map((skill: string) => (
                        <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
          <section className="ops-panel rounded-xl p-5 lg:col-span-2">
            <h2 className="text-base font-semibold">Candidate matches</h2>
            <div className="mt-4 grid gap-3 md:grid-cols-2">
              {(workspace?.match_insights || []).length === 0 ? (
                <div className="rounded-lg border border-white/10 bg-white/[0.03] p-4 text-sm text-foreground-muted">
                  No job-specific candidate matches yet. Create roles and process resumes to generate semantic match records.
                </div>
              ) : (
                workspace.match_insights.map((match: any) => (
                  <div key={`${match.candidate_id}-${match.job_description_id}`} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-medium">{match.job_title}</div>
                        <div className="mt-1 text-sm text-foreground-muted">{match.candidate_name}</div>
                      </div>
                      <div className="text-lg font-semibold text-accent">{Math.round(match.overall_score)}</div>
                    </div>
                    <p className="mt-3 text-sm leading-6 text-foreground-muted">{match.explanation}</p>
                  </div>
                ))
              )}
            </div>
          </section>
          <form onSubmit={createJob} className="ops-panel rounded-xl p-5">
            <h2 className="text-base font-semibold">Create job</h2>
            <input
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              className="ops-input mt-4 w-full rounded-md px-3 py-3 text-sm"
              placeholder="Role title"
              required
            />
            <textarea
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              className="ops-input mt-3 min-h-48 w-full rounded-md px-3 py-3 text-sm"
              placeholder="Paste job description"
              required
            />
            <button disabled={saving} className="ops-button mt-4 inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60">
              {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
              Parse and index
            </button>
          </form>
        </div>
      </div>
    </AppShell>
  );
}
