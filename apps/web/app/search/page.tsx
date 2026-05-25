"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowUpRight, BrainCircuit, Database, Loader2, Radar, Search, SlidersHorizontal } from "lucide-react";
import AppShell from "@/components/app-shell";
import { searchApi } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [skills, setSkills] = useState("");
  const [location, setLocation] = useState("");
  const [results, setResults] = useState<any[]>([]);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    setSearched(true);
    try {
      setResults(
        (await searchApi.candidates({
          query,
          skills: skills ? skills.split(",").map((skill) => skill.trim()).filter(Boolean) : undefined,
          location: location || undefined,
          limit: 10,
        })) as any[]
      );
    } catch (err: any) {
      setError(err.message || "Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <div className="space-y-6">
        <section className="ops-panel-strong rounded-xl p-5 sm:p-6">
          <div className="flex items-center gap-2 text-xs uppercase tracking-[0.28em] text-accent">
            <Radar className="h-4 w-4" />
            Neural search terminal
          </div>
          <h1 className="mt-3 text-2xl font-semibold">Semantic Search</h1>
          <p className="mt-2 text-sm text-foreground-muted">Query candidate intelligence by meaning, role fit, skills, and operational context.</p>
        </section>

        {error && <div className="rounded-lg border border-error/30 bg-error/10 p-4 text-sm text-error">{error}</div>}

        <section className="ops-panel scanline rounded-xl p-5">
          <div className="grid gap-3 lg:grid-cols-[1fr_220px_220px_auto]">
            <div className="relative">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-accent" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={(event) => event.key === "Enter" && handleSearch()}
                className="ops-input w-full rounded-md py-3 pl-10 pr-3 font-mono text-sm"
                placeholder="find backend engineers with python, docker, distributed systems"
              />
            </div>
            <input value={skills} onChange={(event) => setSkills(event.target.value)} className="ops-input rounded-md px-3 py-3 text-sm" placeholder="Skills filter" />
            <input value={location} onChange={(event) => setLocation(event.target.value)} className="ops-input rounded-md px-3 py-3 text-sm" placeholder="Location" />
            <button onClick={handleSearch} disabled={loading || !query.trim()} className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60">
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <BrainCircuit className="h-4 w-4" />}
              Execute
            </button>
          </div>
        </section>

        {loading ? (
          <div className="ops-panel flex min-h-[260px] items-center justify-center rounded-xl">
            <Loader2 className="h-8 w-8 animate-spin text-accent" />
          </div>
        ) : !searched ? (
          <div className="ops-panel rounded-xl p-8 text-sm text-foreground-muted">
            <div className="flex items-center gap-2 font-medium text-foreground">
              <SlidersHorizontal className="h-4 w-4 text-accent" />
              Awaiting query vector
            </div>
            <p className="mt-2">Enter a natural language search to retrieve parsed and indexed candidates.</p>
          </div>
        ) : results.length === 0 ? (
          <div className="ops-panel rounded-xl p-8 text-sm text-foreground-muted">
            No candidates matched this query. Upload and process resumes, or adjust your filters.
          </div>
        ) : (
          <div className="grid gap-4">
            {results.map((result) => {
              const candidateId = result.candidate_id || result.payload?.candidate_id;
              const score = Number(result.score ?? 0);
              return (
                <div key={candidateId || result.id} className="ops-panel holo-border rounded-xl p-5">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 text-accent">
                          <BrainCircuit className="h-5 w-5" />
                        </div>
                        <div>
                          <h2 className="font-semibold">{result.payload?.full_name || result.full_name || "Candidate"}</h2>
                          <p className="text-xs uppercase tracking-[0.18em] text-foreground-subtle">semantic match</p>
                        </div>
                      </div>
                      <p className="mt-4 text-sm leading-6 text-foreground-muted">{result.snippet || result.payload?.headline || "No snippet returned"}</p>
                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                          <div className="flex items-center justify-between text-xs text-foreground-subtle">
                            Vector relevance
                            <span>{Math.round(score)}</span>
                          </div>
                          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                            <div className="h-full rounded-full bg-accent" style={{ width: `${Math.min(100, Math.max(8, score))}%` }} />
                          </div>
                        </div>
                        <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                          <div className="text-xs text-foreground-subtle">Semantic payload</div>
                          <div className="mt-2 truncate text-sm">{result.payload?.headline || result.payload?.location || "Indexed resume chunk"}</div>
                        </div>
                        <div className="rounded-lg border border-white/10 bg-white/[0.03] p-3">
                          <div className="text-xs text-foreground-subtle">Skills relationship</div>
                          <div className="mt-2 truncate text-sm">{(result.payload?.skills || []).slice(0, 3).join(", ") || "No skill metadata"}</div>
                        </div>
                      </div>
                      <div className="mt-4 rounded-lg border border-white/10 bg-white/[0.03] p-3 text-sm leading-6 text-foreground-muted">
                        <div className="mb-1 flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-accent">
                          <Database className="h-3.5 w-3.5" />
                          Ranking explanation
                        </div>
                        Neural Ops embedded the query, filtered the Qdrant candidate index by organization and optional facets, then reranked matches with lexical overlap from the returned resume chunk.
                      </div>
                    </div>
                    {candidateId && (
                      <Link href={`/candidates/${candidateId}`} className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold">
                        Open
                        <ArrowUpRight className="h-4 w-4" />
                      </Link>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </AppShell>
  );
}
