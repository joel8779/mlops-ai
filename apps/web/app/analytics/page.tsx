"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/app-shell";
import { RankingVisualization } from "@/components/ranking-visualization";
import { BarChart3, Clock, Target, Zap, Users, TrendingUp, Award, Activity } from "lucide-react";
import { analyticsApi } from "@/lib/api";

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await analyticsApi.executive();
      setAnalytics(data);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center p-12">
          <div className="text-slate-600">Loading analytics...</div>
        </div>
      </AppShell>
    );
  }

  const metrics = [
    { label: "Time to hire", value: analytics?.time_to_hire || "18 days", icon: Clock },
    { label: "Interview conversion", value: analytics?.interview_conversion || "42%", icon: Target },
    { label: "Ranking precision@10", value: analytics?.ranking_precision || "0.81", icon: Award },
    { label: "Recruiter actions", value: analytics?.total_actions || "1,284", icon: Activity },
    { label: "AI usage", value: analytics?.ai_usage || "847", icon: Zap },
    { label: "Total candidates", value: analytics?.total_candidates || "128", icon: Users },
  ];

  const funnelData = analytics?.hiring_funnel || {};
  const funnelStages = [
    { key: "applied", label: "Applied" },
    { key: "screening", label: "Screening" },
    { key: "interview", label: "Interview" },
    { key: "technical_round", label: "Technical" },
    { key: "final_round", label: "Final" },
    { key: "hired", label: "Hired" },
  ];

  const topSkills = analytics?.top_skills || [];

  return (
    <AppShell>
      <header className="border-b border-slate-200 bg-white px-6 py-4">
        <h1 className="text-xl font-semibold">Recruiter Analytics</h1>
        <p className="text-sm text-slate-600">Executive hiring funnel and AI quality signals</p>
      </header>
      <section className="grid gap-6 p-6">
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          {metrics.map((metric) => {
            const Icon = metric.icon;
            return (
              <div key={metric.label} className="rounded-md border border-slate-200 bg-white p-4">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  {metric.label}
                  <Icon size={16} className="text-signal" />
                </div>
                <div className="mt-2 text-2xl font-semibold">{metric.value}</div>
              </div>
            );
          })}
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-md border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp size={20} className="text-signal" />
              <h2 className="text-lg font-semibold">Hiring Funnel</h2>
            </div>
            <div className="space-y-3">
              {funnelStages.map((stage, index) => {
                const count = funnelData[stage.key] || 0;
                const values = Object.values(funnelData || {}) as number[];
                const maxCount = Math.max(...values, 1);
                const percentage = (count / maxCount) * 100;
                return (
                  <div key={stage.key}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{stage.label}</span>
                      <span className="text-slate-600">{count} candidates</span>
                    </div>
                    <div className="mt-1 h-2 rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-signal transition-all"
                        style={{ width: `${percentage}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-white p-6">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 size={20} className="text-signal" />
              <h2 className="text-lg font-semibold">Top Skills Demand</h2>
            </div>
            <div className="space-y-3">
              {topSkills.slice(0, 8).map((skill: any, index: number) => (
                <div key={index}>
                  <div className="flex items-center justify-between text-sm">
                    <span className="font-medium">{skill.skill || skill}</span>
                    <span className="text-slate-600">{skill.count || skill}</span>
                  </div>
                  <div className="mt-1 h-2 rounded-full bg-slate-100">
                    <div
                      className="h-full rounded-full bg-signal transition-all"
                      style={{ width: `${Math.min(100, (skill.count / topSkills[0].count) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-md border border-slate-200 bg-white p-6">
          <div className="flex items-center gap-2 mb-4">
            <Award size={20} className="text-signal" />
            <h2 className="text-lg font-semibold">Ranking Quality</h2>
          </div>
          <RankingVisualization />
        </div>
      </section>
    </AppShell>
  );
}
