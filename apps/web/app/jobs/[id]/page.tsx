"use client";

import Link from "next/link";
import { use, useEffect, useState } from "react";
import { AlertTriangle, Bot, BrainCircuit, CheckCircle, Loader2, RefreshCcw, Star, XCircle } from "lucide-react";
import AppShell from "@/components/app-shell";
import { atsApi, jobsApi, feedbackApi } from "@/lib/api";

export default function JobIntelligencePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      setData(await jobsApi.intelligence(id));
    } catch (err: any) {
      setError(err.message || "Unable to load job intelligence");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [id]);

  const scoreCandidate = async (candidateId: string) => {
    setSavingId(candidateId);
    setError("");
    try {
      await atsApi.scoreCandidateForJob(id, candidateId);
      await load();
    } catch (err: any) {
      setError(err.message || "Unable to score candidate for this job");
    } finally {
      setSavingId(null);
    }
  };

  const feedback = async (candidateId: string, action: string) => {
    setSavingId(candidateId);
    setError("");
    try {
      await feedbackApi.ranking({ candidate_id: candidateId, job_description_id: id, action });
      await load();
    } catch (err: any) {
      setError(err.message || "Unable to save recruiter action");
    } finally {
      setSavingId(null);
    }
  };

  const job = data?.job;
  const ranked = data?.ranked_candidates || [];
  const insights = data?.semantic_insights || {};
  const semanticRequirements = job?.metadata_json?.intelligence?.semantic_requirements || [];

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Top Section: Job title, experience, primary skills, ATS stats */}
        <section className="ops-panel-strong rounded-xl p-5 sm:p-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-accent">
                <BrainCircuit className="h-4 w-4" />
                Job intelligence
              </div>
              <h1 className="mt-3 text-2xl font-semibold">{job?.title || "Job"}</h1>
              <div className="mt-3 flex flex-wrap items-center gap-4 text-sm">
                <span className="text-foreground-muted">Experience required: <span className="text-foreground font-medium">{job?.years_experience_min ?? "Any"} years</span></span>
                <span className="text-foreground-muted">Status: <span className="text-foreground font-medium">{job?.status || "active"}</span></span>
              </div>
              <div className="mt-4 flex flex-wrap gap-2">
                {(job?.required_skills || []).slice(0, 8).map((skill: string) => (
                  <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">{skill}</span>
                ))}
                {(job?.required_skills || []).length === 0 && <span className="text-sm text-foreground-muted">No required skills extracted.</span>}
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 lg:min-w-[280px]">
              <div className="ops-panel rounded-lg p-3 text-center">
                <div className="text-xs text-foreground-subtle">Candidates</div>
                <div className="mt-1 text-xl font-semibold text-accent">{insights.candidate_count || 0}</div>
              </div>
              <div className="ops-panel rounded-lg p-3 text-center">
                <div className="text-xs text-foreground-subtle">Semantic</div>
                <div className="mt-1 text-xl font-semibold text-accent">{Math.round(insights.average_semantic_alignment || 0)}</div>
              </div>
              <div className="ops-panel rounded-lg p-3 text-center">
                <div className="text-xs text-foreground-subtle">ATS Avg</div>
                <div className="mt-1 text-xl font-semibold text-accent">{Math.round(insights.average_ats_score || 0)}</div>
              </div>
            </div>
          </div>
          <button onClick={load} className="ops-button-secondary mt-4 inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm">
            <RefreshCcw className="h-4 w-4" />
            Refresh
          </button>
        </section>

        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}

        {loading ? (
          <div className="ops-panel flex min-h-[320px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : (
          <>
            {/* Middle Section: Cleaned JD summary, responsibilities, requirements */}
            <div className="grid gap-6 lg:grid-cols-2">
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Job description summary</h2>
                <div className="mt-4 text-sm leading-6 text-foreground-muted max-h-[200px] overflow-y-auto">
                  {job?.description ? (
                    <p>{job.description.slice(0, 800)}{job.description.length > 800 ? "..." : ""}</p>
                  ) : (
                    <p>Loading job description...</p>
                  )}
                </div>
              </section>
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Semantic requirements</h2>
                <div className="mt-4 space-y-3 max-h-[200px] overflow-y-auto">
                  {semanticRequirements.length === 0 ? (
                    <p className="text-sm text-foreground-muted">No semantic requirements extracted yet.</p>
                  ) : (
                    semanticRequirements.slice(0, 6).map((item: string) => (
                      <div key={item} className="rounded-md border border-white/10 bg-white/[0.03] p-3 text-sm leading-6 text-foreground-muted">
                        {item}
                      </div>
                    ))
                  )}
                </div>
              </section>
            </div>

            {/* Bottom Section: Ranked candidates, semantic insights, ATS explanation */}
            <div className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)]">
              <aside className="space-y-6">
                <section className="ops-panel rounded-xl p-5">
                  <h2 className="text-base font-semibold">Semantic insights</h2>
                  <div className="mt-4 space-y-3 text-sm">
                    <div>
                      <div className="mb-2 text-xs uppercase tracking-[0.16em] text-foreground-subtle">Most matched skills</div>
                      {(insights.most_matched_skills || []).slice(0, 6).map((item: any) => (
                        <div key={item.name} className="flex items-center justify-between rounded-md border border-white/10 bg-white/[0.03] px-3 py-2">
                          <span>{item.name}</span>
                          <span className="text-foreground-muted">{item.count}</span>
                        </div>
                      ))}
                    </div>
                    <div>
                      <div className="mb-2 text-xs uppercase tracking-[0.16em] text-warning">Missing skill clusters</div>
                      {(insights.missing_skill_clusters || []).slice(0, 4).map((item: any) => (
                        <div key={item.name} className="flex items-center gap-2 rounded-md border border-warning/20 bg-warning/10 px-3 py-2 text-warning">
                          <AlertTriangle className="h-4 w-4" />
                          {item.name}
                        </div>
                      ))}
                    </div>
                  </div>
                </section>
              </aside>

              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">ATS-ranked candidates</h2>
                <div className="mt-4 space-y-4">
                  {ranked.length === 0 ? (
                    <div className="rounded-lg border border-white/10 bg-white/[0.03] p-6 text-sm text-foreground-muted">
                      No candidates are ready for this job yet. Upload resumes and refresh when embeddings are complete.
                    </div>
                  ) : (
                    ranked.map((candidate: any, index: number) => (
                      <div key={candidate.candidate_id} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                          <div className="min-w-0">
                            <div className="flex items-center gap-2">
                              <span className="text-xs text-foreground-subtle">#{index + 1}</span>
                              <Link href={`/candidates/${candidate.candidate_id}`} className="font-semibold hover:text-accent">
                                {candidate.full_name || candidate.email || "Unnamed candidate"}
                              </Link>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-foreground-muted">{candidate.explanation}</p>
                          </div>
                          <div className="grid min-w-[220px] grid-cols-2 gap-2 text-sm">
                            <Score label="ATS" value={candidate.ats_score ?? candidate.overall_score} />
                            <Score label="Semantic" value={candidate.semantic_score} />
                            <Score label="Experience" value={candidate.experience_match} />
                            <Score label="Keywords" value={candidate.keyword_score} />
                          </div>
                        </div>
                        <div className="mt-4 grid gap-3 md:grid-cols-2">
                          <div>
                            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-success">
                              <CheckCircle className="h-3.5 w-3.5" />
                              Matched
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {(candidate.matched_skills || []).map((skill: string) => <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">{skill}</span>)}
                            </div>
                          </div>
                          <div>
                            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.16em] text-warning">
                              <XCircle className="h-3.5 w-3.5" />
                              Gaps
                            </div>
                            <div className="flex flex-wrap gap-2">
                              {(candidate.missing_skills || []).map((skill: string) => <span key={skill} className="rounded-md border border-warning/20 px-2 py-1 text-xs text-warning">{skill}</span>)}
                              {(candidate.missing_skills || []).length === 0 && <span className="text-sm text-foreground-muted">No critical gaps.</span>}
                            </div>
                          </div>
                        </div>
                        <div className="mt-4 flex flex-wrap gap-2">
                          <button onClick={() => scoreCandidate(candidate.candidate_id)} disabled={savingId === candidate.candidate_id} className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm disabled:opacity-60">
                            {savingId === candidate.candidate_id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
                            Generate ATS
                          </button>
                          <button onClick={() => feedback(candidate.candidate_id, "shortlist")} disabled={savingId === candidate.candidate_id} className="ops-button inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold disabled:opacity-60">
                            <Star className="h-4 w-4" />
                            Shortlist
                          </button>
                          <button onClick={() => feedback(candidate.candidate_id, "reject")} disabled={savingId === candidate.candidate_id} className="rounded-lg border border-error/30 px-3 py-2 text-sm text-error hover:bg-error/10 disabled:opacity-60">
                            Reject
                          </button>
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

function Score({ label, value }: { label: string; value: number }) {
  const score = Math.round(Number(value || 0));
  return (
    <div className="rounded-md border border-white/10 bg-background/40 p-3">
      <div className="text-xs text-foreground-subtle">{label}</div>
      <div className="mt-1 text-lg font-semibold text-accent">{score}</div>
    </div>
  );
}
