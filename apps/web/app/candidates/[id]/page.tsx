"use client";

import { use, useEffect, useState } from "react";
import { Bot, Loader2 } from "lucide-react";
import AppShell from "@/components/app-shell";
import { aiApi, candidatesApi } from "@/lib/api";

export default function CandidateProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [candidate, setCandidate] = useState<any>(null);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const candidateData = await candidatesApi.get(id) as any;
        setCandidate(candidateData);
        setSummary(candidateData.summary || "");
      } catch (err: any) {
        setError(err.message || "Unable to load candidate");
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
      const answerText = String(response.answer ?? "").trim();
      const summaryText = String(response.summary ?? "").trim();
      const nextSummary = answerText || summaryText || candidate?.summary || "";
      setSummary(nextSummary);
      if (answerText || summaryText) {
        const newSummary = answerText || summaryText;
        setCandidate((prev) => (prev ? { ...prev, summary: newSummary } : prev));
      }
    } catch (err: any) {
      setError(err.message || "Unable to generate summary");
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {loading ? (
          <div className="ops-panel flex min-h-[280px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : error && !candidate ? (
          <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>
        ) : (
          <>
            <div className="ops-panel-strong rounded-xl p-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-xs uppercase tracking-[0.28em] text-accent">Candidate dossier</div>
                <h1 className="mt-2 text-xl font-semibold">{candidate?.full_name || candidate?.email || "Candidate"}</h1>
                <p className="text-sm text-foreground-muted">{candidate?.headline || candidate?.location || "Profile details from parsed resume data."}</p>
              </div>
              <div className="flex flex-wrap gap-2">
                <button onClick={generateSummary} disabled={aiLoading} className="ops-button inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60">
                  {aiLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
                  AI summary
                </button>
              </div>
            </div>
            {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}
            <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
              <section className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Candidate profile</h2>
                <p className="mt-3 text-sm leading-6 text-foreground-muted">
                  {summary || candidate?.summary || "No AI summary or extracted profile summary is available yet."}
                </p>
                <div className="mt-5 flex flex-wrap gap-2">
                  {(candidate?.skills || []).map((skill: string) => (
                    <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">
                      {skill}
                    </span>
                  ))}
                  {(!candidate?.skills || candidate.skills.length === 0) && <span className="text-sm text-foreground-muted">No skills extracted.</span>}
                </div>
                {candidate?.resume_text_preview && (
                  <div className="mt-5 rounded-lg border border-white/10 bg-white/[0.03] p-4">
                    <h3 className="text-sm font-semibold">Resume preview</h3>
                    <p className="mt-2 max-h-96 overflow-auto whitespace-pre-wrap text-sm leading-6 text-foreground-muted">{candidate.resume_text_preview}</p>
                  </div>
                )}
              </section>
              <aside className="ops-panel rounded-xl p-5">
                <h2 className="text-base font-semibold">Backend signals</h2>
                <div className="mt-4 space-y-3 text-sm">
                  <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
                    <div className="text-foreground-muted">Resume status</div>
                    <div className="mt-1">{candidate?.latest_resume_status || "No resume linked"}</div>
                  </div>
                  <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
                    <div className="text-foreground-muted">Pipeline stage</div>
                    <div className="mt-1">{candidate?.current_stage || "No stage recorded"}</div>
                  </div>
                  <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
                    <div className="text-foreground-muted">Best match score</div>
                    <div className="mt-1">{candidate?.best_match_score ?? "No match generated"}</div>
                  </div>
                  <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
                    <div className="text-foreground-muted">ATS scoring</div>
                    <div className="mt-1">Open a job to score this candidate against that JD.</div>
                  </div>
                </div>
              </aside>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
