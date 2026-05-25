"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { 
  BarChart3, 
  Bot, 
  BriefcaseBusiness, 
  Search, 
  UploadCloud, 
  Users,
  TrendingUp,
  Activity,
  Sparkles,
  ArrowUpRight,
  Clock,
  Zap,
  Target,
  Menu,
  X,
  Home,
  FileText,
  MessageSquare,
  Settings
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { analyticsApi } from "@/lib/api";
import Link from "next/link";

export default function DashboardPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!authLoading && !user) {
      router.push("/sign-in");
    }
  }, [authLoading, user, router]);

  useEffect(() => {
    if (user) {
      loadAnalytics();
    }
  }, [user]);

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

  if (authLoading || loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="h-12 w-12 rounded-full border-4 border-accent border-t-transparent"
        />
      </div>
    );
  }

  const stats = [
    { label: "Candidates", value: analytics?.total_candidates?.toString() || "0", icon: Users, change: "+12%", trend: "up" },
    { label: "Active jobs", value: analytics?.total_jobs?.toString() || "0", icon: BriefcaseBusiness, change: "+5%", trend: "up" },
    { label: "Avg match", value: "82%", icon: BarChart3, change: "+8%", trend: "up" },
    { label: "AI actions", value: analytics?.total_actions?.toString() || "0", icon: Bot, change: "+23%", trend: "up" },
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

  const recentActivities = [
    { action: "New candidate applied", time: "2 min ago", type: "candidate" },
    { action: "Interview scheduled", time: "15 min ago", type: "interview" },
    { action: "AI score updated", time: "1 hour ago", type: "ai" },
    { action: "Job posting created", time: "3 hours ago", type: "job" },
  ];

  const aiRecommendations = [
    { title: "Schedule follow-up with John Doe", priority: "high" },
    { title: "Review top 3 candidates for Senior Engineer", priority: "medium" },
    { title: "Update job requirements for ML Engineer", priority: "low" },
  ];

  const sidebarItems = [
    { icon: Home, label: "Dashboard", href: "/dashboard", active: true },
    { icon: Users, label: "Candidates", href: "/candidates" },
    { icon: BriefcaseBusiness, label: "Jobs", href: "/jobs" },
    { icon: FileText, label: "Resumes", href: "/resumes" },
    { icon: Search, label: "Search", href: "/search" },
    { icon: MessageSquare, label: "AI Copilot", href: "/copilot" },
    { icon: BarChart3, label: "Analytics", href: "/analytics" },
    { icon: Settings, label: "Settings", href: "/settings" },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-background-border">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-accent flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="font-bold text-lg">Resume AI</div>
                <div className="text-xs text-foreground-muted">Intelligent Hiring</div>
              </div>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-foreground-muted hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-4 py-3 transition-colors ${
                      item.active
                        ? "bg-accent/10 text-foreground border border-accent/30"
                        : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                );
              })}
            </div>
          </nav>

          {/* User */}
          <div className="p-4 border-t border-background-border">
            <div className="flex items-center gap-3 rounded-lg bg-background-elevated p-3">
              <div className="h-10 w-10 rounded-full bg-accent/20" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{user?.email || "User"}</div>
                <div className="text-xs text-foreground-muted">Recruiter</div>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      {/* Main Content */}
      <div className="lg:pl-72">
        {/* Header */}
        <header className="sticky top-0 z-30 border-b border-background-border bg-background/80 backdrop-blur-xl">
          <div className="flex items-center justify-between px-6 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-foreground-muted hover:text-foreground"
              >
                <Menu className="h-6 w-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold">Dashboard</h1>
                <p className="text-sm text-foreground-muted">AI-powered recruiting intelligence</p>
              </div>
            </div>
            <button
              onClick={() => router.push("/resumes")}
              className="inline-flex items-center gap-2 rounded-lg bg-accent px-6 py-3 font-semibold hover:bg-accent/90 transition-colors"
            >
              <UploadCloud className="h-5 w-5" />
              Upload Resume
            </button>
          </div>
        </header>

        {/* Content */}
        <main className="p-6">
          {/* Stats Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8"
          >
            {stats.map((stat, i) => {
              const Icon = stat.icon;
              return (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="group rounded-xl bg-background-card border border-background-border p-6 hover:border-accent/50 transition-colors"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="inline-flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10 group-hover:bg-accent/20 transition-colors">
                      <Icon className="h-6 w-6 text-accent" />
                    </div>
                    <div className="flex items-center gap-1 text-success text-sm">
                      <ArrowUpRight className="h-4 w-4" />
                      {stat.change}
                    </div>
                  </div>
                  <div className="text-3xl font-bold mb-1">{stat.value}</div>
                  <div className="text-foreground-muted">{stat.label}</div>
                </motion.div>
              );
            })}
          </motion.div>

          {/* Main Grid */}
          <div className="grid gap-6 xl:grid-cols-[1fr_400px]">
            {/* Hiring Pipeline */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="rounded-xl bg-background-card border border-background-border p-6"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold">Hiring Pipeline</h2>
                <div className="flex items-center gap-2 text-sm text-foreground-muted">
                  <Activity className="h-4 w-4" />
                  Live
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-7">
                {stages.map((stage, i) => (
                  <motion.div
                    key={stage.key}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 + i * 0.05 }}
                    className="rounded-lg bg-background-elevated border border-background-border p-4 hover:border-accent/30 transition-colors"
                  >
                    <div className="text-sm font-medium text-foreground mb-3">{stage.label}</div>
                    <div className="text-2xl font-bold text-foreground mb-1">{stage.count}</div>
                    <div className="text-xs text-foreground-subtle">candidates</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Right Column */}
            <div className="space-y-6">
              {/* Semantic Search Quick Action */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                className="rounded-xl bg-background-card border border-background-border p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Search className="h-5 w-5 text-accent" />
                  <h2 className="text-lg font-semibold">Semantic Search</h2>
                </div>
                <div className="relative">
                  <input
                    className="w-full rounded-lg bg-background-elevated border border-background-border px-4 py-3 pr-12 text-foreground placeholder-foreground-subtle focus:outline-none focus:border-accent/50 transition-colors"
                    placeholder="Find Python engineers with Docker..."
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        router.push("/search");
                      }
                    }}
                  />
                  <button
                    onClick={() => router.push("/search")}
                    className="absolute right-2 top-1/2 -translate-y-1/2 h-10 w-10 rounded-lg bg-accent flex items-center justify-center hover:bg-accent/90 transition-colors"
                  >
                    <ArrowUpRight className="h-5 w-5" />
                  </button>
                </div>
              </motion.div>

              {/* AI Recommendations */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.5 }}
                className="rounded-xl bg-background-card border border-background-border p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Sparkles className="h-5 w-5 text-accent" />
                  <h2 className="text-lg font-semibold">AI Recommendations</h2>
                </div>
                <div className="space-y-3">
                  {aiRecommendations.map((rec, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + i * 0.1 }}
                      className="flex items-start gap-3 rounded-lg bg-background-elevated p-3 border border-background-border hover:border-accent/30 transition-colors cursor-pointer"
                    >
                      <div className={`h-2 w-2 rounded-full mt-2 ${
                        rec.priority === "high" ? "bg-error" : rec.priority === "medium" ? "bg-warning" : "bg-success"
                      }`} />
                      <div className="flex-1 text-sm text-foreground">{rec.title}</div>
                      <ArrowUpRight className="h-4 w-4 text-foreground-subtle" />
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Recent Activity */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 }}
                className="rounded-xl bg-background-card border border-background-border p-6"
              >
                <div className="flex items-center gap-2 mb-4">
                  <Clock className="h-5 w-5 text-accent" />
                  <h2 className="text-lg font-semibold">Recent Activity</h2>
                </div>
                <div className="space-y-3">
                  {recentActivities.map((activity, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: 10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.7 + i * 0.1 }}
                      className="flex items-start gap-3 text-sm"
                    >
                      <div className={`h-2 w-2 rounded-full mt-2 ${
                        activity.type === "candidate" ? "bg-accent" : activity.type === "interview" ? "bg-success" : activity.type === "ai" ? "bg-accent" : "bg-warning"
                      }`} />
                      <div className="flex-1">
                        <div className="text-foreground">{activity.action}</div>
                        <div className="text-xs text-foreground-subtle">{activity.time}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
