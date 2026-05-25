"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { BarChart3, Clock, Target, Zap, Users, TrendingUp, Award, Activity, Menu, X, LogOut, Home, UserSearch, MessageSquare, UploadCloud, BriefcaseBusiness } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { analyticsApi } from "@/lib/api";
import { fadeInUp } from "@/lib/animations";

export default function AnalyticsPage() {
  const { user, logout } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

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
      <div className="flex items-center justify-center min-h-screen bg-background">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }} className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent" />
      </div>
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
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="border-b border-background-border px-6 py-4">
          <div className="text-lg font-semibold text-foreground">Resume AI</div>
          <div className="text-sm text-foreground-muted">Analytics</div>
        </div>
        <nav className="space-y-1 p-4">
          {[
            { href: "/dashboard", label: "Dashboard", icon: Home },
            { href: "/candidates", label: "Candidates", icon: UserSearch },
            { href: "/search", label: "Search", icon: Target },
            { href: "/resumes", label: "Uploads", icon: UploadCloud },
            { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
            { href: "/analytics", label: "Analytics", icon: BarChart3 },
            { href: "/copilot", label: "Copilot", icon: MessageSquare }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm transition-colors ${
                  item.href === "/analytics" ? "bg-accent text-white" : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </a>
            );
          })}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 border-t border-background-border p-4">
          <button
            onClick={() => logout()}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm text-foreground-muted hover:bg-background-elevated hover:text-foreground transition-colors"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </motion.div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      {/* Main content */}
      <main className="lg:pl-72">
        <div className="border-b border-background-border bg-background-card px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-background-elevated transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h1 className="text-xl font-semibold text-foreground">Recruiter Analytics</h1>
        </div>

        <section className="p-6">
          <motion.div {...fadeInUp} className="grid gap-6">
            <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
              {metrics.map((metric) => {
                const Icon = metric.icon;
                return (
                  <div key={metric.label} className="rounded-xl bg-background-card border border-background-border p-4 hover:border-accent/50 transition-colors">
                    <div className="flex items-center justify-between text-sm text-foreground-muted">
                      {metric.label}
                      <Icon size={16} className="text-accent" />
                    </div>
                    <div className="mt-2 text-2xl font-semibold text-foreground">{metric.value}</div>
                  </div>
                );
              })}
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="rounded-xl bg-background-card border border-background-border p-6">
                <div className="flex items-center gap-2 mb-4">
                  <TrendingUp size={20} className="text-accent" />
                  <h2 className="text-lg font-semibold text-foreground">Hiring Funnel</h2>
                </div>
                <div className="space-y-3">
                  {funnelStages.map((stage) => {
                    const count = funnelData[stage.key] || 0;
                    const values = Object.values(funnelData || {}) as number[];
                    const maxCount = Math.max(...values, 1);
                    const percentage = (count / maxCount) * 100;
                    return (
                      <div key={stage.key}>
                        <div className="flex items-center justify-between text-sm">
                          <span className="font-medium text-foreground">{stage.label}</span>
                          <span className="text-foreground-muted">{count} candidates</span>
                        </div>
                        <div className="mt-1 h-2 rounded-full bg-background-border overflow-hidden">
                          <div
                            className="h-full rounded-full bg-accent transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="rounded-xl bg-background-card border border-background-border p-6">
                <div className="flex items-center gap-2 mb-4">
                  <BarChart3 size={20} className="text-accent" />
                  <h2 className="text-lg font-semibold text-foreground">Top Skills Demand</h2>
                </div>
                <div className="space-y-3">
                  {topSkills.slice(0, 8).map((skill: any, index: number) => (
                    <div key={index}>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium text-foreground">{skill.skill || skill}</span>
                        <span className="text-foreground-muted">{skill.count || skill}</span>
                      </div>
                      <div className="mt-1 h-2 rounded-full bg-background-border overflow-hidden">
                        <div
                          className="h-full rounded-full bg-accent transition-all"
                          style={{ width: `${Math.min(100, (skill.count / topSkills[0].count) * 100)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="rounded-xl bg-background-card border border-background-border p-6">
              <div className="flex items-center gap-2 mb-4">
                <Award size={20} className="text-accent" />
                <h2 className="text-lg font-semibold text-foreground">Ranking Quality</h2>
              </div>
              <div className="space-y-3">
                {[
                  { label: "Semantic", value: 38, color: "bg-accent" },
                  { label: "Skills", value: 24, color: "bg-accent/70" },
                  { label: "Experience", value: 14, color: "bg-accent/50" },
                  { label: "ATS", value: 11, color: "bg-accent/30" }
                ].map((segment) => (
                  <div key={segment.label} className="flex items-center justify-between text-sm">
                    <span className="text-foreground">{segment.label}</span>
                    <span className="font-medium text-accent">{segment.value}</span>
                  </div>
                ))}
                <div className="mt-4 flex h-3 overflow-hidden rounded-full bg-background-border">
                  {[
                    { width: "38%", color: "bg-accent" },
                    { width: "24%", color: "bg-accent/70" },
                    { width: "14%", color: "bg-accent/50" },
                    { width: "11%", color: "bg-accent/30" }
                  ].map((bar, i) => (
                    <div key={i} className={`h-full ${bar.color}`} style={{ width: bar.width }} />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        </section>
      </main>
    </div>
  );
}
