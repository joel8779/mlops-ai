"use client";

import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Bot, Send } from "lucide-react";

export default function CopilotPage() {
  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Recruiter AI Copilot</h1>
        <p className="text-sm text-slate-600">RAG-backed answers with candidate citations</p>
      </header>
      <section className="mx-auto max-w-4xl p-6">
        <div className="min-h-96 rounded-md border border-slate-200 bg-white p-4">
          <div className="flex gap-3 rounded-md bg-slate-50 p-3 text-sm">
            <Bot size={18} className="text-signal" />
            Ask for ranked candidate shortlists, comparison notes, or interview plans.
          </div>
        </div>
        <div className="mt-3 flex gap-2">
          <input className="min-w-0 flex-1 rounded-md border border-slate-300 px-3 py-2 outline-none" placeholder="Find top backend engineers for our fintech role" />
          <Button><Send size={16} />Ask</Button>
        </div>
      </section>
    </AppShell>
  );
}
