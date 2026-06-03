"use client";

import { use, useEffect, useState } from "react";
import { Bot, Loader2 } from "lucide-react";
import AppShell from "@/components/app-shell";
import { aiApi, candidatesApi } from "@/lib/api";

const SUMMARY_SECTIONS = [
  "Candidate Overview",
  "Technical Strengths",
  "Relevant Experience",
  "Hiring Concerns",
  "Recommended Fit",
  "Interview Focus Areas",
];

function parseBriefing(value: string) {
  const clean = value.replace(/\*\*/g, "").trim();
  if (!clean) return [];
  const sectionPattern = new RegExp(`^(${SUMMARY_SECTIONS.join("|")})\\s*$`, "gim");
  const matches = [...clean.matchAll(sectionPattern)];
  if (!matches.length) return [{ title: "Candidate Overview", body: clean, bullets: [] }];
  return matches.map((match, index) => {
    const title = match[1];
    const start = (match.index ?? 0) + match[0].length;
    const end = index + 1 < matches.length ? matches[index + 1].index ?? clean.length : clean.length;
    const body = clean.slice(start, end).trim();
    const lines = body.split(/\n+/).map((line) => line.replace(/^[-•]\s*/, "").trim()).filter(Boolean);
    return {
      title,
      body: title === "Candidate Overview" ? lines.join(" ") : "",
      bullets: title === "Candidate Overview" ? [] : lines,
    };
  });
}

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
        setCandidate((prev: any) => (prev ? { ...prev, summary: newSummary } : prev));
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
                <h1 className="mt-2 text-xl font-semibold">{candidate?.full_name || candidate?.email || "Unnamed candidate"}</h1>
                {(candidate?.headline || candidate?.location) && (
                  <p className="text-sm text-foreground-muted">{candidate?.headline || candidate?.location}</p>
                )}
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
                <h2 className="text-base font-semibold">Recruiter briefing</h2>
                <div className="mt-4 grid gap-3">
                  {parseBriefing(summary || candidate?.summary || "").map((section) => (
                    <div key={section.title} className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
                      <h3 className="text-sm font-semibold text-foreground">{section.title}</h3>
                      {section.body && <p className="mt-2 text-sm leading-6 text-foreground-muted">{section.body}</p>}
                      {section.bullets.length > 0 && (
                        <ul className="mt-2 space-y-1.5 text-sm leading-6 text-foreground-muted">
                          {section.bullets.slice(0, 6).map((item) => (
                            <li key={item} className="flex gap-2">
                              <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                              <span>{item}</span>
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ))}
                  {!summary && !candidate?.summary && <p className="text-sm text-foreground-muted">Generate a recruiter briefing for this candidate.</p>}
                </div>
                <div className="mt-5 flex flex-wrap gap-2">
                  {(candidate?.skills || []).map((skill: string) => (
                    <span key={skill} className="ops-chip rounded-md px-2 py-1 text-xs">
                      {skill}
                    </span>
                  ))}
                  {(!candidate?.skills || candidate.skills.length === 0) && <span className="text-sm text-foreground-muted">Skills unavailable.</span>}
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
