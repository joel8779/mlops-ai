"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { 
  BarChart3, 
  Bot, 
  BriefcaseBusiness, 
  UploadCloud, 
  Users,
  ArrowUpRight
} from "lucide-react";
import { analyticsApi } from "@/lib/api";
import AppShell from "@/components/app-shell";

export default function DashboardPage() {
  const router = useRouter();
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
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="h-8 w-8 rounded-full border-2 border-foreground-border border-t-foreground animate-spin" />
        </div>
      </AppShell>
    );
  }

  const hasData = analytics && (analytics.total_candidates > 0 || analytics.total_jobs > 0);

  const stats = [
    { label: "Candidates", value: analytics?.total_candidates?.toString() || "0", icon: Users },
    { label: "Active jobs", value: analytics?.total_jobs?.toString() || "0", icon: BriefcaseBusiness },
    { label: "Avg match", value: analytics?.ranking_precision ? Math.round(analytics.ranking_precision * 100) + "%" : "N/A", icon: BarChart3 },
    { label: "AI actions", value: analytics?.total_actions?.toString() || "0", icon: Bot },
  ];

  const stages = [
    { key: "applied", label: "Applied", count: analytics?.hiring_funnel?.applied || 0 },
    { key: "screening", label: "Screening", count: analytics?.hiring_funnel?.screening || 0 },
    { key: "interview", label: "Interview", count: analytics?.hiring_funnel?.interview || 0 },
    { key: "technical_round", label: "Technical", count: analytics?.hiring_funnel?.technical_round || 0 },
    { key: "final_round", label: "Final", count: analytics?.hiring_funnel?.final_round || 0 },
    { key: "hired", label: "Hired", count: analytics?.hiring_funnel?.hired || 0 },
    { key: "rejected", label: "Rejected", count: analytics?.hiring_funnel?.rejected || 0 },
  ];

  return (
    <AppShell>
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-xl font-semibold">Dashboard</h1>
            <p className="text-sm text-foreground-muted">Recruiting intelligence</p>
          </div>
          <button
            onClick={() => router.push("/documents")}
            className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors"
          >
            <UploadCloud className="h-4 w-4" />
            Upload
          </button>
        </div>

        {!hasData ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="h-16 w-16 rounded-full bg-background-elevated flex items-center justify-center mb-6">
              <UploadCloud className="h-8 w-8 text-foreground-muted" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Get Started</h2>
            <p className="text-foreground-muted max-w-md mb-6">
              Upload your first resume to start using recruiting intelligence
            </p>
            <button
              onClick={() => router.push("/documents")}
              className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-6 py-3 text-sm font-medium hover:bg-foreground/90 transition-colors"
            >
              <UploadCloud className="h-4 w-4" />
              Upload Resume
            </button>
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
              {stats.map((stat) => {
                const Icon = stat.icon;
                return (
                  <div
                    key={stat.label}
                    className="rounded-lg bg-background-card border border-background-border p-6"
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="inline-flex h-10 w-10 items-center justify-center rounded-md bg-background-elevated">
                        <Icon className="h-5 w-5 text-foreground-muted" />
                      </div>
                    </div>
                    <div className="text-2xl font-semibold mb-1">{stat.value}</div>
                    <div className="text-sm text-foreground-muted">{stat.label}</div>
                  </div>
                );
              })}
            </div>

            {/* Main Grid */}
            <div className="grid gap-6 lg:grid-cols-3">
              {/* Hiring Pipeline */}
              <div className="rounded-lg bg-background-card border border-background-border p-6 lg:col-span-2">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-base font-semibold">Hiring Pipeline</h2>
                </div>
                <div className="grid gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7">
                  {stages.map((stage) => (
                    <div
                      key={stage.key}
                      className="rounded-md bg-background-elevated border border-background-border p-3"
                    >
                      <div className="text-xs font-medium text-foreground mb-2">{stage.label}</div>
                      <div className="text-xl font-semibold text-foreground mb-1">{stage.count}</div>
                      <div className="text-xs text-foreground-muted">candidates</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="space-y-6">
                {/* Semantic Search */}
                <div className="rounded-lg bg-background-card border border-background-border p-6">
                  <h2 className="text-base font-semibold mb-4">Semantic Search</h2>
                  <div className="relative">
                    <input
                      className="w-full rounded-md bg-background-elevated border border-background-border px-3 py-2 pr-10 text-sm text-foreground placeholder-foreground-muted focus:outline-none focus:border-foreground/50 transition-colors"
                      placeholder="Find Python engineers..."
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          router.push("/search");
                        }
                      }}
                    />
                    <button
                      onClick={() => router.push("/search")}
                      className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-md bg-foreground text-background flex items-center justify-center hover:bg-foreground/90 transition-colors"
                    >
                      <ArrowUpRight className="h-4 w-4" />
                    </button>
                  </div>
                </div>

                {/* Upload Action */}
                <div className="rounded-lg bg-background-card border border-background-border p-6">
                  <h2 className="text-base font-semibold mb-4">Quick Upload</h2>
                  <button
                    onClick={() => router.push("/documents")}
                    className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-background-elevated border border-background-border px-4 py-3 text-sm font-medium hover:bg-background-elevated/80 transition-colors"
                  >
                    <UploadCloud className="h-4 w-4" />
                    Upload Resume
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
