"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowUpRight, Bookmark, Loader2, RefreshCcw, UploadCloud, User } from "lucide-react";
import AppShell from "@/components/app-shell";
import { candidatesApi, feedbackApi } from "@/lib/api";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState<string | null>(null);
  const [error, setError] = useState("");

  const loadCandidates = async () => {
    setLoading(true);
    setError("");
    try {
      setCandidates((await candidatesApi.list()) as any[]);
    } catch (err: any) {
      setError(err.message || "Unable to load candidates");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const saveFeedback = async (candidateId: string, action: string) => {
    setSavingId(candidateId);
    try {
      await feedbackApi.ranking({ candidate_id: candidateId, action });
    } catch (err: any) {
      setError(err.message || "Unable to save feedback");
    } finally {
      setSavingId(null);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="ops-panel-strong rounded-xl p-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.28em] text-accent">Candidate intelligence</div>
            <h1 className="mt-2 text-xl font-semibold">Candidates</h1>
            <p className="text-sm text-foreground-muted">Parsed candidates from uploaded documents.</p>
          </div>
          <button onClick={loadCandidates} className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm">
            <RefreshCcw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}

        {loading ? (
          <div className="ops-panel flex min-h-[280px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : candidates.length === 0 ? (
          <div className="ops-panel rounded-xl p-10 text-center">
            <User className="mx-auto h-10 w-10 text-accent" />
            <h2 className="mt-4 text-lg font-semibold">No candidates yet</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-foreground-muted">
              Upload resumes on the Documents page. Parsed candidates will appear here when backend processing completes.
            </p>
            <Link href="/documents" className="ops-button mt-6 inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold">
              <UploadCloud className="h-4 w-4" />
              Upload resumes
            </Link>
          </div>
        ) : (
          <div className="ops-panel overflow-hidden rounded-xl">
            <div className="hidden grid-cols-[minmax(180px,1.4fr)_minmax(120px,1fr)_120px_120px] gap-4 border-b border-white/10 px-5 py-3 text-xs uppercase tracking-[0.18em] text-foreground-subtle lg:grid">
              <div>Candidate</div>
              <div>Profile signals</div>
              <div>Resume state</div>
              <div>ATS / match</div>
            </div>
            {candidates.map((candidate) => (
              <div key={candidate.id} className="grid gap-4 border-b border-white/10 px-5 py-4 last:border-b-0 lg:grid-cols-[minmax(180px,1.4fr)_minmax(120px,1fr)_120px_120px] lg:items-start">
                <div className="min-w-0">
                    <Link href={`/candidates/${candidate.id}`} className="text-lg font-semibold hover:text-accent">
                      {candidate.full_name || candidate.email || "Unnamed candidate"}
                    </Link>
                    <p className="mt-1 text-sm text-foreground-muted">{candidate.headline || candidate.location || "Profile details pending extraction"}</p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {(candidate.skills || []).slice(0, 6).map((skill: string) => (
                      <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">
                        {skill}
                      </span>
                    ))}
                    {(!candidate.skills || candidate.skills.length === 0) && <span className="text-sm text-foreground-muted">No skills extracted yet</span>}
                  </div>
                  <div className="text-sm text-foreground-muted">{candidate.latest_resume_status || "No resume"}</div>
                  <div className="flex flex-col gap-2">
                    <div className="text-sm text-foreground-muted">
                      {candidate.best_match_score ? `${Math.round(candidate.best_match_score)} match` : "No match"}
                    </div>
                    <button
                      onClick={() => saveFeedback(candidate.id, "shortlist")}
                      disabled={savingId === candidate.id}
                      className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                    >
                      {savingId === candidate.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bookmark className="h-4 w-4" />}
                      Shortlist
                    </button>
                    <Link href={`/candidates/${candidate.id}`} className="ops-button inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold">
                      Open
                      <ArrowUpRight className="h-4 w-4" />
                    </Link>
                  </div>
                </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  );
}
