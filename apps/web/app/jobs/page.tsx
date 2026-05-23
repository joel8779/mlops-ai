import { AppShell } from "@/components/app-shell";

export default function JobsPage() {
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Job Descriptions</h1>
        <p className="text-sm text-slate-600">Create, parse, index, and match roles</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[1fr_380px]">
        <div className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Active roles</h2>
          <div className="mt-3 divide-y divide-slate-200 text-sm">
            {["Senior Backend Engineer", "ML Engineer NLP", "Frontend Platform Engineer"].map((job) => (
              <div key={job} className="flex items-center justify-between py-3">
                <span>{job}</span>
                <span className="rounded-md bg-slate-100 px-2 py-1 text-xs">Indexed</span>
              </div>
            ))}
          </div>
        </div>
        <form className="rounded-md border border-slate-200 bg-white p-4">
          <h2 className="text-sm font-semibold">Create job</h2>
          <input className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none" placeholder="Title" />
          <textarea className="mt-3 min-h-48 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none" placeholder="Paste job description" />
          <button className="mt-3 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white">Parse and index</button>
        </form>
      </section>
    </AppShell>
  );
}
