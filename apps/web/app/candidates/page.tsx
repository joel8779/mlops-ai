"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/app-shell";
import { Bookmark, Loader2, MessageSquare, RefreshCcw, Star } from "lucide-react";
import { candidatesApi, feedbackApi } from "@/lib/api";

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [savingId, setSavingId] = useState<string | null>(null);

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
    loadCandidates();
  }, []);

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

  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">Candidates</h1>
            <p className="text-sm text-slate-600">Ranked profiles with workflow actions</p>
          </div>
          <button
            onClick={loadCandidates}
            className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            <RefreshCcw size={16} />
            Refresh
          </button>
        </div>
      </header>
      <section className="p-6">
        {error && (
          <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}
        <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
          {loading ? (
            <div className="flex items-center justify-center p-10 text-sm text-slate-600">
              <Loader2 className="mr-2 animate-spin" size={18} />
              Loading candidates
            </div>
          ) : candidates.length === 0 ? (
            <div className="p-10 text-center text-sm text-slate-600">
              No candidates yet. Upload resumes to start building the pipeline.
            </div>
          ) : (
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-100 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Candidate</th>
                <th className="px-4 py-3">Skills</th>
                <th className="px-4 py-3">Match</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {candidates.map((candidate) => (
                <tr key={candidate.id}>
                  <td className="px-4 py-3">
                    <Link href={`/candidates/${candidate.id}`} className="font-medium text-slate-900 hover:text-signal">
                      {candidate.full_name || "Unnamed candidate"}
                    </Link>
                    <div className="text-xs text-slate-500">{candidate.headline || candidate.email}</div>
                  </td>
                  <td className="px-4 py-3">{candidate.skills?.slice(0, 5).join(", ") || "Pending extraction"}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center gap-1 font-medium">
                      <Star size={15} />
                      {candidate.best_match_score ? Math.round(candidate.best_match_score) : "N/A"}
                    </span>
                  </td>
                  <td className="px-4 py-3">{candidate.current_stage || candidate.latest_resume_status || "New"}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button
                        onClick={() => recordFeedback(candidate.id, "shortlist")}
                        disabled={savingId === candidate.id}
                        className="rounded-md border border-slate-200 p-2 hover:border-signal"
                        aria-label="Shortlist candidate"
                      >
                        <Bookmark size={16} />
                      </button>
                      <button
                        onClick={() => recordFeedback(candidate.id, "interview")}
                        disabled={savingId === candidate.id}
                        className="rounded-md border border-slate-200 p-2 hover:border-signal"
                        aria-label="Mark for interview"
                      >
                        <MessageSquare size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          )}
        </div>
      </section>
    </AppShell>
  );
}
