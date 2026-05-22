import { BarChart3, Search, UploadCloud, Users } from "lucide-react";

const stats = [
  { label: "Candidates", value: "0", icon: Users },
  { label: "Active jobs", value: "0", icon: Search },
  { label: "Uploads today", value: "0", icon: UploadCloud },
  { label: "Ranking runs", value: "0", icon: BarChart3 }
];

export default function DashboardPage() {
  return (
    <main className="min-h-screen">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-normal">Resume Intelligence</h1>
            <p className="text-sm text-slate-600">Recruiter operations workspace</p>
          </div>
          <a
            href="/resumes"
            className="inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white"
          >
            <UploadCloud size={18} />
            Upload resume
          </a>
        </div>
      </div>

      <section className="mx-auto max-w-7xl px-6 py-6">
        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="rounded-md border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-600">{stat.label}</span>
                  <Icon size={18} className="text-signal" />
                </div>
                <div className="mt-3 text-2xl font-semibold">{stat.value}</div>
              </div>
            );
          })}
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <section className="rounded-md border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3">
              <h2 className="text-sm font-semibold">Candidate pipeline</h2>
            </div>
            <div className="grid grid-cols-5 gap-px bg-slate-200 text-sm">
              {["Sourced", "Parsed", "Matched", "Interview", "Offer"].map((stage) => (
                <div key={stage} className="min-h-56 bg-white p-3">
                  <div className="font-medium text-slate-700">{stage}</div>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-md border border-slate-200 bg-white p-4">
            <h2 className="text-sm font-semibold">Semantic search</h2>
            <div className="mt-3 flex rounded-md border border-slate-300 bg-white">
              <input
                className="min-w-0 flex-1 rounded-md px-3 py-2 text-sm outline-none"
                placeholder="Find Python developers with FastAPI and Docker"
              />
              <button className="m-1 inline-flex h-8 w-8 items-center justify-center rounded-md bg-signal text-white">
                <Search size={16} />
              </button>
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
