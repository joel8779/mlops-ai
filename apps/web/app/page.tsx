import { AppShell } from "@/components/app-shell";
import { BarChart3, Bot, BriefcaseBusiness, Search, UploadCloud, Users } from "lucide-react";

const stats = [
  { label: "Candidates", value: "128", icon: Users },
  { label: "Active jobs", value: "14", icon: BriefcaseBusiness },
  { label: "Avg match", value: "82%", icon: BarChart3 },
  { label: "AI actions", value: "46", icon: Bot }
];

const stages = ["Applied", "Screening", "Interview", "Technical Round", "Final Round", "Hired", "Rejected"];

export default function DashboardPage() {
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-semibold">Recruiter Dashboard</h1>
            <p className="text-sm text-slate-600">AI ranking, pipeline operations, and candidate intelligence</p>
          </div>
          <button className="inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-white">
            <UploadCloud size={18} />
            Upload resume
          </button>
        </div>
      </header>
      <section className="px-6 py-6">
        <div className="grid gap-4 md:grid-cols-4">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="rounded-md border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  {stat.label}
                  <Icon size={18} className="text-signal" />
                </div>
                <div className="mt-3 text-2xl font-semibold">{stat.value}</div>
              </div>
            );
          })}
        </div>
        <div className="mt-6 grid gap-6 xl:grid-cols-[1fr_360px]">
          <section className="overflow-hidden rounded-md border border-slate-200 bg-white">
            <div className="border-b border-slate-200 px-4 py-3 text-sm font-semibold">Hiring pipeline</div>
            <div className="grid min-h-80 grid-cols-1 gap-px bg-slate-200 md:grid-cols-7">
              {stages.map((stage) => (
                <div key={stage} className="bg-white p-3">
                  <div className="text-sm font-medium text-slate-700">{stage}</div>
                  <div className="mt-3 rounded-md border border-slate-200 p-3 text-sm">
                    <div className="font-medium">Candidate queue</div>
                    <div className="mt-1 text-xs text-slate-500">Live statuses sync from API</div>
                  </div>
                </div>
              ))}
            </div>
          </section>
          <section className="rounded-md border border-slate-200 bg-white p-4">
            <h2 className="text-sm font-semibold">Semantic search</h2>
            <div className="mt-3 flex rounded-md border border-slate-300">
              <input className="min-w-0 flex-1 rounded-md px-3 py-2 text-sm outline-none" placeholder="Find Python backend engineers with Docker" />
              <button className="m-1 inline-flex h-8 w-8 items-center justify-center rounded-md bg-signal text-white">
                <Search size={16} />
              </button>
            </div>
          </section>
        </div>
      </section>
    </AppShell>
  );
}
