"use client";

import { useEffect, useState } from "react";
import { Activity, BarChart3, BriefcaseBusiness, FileText, Loader2, Users } from "lucide-react";
import AppShell from "@/components/app-shell";
import { analyticsApi, workspaceApi } from "@/lib/api";

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<any>(null);
  const [workspace, setWorkspace] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const [analyticsData, workspaceData] = await Promise.all([analyticsApi.executive(), workspaceApi.activation()]);
        setAnalytics(analyticsData);
        setWorkspace(workspaceData);
      } catch (err: any) {
        setError(err.message || "Unable to load analytics");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const metrics = [
    { label: "Candidates", value: analytics?.total_candidates ?? 0, icon: Users },
    { label: "Jobs", value: analytics?.total_jobs ?? 0, icon: BriefcaseBusiness },
    { label: "Resumes", value: analytics?.total_resumes ?? 0, icon: FileText },
    { label: "Actions", value: analytics?.total_actions ?? 0, icon: Activity },
  ];
  const funnel = analytics?.hiring_funnel || {};
  const topSkills = analytics?.top_skills || [];
  const candidatesPerJob = analytics?.candidates_per_job || [];
  const atsDistribution = analytics?.ats_score_distribution || {};
  const semanticAverages = analytics?.semantic_match_averages || [];

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="ops-panel-strong rounded-xl p-5">
          <div className="text-xs uppercase tracking-[0.28em] text-accent">Operational telemetry</div>
          <h1 className="mt-2 text-xl font-semibold">Analytics</h1>
          <p className="text-sm text-foreground-muted">Backend analytics for recruiting operations.</p>
        </div>
        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}
        {loading ? (
          <div className="ops-panel flex min-h-[280px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="ops-panel rounded-xl p-5">
                    <div className="flex items-center justify-between text-sm text-foreground-muted">
                      {metric.label}
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="mt-3 text-2xl font-semibold">{metric.value}</div>
                  </div>
                );
              })}
            </div>
            <div className="grid gap-6 lg:grid-cols-2">
              <section className="ops-panel rounded-xl p-5">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-foreground-muted" />
                  <h2 className="text-base font-semibold">Hiring funnel</h2>
                </div>
                <div className="mt-4 space-y-3">
                  {Object.keys(funnel).length === 0 ? (
                    <p className="text-sm text-foreground-muted">No funnel data yet.</p>
                  ) : (
                    Object.entries(funnel).map(([stage, count]) => (
                      <div key={stage} className="flex items-center justify-between rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
                        <span className="capitalize">{stage.replace("_", " ")}</span>
                        <span>{String(count)}</span>
                      </div>
                    ))
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Top skills</h2>
                <div className="mt-4 space-y-3">
                  {topSkills.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No skills extracted yet.</p>
                  ) : (
                    topSkills.slice(0, 10).map((skill: any, index: number) => (
                      <div key={`${skill.skill || skill.name || index}`} className="flex items-center justify-between rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
                        <span>{skill.skill || skill.name || String(skill)}</span>
                        <span className="text-foreground-muted">{skill.count ?? ""}</span>
                      </div>
                    ))
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Processing metrics</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {Object.entries(workspace?.pipeline || {}).map(([status, count]) => (
                    <div key={status} className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-sm">
                      <div className="capitalize text-foreground-muted">{status}</div>
                      <div className="mt-1 text-xl font-semibold">{String(count)}</div>
                    </div>
                  ))}
                  {Object.keys(workspace?.pipeline || {}).length === 0 && (
                    <p className="text-sm text-foreground-muted">No processing state reported yet.</p>
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Activity sources</h2>
                <div className="mt-4 space-y-3">
                  {(workspace?.activity || []).slice(0, 6).map((event: any) => (
                    <div key={event.id} className="flex items-center justify-between rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
                      <span>{event.label}</span>
                      <span className="text-foreground-muted">{event.source}</span>
                    </div>
                  ))}
                  {(workspace?.activity || []).length === 0 && (
                    <p className="text-sm text-foreground-muted">No workflow or resume processing events yet.</p>
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Candidates per job</h2>
                <div className="mt-4 space-y-3">
                  {candidatesPerJob.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No job ranking data yet.</p>
                  ) : (
                    candidatesPerJob.slice(0, 8).map((item: any) => (
                      <div key={item.job_id} className="flex items-center justify-between rounded-md border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
                        <span>{item.job_title}</span>
                        <span className="text-foreground-muted">{item.candidate_count}</span>
                      </div>
                    ))
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">ATS distribution</h2>
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {Object.entries(atsDistribution).map(([bucket, count]) => (
                    <div key={bucket} className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-sm">
                      <div className="text-foreground-muted">{bucket.replace("_", "-")}</div>
                      <div className="mt-1 text-xl font-semibold">{String(count)}</div>
                    </div>
                  ))}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5 lg:col-span-2">
                <h2 className="text-base font-semibold">Semantic match averages</h2>
                <div className="mt-4 space-y-3">
                  {semanticAverages.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No semantic match averages yet.</p>
                  ) : (
                    semanticAverages.map((item: any) => (
                      <div key={item.job_id} className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-sm">
                        <div className="flex items-center justify-between">
                          <span>{item.job_title}</span>
                          <span className="text-accent">{Math.round(item.average_semantic_score)}</span>
                        </div>
                        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                          <div className="h-full bg-accent" style={{ width: `${Math.min(100, Math.max(4, item.average_semantic_score))}%` }} />
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
