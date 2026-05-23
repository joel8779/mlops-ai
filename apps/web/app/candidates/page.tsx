import { AppShell } from "@/components/app-shell";
import { Bookmark, MessageSquare, Star } from "lucide-react";

const candidates = [
  { name: "Aarav Sharma", role: "Backend Engineer", score: 91, skills: "FastAPI, Docker, PostgreSQL", stage: "Technical Round" },
  { name: "Meera Iyer", role: "ML Engineer", score: 88, skills: "NLP, PyTorch, MLflow", stage: "Screening" },
  { name: "Kabir Khan", role: "Frontend Engineer", score: 84, skills: "Next.js, TypeScript, Tailwind", stage: "Interview" }
];

export default function CandidatesPage() {
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Candidates</h1>
        <p className="text-sm text-slate-600">Ranked profiles with workflow actions</p>
      </header>
      <section className="p-6">
        <div className="overflow-hidden rounded-md border border-slate-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-100 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Candidate</th>
                <th className="px-4 py-3">Skills</th>
                <th className="px-4 py-3">Match</th>
                <th className="px-4 py-3">Stage</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {candidates.map((candidate) => (
                <tr key={candidate.name}>
                  <td className="px-4 py-3">
                    <div className="font-medium">{candidate.name}</div>
                    <div className="text-xs text-slate-500">{candidate.role}</div>
                  </td>
                  <td className="px-4 py-3">{candidate.skills}</td>
                  <td className="px-4 py-3"><span className="inline-flex items-center gap-1 font-medium"><Star size={15} />{candidate.score}%</span></td>
                  <td className="px-4 py-3">{candidate.stage}</td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <button className="rounded-md border border-slate-200 p-2"><Bookmark size={16} /></button>
                      <button className="rounded-md border border-slate-200 p-2"><MessageSquare size={16} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </AppShell>
  );
}
