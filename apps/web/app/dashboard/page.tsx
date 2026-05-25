"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Bot,
  BriefcaseBusiness,
  CheckCircle,
  Cpu,
  Database,
  FileText,
  Loader2,
  Radar,
  Search,
  UploadCloud,
  Users,
  Zap,
} from "lucide-react";
import AppShell from "@/components/app-shell";
import { analyticsApi, candidatesApi, resumesApi, workspaceApi } from "@/lib/api";

const pipelineLabels: Record<string, string> = {
  uploaded: "Uploaded",
  queued: "Queued",
  parsing: "OCR / parse",
  parsed: "Parsed",
  embedded: "Embedded",
  failed: "Failed",
};

export default function DashboardPage() {
  const [activation, setActivation] = useState<any>(null);
  const [analytics, setAnalytics] = useState<any>(null);
  const [candidates, setCandidates] = useState<any[]>([]);
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [demoLoading, setDemoLoading] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const activationData = await workspaceApi.activation();
      setActivation(activationData);
      if ((activationData as any).activated) {
        const [analyticsData, candidateData, documentData] = await Promise.all([
          analyticsApi.executive(),
          candidatesApi.list(),
          resumesApi.list(),
        ]);
        setAnalytics(analyticsData);
        setCandidates(candidateData as any[]);
        setDocuments(documentData as any[]);
      } else {
        setAnalytics(null);
        setCandidates([]);
        setDocuments([]);
      }
    } catch (err: any) {
      setError(err.message || "Unable to load workspace state");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const loadDemo = async () => {
    setDemoLoading(true);
    setError("");
    try {
      const response = (await workspaceApi.loadDemo()) as any;
      setActivation(response.activation);
      await load();
    } catch (err: any) {
      setError(err.message || "Unable to load demo workspace");
    } finally {
      setDemoLoading(false);
    }
  };

  const counts = activation?.counts || {};
  const pipeline = activation?.pipeline || {};
  const activity = activation?.activity || [];
  const insights = activation?.match_insights || [];
  const metrics = [
    { label: "Candidates", value: counts.candidates ?? analytics?.total_candidates ?? 0, icon: Users, tone: "text-accent" },
    { label: "Active jobs", value: counts.jobs ?? analytics?.total_jobs ?? 0, icon: BriefcaseBusiness, tone: "text-violet" },
    { label: "Embedded resumes", value: counts.embedded_resumes ?? 0, icon: Database, tone: "text-success" },
    { label: "Semantic matches", value: counts.semantic_matches ?? 0, icon: Bot, tone: "text-warning" },
  ];

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="ops-panel-strong holo-border rounded-xl p-5 sm:p-6">
          <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-accent">
                <Radar className="h-4 w-4" />
                Recruiting mission control
              </div>
              <h1 className="mt-3 text-3xl font-semibold tracking-tight">Neural Ops Command Center</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-foreground-muted">
                Backend-visible recruiting intelligence: ingestion, OCR, embeddings, semantic matching, ATS scoring, and workflow activity.
              </p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link href="/documents" className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm font-semibold">
                <UploadCloud className="h-4 w-4" />
                Upload resumes
              </Link>
              <button onClick={loadDemo} disabled={demoLoading} className="ops-button-secondary inline-flex items-center justify-center gap-2 rounded-lg px-4 py-3 text-sm disabled:opacity-60">
                {demoLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
                Load demo workspace
              </button>
            </div>
          </div>
        </section>

        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}

        {loading ? (
          <div className="ops-panel flex min-h-[360px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : !activation?.activated ? (
          <section className="ops-panel-strong scanline rounded-xl p-8 sm:p-10">
            <div className="mx-auto max-w-3xl text-center">
              <Zap className="mx-auto h-11 w-11 text-accent" />
              <h2 className="mt-4 text-2xl font-semibold">Welcome to Neural Ops.</h2>
              <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-foreground-muted">
                Import candidate intelligence to activate your workspace. Neural Ops comes alive after resumes, jobs, embeddings, matches, and workflow events exist in the backend.
              </p>
              <div className="mt-7 flex flex-col justify-center gap-3 sm:flex-row">
                <Link href="/documents" className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-5 py-3 text-sm font-semibold">
                  <UploadCloud className="h-4 w-4" />
                  Upload resumes
                </Link>
                <button onClick={loadDemo} disabled={demoLoading} className="ops-button-secondary inline-flex items-center justify-center gap-2 rounded-lg px-5 py-3 text-sm disabled:opacity-60">
                  {demoLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Database className="h-4 w-4" />}
                  Load demo workspace
                </button>
              </div>
            </div>
          </section>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="ops-panel rounded-xl p-5">
                    <div className="flex items-center justify-between text-sm text-foreground-muted">
                      {metric.label}
                      <Icon className={`h-5 w-5 ${metric.tone}`} />
                    </div>
                    <div className="mt-4 text-3xl font-semibold">{metric.value}</div>
                    <div className="mt-3 text-xs uppercase tracking-[0.18em] text-foreground-subtle">backend state</div>
                  </div>
                );
              })}
            </div>

            <div className="grid gap-6 xl:grid-cols-3">
              <section className="ops-panel rounded-xl p-5 xl:col-span-2">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold">AI ingestion pipeline</h2>
                  <Activity className="h-4 w-4 text-accent" />
                </div>
                <div className="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  {Object.keys(pipelineLabels).map((key) => (
                    <div key={key} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                      <div className="flex items-center justify-between">
                        <div className="text-xs text-foreground-subtle">{pipelineLabels[key]}</div>
                        {Number(pipeline[key] || 0) > 0 ? <CheckCircle className="h-4 w-4 text-success" /> : <Cpu className="h-4 w-4 text-foreground-subtle" />}
                      </div>
                      <div className="mt-3 text-2xl font-semibold">{pipeline[key] || 0}</div>
                    </div>
                  ))}
                </div>
              </section>

              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Next best actions</h2>
                <div className="mt-4 space-y-3">
                  {(activation.recommendations || []).map((item: string) => (
                    <div key={item} className="rounded-lg border border-white/10 bg-white/[0.03] p-3 text-sm leading-6 text-foreground-muted">
                      {item}
                    </div>
                  ))}
                </div>
                <div className="mt-4 grid gap-3">
                  <Link href="/search" className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-3 py-3 text-sm">
                    <Search className="h-4 w-4" />
                    Run semantic search
                  </Link>
                  <Link href="/analytics" className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-3 py-3 text-sm">
                    <Bot className="h-4 w-4" />
                    Review intelligence
                  </Link>
                </div>
              </section>

              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Operational activity</h2>
                <div className="mt-4 space-y-3">
                  {activity.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No activity emitted yet.</p>
                  ) : (
                    activity.slice(0, 8).map((event: any) => (
                      <div key={event.id} className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                        <div className="flex items-center justify-between gap-3">
                          <div className="text-sm font-medium">{event.label}</div>
                          <span className="rounded-full border border-accent/20 px-2 py-0.5 text-[11px] uppercase tracking-[0.14em] text-accent">{event.source}</span>
                        </div>
                        <div className="mt-1 text-xs text-foreground-subtle">{new Date(event.created_at).toLocaleString()}</div>
                      </div>
                    ))
                  )}
                </div>
              </section>

              <section className="ops-panel rounded-xl p-5 xl:col-span-2">
                <div className="flex items-center justify-between">
                  <h2 className="text-base font-semibold">Semantic match intelligence</h2>
                  <BarChart3 className="h-4 w-4 text-accent" />
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {insights.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No match insights yet. Create jobs and run ranking to populate this panel.</p>
                  ) : (
                    insights.map((insight: any) => (
                      <div key={`${insight.candidate_id}-${insight.job_description_id}`} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <div className="font-medium">{insight.candidate_name || "Candidate"}</div>
                            <div className="mt-1 text-xs text-foreground-subtle">{insight.job_title}</div>
                          </div>
                          <div className="text-lg font-semibold text-accent">{Math.round(insight.overall_score)}</div>
                        </div>
                        <p className="mt-3 text-sm leading-6 text-foreground-muted">{insight.explanation}</p>
                        <div className="mt-3 flex flex-wrap gap-2">
                          {(insight.matched_skills || []).slice(0, 5).map((skill: string) => (
                            <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">{skill}</span>
                          ))}
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>

              <section className="ops-panel rounded-xl p-5 xl:col-span-3">
                <h2 className="text-base font-semibold">Recent backend objects</h2>
                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <div className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                    <div className="mb-3 flex items-center gap-2 text-sm font-medium"><FileText className="h-4 w-4 text-accent" />Documents</div>
                    <div className="space-y-2 text-sm text-foreground-muted">
                      {documents.slice(0, 4).map((document) => <div key={document.id}>{document.original_filename} - {document.status}</div>)}
                      {documents.length === 0 && <div>No uploaded resumes.</div>}
                    </div>
                  </div>
                  <div className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                    <div className="mb-3 flex items-center gap-2 text-sm font-medium"><Users className="h-4 w-4 text-accent" />Candidates</div>
                    <div className="space-y-2 text-sm text-foreground-muted">
                      {candidates.slice(0, 4).map((candidate) => <div key={candidate.id}>{candidate.full_name || candidate.email || "Unnamed"} - {candidate.latest_resume_status || "profile"}</div>)}
                      {candidates.length === 0 && <div>No parsed candidates.</div>}
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
