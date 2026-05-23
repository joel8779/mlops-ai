"use client";

import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { useRecruiterStore } from "@/lib/store";
import { SlidersHorizontal } from "lucide-react";

export default function SearchPage() {
  const { query, setQuery } = useRecruiterStore();
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Semantic Candidate Search</h1>
        <p className="text-sm text-slate-600">Hybrid vector, metadata, and reranking retrieval</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[320px_1fr]">
        <aside className="rounded-md border border-slate-200 bg-white p-4">
          <div className="flex items-center gap-2 text-sm font-semibold"><SlidersHorizontal size={18} />Filters</div>
          {["Skills", "Location", "Education", "Experience"].map((filter) => (
            <label key={filter} className="mt-4 block text-sm">
              <span className="text-slate-600">{filter}</span>
              <input className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 outline-none" />
            </label>
          ))}
        </aside>
        <div>
          <div className="flex gap-2">
            <input value={query} onChange={(event) => setQuery(event.target.value)} className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none" />
            <Button>Search</Button>
          </div>
          <div className="mt-4 rounded-md border border-slate-200 bg-white p-4 text-sm text-slate-600">
            Search results will stream from `/api/v1/search/candidates`.
          </div>
        </div>
      </section>
    </AppShell>
  );
}
