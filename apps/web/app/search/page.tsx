"use client";

import { useState } from "react";
import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { SlidersHorizontal, Search, User, MapPin, Briefcase, Star, Loader2 } from "lucide-react";
import { searchApi } from "@/lib/api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [filters, setFilters] = useState({
    skills: "",
    location: "",
    limit: 10,
  });
  const [showFilters, setShowFilters] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchApi.candidates({
        query,
        skills: filters.skills ? filters.skills.split(",").map((s) => s.trim()) : undefined,
        location: filters.location || undefined,
        limit: filters.limit,
      });
      setResults(data as any[]);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Semantic Candidate Search</h1>
        <p className="text-sm text-slate-600">Hybrid vector, metadata, and reranking retrieval</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[320px_1fr]">
        <aside className="rounded-md border border-slate-200 bg-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <SlidersHorizontal size={18} />
              Filters
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="text-xs text-slate-600 hover:underline"
            >
              {showFilters ? "Hide" : "Show"}
            </button>
          </div>
          {showFilters && (
            <div className="mt-4 space-y-4">
              <label className="block text-sm">
                <span className="text-slate-600">Skills</span>
                <input
                  value={filters.skills}
                  onChange={(e) => setFilters({ ...filters, skills: e.target.value })}
                  placeholder="python, react, docker"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
                />
              </label>
              <label className="block text-sm">
                <span className="text-slate-600">Location</span>
                <input
                  value={filters.location}
                  onChange={(e) => setFilters({ ...filters, location: e.target.value })}
                  placeholder="San Francisco, CA"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
                />
              </label>
              <label className="block text-sm">
                <span className="text-slate-600">Results</span>
                <select
                  value={filters.limit}
                  onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) })}
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
                >
                  <option value={10}>10</option>
                  <option value={25}>25</option>
                  <option value={50}>50</option>
                </select>
              </label>
            </div>
          )}
        </aside>
        <div>
          <div className="flex gap-2">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Find Python backend engineers with Docker experience"
              className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none"
            />
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? <Loader2 className="animate-spin" size={18} /> : <Search size={18} />}
            </Button>
          </div>

          {loading && (
            <div className="mt-4 flex items-center justify-center rounded-md border border-slate-200 bg-white p-8">
              <Loader2 className="animate-spin text-signal" size={32} />
              <span className="ml-3 text-slate-600">Searching candidates...</span>
            </div>
          )}

          {!loading && results.length === 0 && query && (
            <div className="mt-4 rounded-md border border-slate-200 bg-white p-8 text-center text-slate-600">
              No candidates found. Try adjusting your search or filters.
            </div>
          )}

          {!loading && results.length > 0 && (
            <div className="mt-4 space-y-3">
              <div className="text-sm text-slate-600">{results.length} candidates found</div>
              {results.map((result) => (
                <div key={result.candidate_id} className="rounded-md border border-slate-200 bg-white p-4 hover:border-signal">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold">{result.payload?.full_name || "Unknown"}</h3>
                        <div className="flex items-center gap-1 rounded-full bg-signal/10 px-2 py-0.5 text-xs font-medium text-signal">
                          <Star size={12} />
                          {result.score}%
                        </div>
                      </div>
                      <div className="mt-2 flex items-center gap-4 text-sm text-slate-600">
                        {result.payload?.location && (
                          <div className="flex items-center gap-1">
                            <MapPin size={14} />
                            {result.payload.location}
                          </div>
                        )}
                        {result.payload?.headline && (
                          <div className="flex items-center gap-1">
                            <Briefcase size={14} />
                            {result.payload.headline}
                          </div>
                        )}
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {result.payload?.skills?.slice(0, 5).map((skill: string) => (
                          <span key={skill} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-700">
                            {skill}
                          </span>
                        ))}
                      </div>
                      <p className="mt-2 text-sm text-slate-600 line-clamp-2">{result.snippet}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && results.length === 0 && !query && (
            <div className="mt-4 rounded-md border border-slate-200 bg-white p-8 text-center">
              <User size={48} className="mx-auto text-slate-300" />
              <h3 className="mt-4 font-semibold text-slate-700">Start your search</h3>
              <p className="mt-2 text-sm text-slate-600">
                Enter a natural language query to find candidates using AI-powered semantic search.
              </p>
              <div className="mt-4 text-left text-sm text-slate-600">
                <p className="font-medium">Try:</p>
                <ul className="mt-2 space-y-1 list-disc pl-5">
                  <li>"Find senior Python developers with Docker experience"</li>
                  <li>"Machine learning engineers with NLP skills"</li>
                  <li>"Full stack developers in San Francisco"</li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </section>
    </AppShell>
  );
}
