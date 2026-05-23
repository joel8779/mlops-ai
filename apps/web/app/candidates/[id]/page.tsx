import { AppShell } from "@/components/app-shell";
import { RankingVisualization } from "@/components/ranking-visualization";

export default async function CandidateProfilePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Candidate Profile</h1>
        <p className="text-sm text-slate-600">Profile ID: {id}</p>
      </header>
      <section className="grid gap-6 p-6 lg:grid-cols-[1fr_360px]">
        <article className="rounded-md border border-slate-200 bg-white p-5">
          <h2 className="text-lg font-semibold">AI summary</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            Strong backend profile with evidence across API design, PostgreSQL, Dockerized delivery, and production debugging.
          </p>
          <div className="mt-5 grid gap-3 md:grid-cols-3">
            {["FastAPI", "PostgreSQL", "Docker"].map((skill) => (
              <span key={skill} className="rounded-md bg-slate-100 px-3 py-2 text-sm">{skill}</span>
            ))}
          </div>
        </article>
        <RankingVisualization />
      </section>
    </AppShell>
  );
}
