import { AppShell } from "@/components/app-shell";
import { RankingVisualization } from "@/components/ranking-visualization";

const metrics = [
  ["Time to hire", "18 days"],
  ["Interview conversion", "42%"],
  ["Ranking precision@10", "0.81"],
  ["Recruiter actions", "1,284"]
];

export default function AnalyticsPage() {
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Recruiter Analytics</h1>
        <p className="text-sm text-slate-600">Executive hiring funnel and AI quality signals</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[1fr_360px]">
        <div className="grid gap-4 md:grid-cols-2">
          {metrics.map(([label, value]) => (
            <div key={label} className="rounded-md border border-slate-200 bg-white p-4">
              <div className="text-sm text-slate-600">{label}</div>
              <div className="mt-2 text-2xl font-semibold">{value}</div>
            </div>
          ))}
        </div>
        <RankingVisualization />
      </section>
    </AppShell>
  );
}
