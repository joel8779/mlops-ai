"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Loader2, Plus, RefreshCcw } from "lucide-react";
import { jobsApi } from "@/lib/api";

export default function JobsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

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
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Job Descriptions</h1>
        <p className="text-sm text-slate-600">Create, parse, index, and match roles</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[1fr_380px]">
        <div className="rounded-md border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold">Active roles</h2>
            <button onClick={loadJobs} className="rounded-md border border-slate-200 p-2" aria-label="Refresh jobs">
              <RefreshCcw size={16} />
            </button>
          </div>
          {error && <div className="mt-3 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</div>}
          <div className="mt-3 divide-y divide-slate-200 text-sm">
            {loading ? (
              <div className="flex items-center py-6 text-slate-600">
                <Loader2 className="mr-2 animate-spin" size={16} />
                Loading roles
              </div>
            ) : jobs.length === 0 ? (
              <div className="py-6 text-slate-600">No roles yet. Create one to rank candidates.</div>
            ) : (
              jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between gap-3 py-3">
                  <div>
                    <div className="font-medium">{job.title}</div>
                    <div className="text-xs text-slate-500">
                      {(job.required_skills || []).slice(0, 4).join(", ") || "Parsing pending"}
                    </div>
                  </div>
                  <span className="rounded-md bg-slate-100 px-2 py-1 text-xs">{job.status}</span>
                </div>
              ))
            )}
          </div>
        </div>
        <form onSubmit={createJob} className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Create job</h2>
          <input
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
            placeholder="Title"
            required
          />
          <textarea
            value={description}
            onChange={(event) => setDescription(event.target.value)}
            className="mt-3 min-h-48 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
            placeholder="Paste job description"
            required
          />
          <button
            disabled={saving}
            className="mt-3 inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          >
            {saving ? <Loader2 className="animate-spin" size={16} /> : <Plus size={16} />}
            Parse and index
          </button>
        </form>
      </section>
    </AppShell>
  );
}
