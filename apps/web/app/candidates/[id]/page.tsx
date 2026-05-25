"use client";

import { use, useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { RankingVisualization } from "@/components/ranking-visualization";
import { aiApi, atsApi, candidatesApi } from "@/lib/api";
import { Bot, FileText, Loader2, Sparkles } from "lucide-react";

export default function CandidateProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [candidate, setCandidate] = useState<any>(null);
  const [summary, setSummary] = useState("");
  const [atsScore, setAtsScore] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [aiLoading, setAiLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError("");
      try {
        const data = (await candidatesApi.get(id)) as any;
        setCandidate(data);
      } catch (err: any) {
        setError(err.message || "Failed to load candidate");
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
      setSummary(response.answer);
    } catch (err: any) {
      setError(err.message || "Failed to generate summary");
    } finally {
      setAiLoading(false);
    }
  };

  const scoreResume = async () => {
    if (!candidate?.latest_resume_id) return;
    setAiLoading(true);
    setError("");
    try {
      setAtsScore(await atsApi.scoreResume(candidate.latest_resume_id));
    } catch (err: any) {
      setError(err.message || "Failed to score resume");
    } finally {
      setAiLoading(false);
    }
  };

  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">{candidate?.full_name || "Candidate Profile"}</h1>
        <p className="text-sm text-slate-600">{candidate?.headline || `Profile ID: ${id}`}</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[1fr_360px]">
        {loading ? (
          <div className="rounded-md border border-slate-200 bg-white p-8 text-sm text-slate-600">
            <Loader2 className="mr-2 inline animate-spin" size={16} />
            Loading candidate
          </div>
        ) : error ? (
          <div className="rounded-md border border-red-200 bg-red-50 p-5 text-sm text-red-700">{error}</div>
        ) : (
        <article className="rounded-md border border-slate-200 bg-white p-5">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-lg font-semibold">Candidate intelligence</h2>
            <div className="flex gap-2">
              <button
                onClick={generateSummary}
                disabled={aiLoading}
                className="inline-flex items-center gap-2 rounded-md bg-signal px-3 py-2 text-sm font-medium text-white disabled:opacity-60"
              >
                {aiLoading ? <Loader2 className="animate-spin" size={16} /> : <Bot size={16} />}
                Summarize
              </button>
              <button
                onClick={scoreResume}
                disabled={aiLoading || !candidate?.latest_resume_id}
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 px-3 py-2 text-sm disabled:opacity-60"
              >
                <FileText size={16} />
                ATS
              </button>
            </div>
          </div>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            {summary || candidate?.summary || "Generate an AI summary to review this candidate."}
          </p>
          {atsScore && (
            <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
              <div className="flex items-center gap-2 font-medium">
                <Sparkles size={16} className="text-signal" />
                ATS score: {Math.round(atsScore.ats_score)}
              </div>
            </div>
          )}
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {(candidate?.skills || []).slice(0, 9).map((skill: string) => (
              <span key={skill} className="rounded-md bg-slate-100 px-3 py-2 text-sm">{skill}</span>
            ))}
          </div>
          {candidate?.resume_text_preview && (
            <div className="mt-5 rounded-md border border-slate-200 bg-slate-50 p-4">
              <h3 className="text-sm font-semibold">Resume preview</h3>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-600">
                {candidate.resume_text_preview}
              </p>
            </div>
          )}
        </article>
        )}
        <RankingVisualization />
      </section>
    </AppShell>
  );
}
