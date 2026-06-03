"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  Cpu,
  FileText,
  Home,
  LogOut,
  Menu,
  Radar,
  Search,
  Settings,
  Shield,
  Users,
  X,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { getAccessToken } from "@/lib/api";

interface AppShellProps {
  children: React.ReactNode;
}

const sidebarItems = [
  { icon: Home, label: "Dashboard", href: "/dashboard" },
  { icon: FileText, label: "Documents", href: "/documents" },
  { icon: Users, label: "Candidates", href: "/candidates" },
  { icon: BriefcaseBusiness, label: "Jobs", href: "/jobs" },
  { icon: Search, label: "Search", href: "/search" },
  { icon: BarChart3, label: "Analytics", href: "/analytics" },
  { icon: Settings, label: "Settings", href: "/settings" },
];

export default function AppShell({ children }: AppShellProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, loading, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user && !getAccessToken()) {
      router.replace("/login");
    }
  }, [loading, router, user]);

  const handleLogout = () => {
    void logout().finally(() => router.replace("/login"));
  };

  if (loading || (!user && !getAccessToken())) {
    return (
      <div className="neural-bg flex min-h-screen items-center justify-center text-foreground">
        <div className="ops-panel-strong scanline rounded-lg p-8 text-center">
          <Cpu className="mx-auto h-8 w-8 animate-pulse text-accent" />
          <div className="mt-4 text-sm uppercase tracking-[0.32em] text-foreground-muted">Syncing session</div>
        </div>
      </div>
    );
  }

  return (
    <div className="neural-bg min-h-screen text-foreground">
      <div className="pointer-events-none fixed inset-0 ops-grid opacity-70" />
      <div className="pointer-events-none fixed inset-x-0 top-0 h-48 bg-gradient-to-b from-accent/10 to-transparent" />

      {sidebarOpen && <div onClick={() => setSidebarOpen(false)} className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden" />}

      <aside
        className={`fixed left-0 top-0 z-50 h-full w-72 border-r border-white/10 bg-background/78 backdrop-blur-2xl transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          <div className="border-b border-white/10 p-5">
            <div className="flex items-center justify-between">
              <Link href="/dashboard" className="flex items-center gap-3">
                <div className="h-11 w-11 rounded-lg border border-accent/30 bg-accent/10 shadow-glow">
                  <div className="flex h-full w-full items-center justify-center">
                    <Radar className="h-5 w-5 text-accent" />
                  </div>
                </div>
                <div>
                  <div className="text-base font-semibold tracking-wide">NEURAL OPS</div>
                  <div className="text-[11px] uppercase tracking-[0.24em] text-foreground-subtle">Command Center</div>
                </div>
              </Link>
              <button onClick={() => setSidebarOpen(false)} className="rounded-md p-2 text-foreground-muted hover:bg-white/5 hover:text-foreground lg:hidden">
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="mt-5 rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <div className="flex items-center justify-between text-xs text-foreground-muted">
                <span>System state</span>
                <span className="text-success">ONLINE</span>
              </div>
              <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-white/10">
                <div className="h-full w-2/3 rounded-full bg-accent shadow-glow" />
              </div>
            </div>
          </div>

          <nav className="flex-1 overflow-y-auto p-4">
            <div className="mb-3 px-3 text-[11px] uppercase tracking-[0.24em] text-foreground-subtle">Operations</div>
            <div className="space-y-1">
              {sidebarItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`group flex items-center gap-3 rounded-lg px-3 py-3 text-sm transition-all ${
                      isActive
                        ? "border border-accent/30 bg-accent/10 text-foreground shadow-glow"
                        : "text-foreground-muted hover:border hover:border-white/10 hover:bg-white/[0.04] hover:text-foreground"
                    }`}
                  >
                    <Icon className={`h-4 w-4 ${isActive ? "text-accent" : "text-foreground-subtle group-hover:text-accent"}`} />
                    <span className="font-medium">{item.label}</span>
                    {isActive && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-accent" />}
                  </Link>
                );
              })}
            </div>
          </nav>

          <div className="border-t border-white/10 p-4">
            <div className="mb-3 rounded-lg border border-white/10 bg-white/[0.03] p-3">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-md bg-violet/10 text-violet-subtle">
                  <Shield className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <div className="truncate text-sm font-medium">{user?.full_name || user?.email}</div>
                  <div className="text-xs text-foreground-subtle">Authenticated operator</div>
                </div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-lg border border-white/10 bg-white/[0.03] px-3 py-3 text-sm text-foreground-muted transition-colors hover:border-error/30 hover:bg-error/10 hover:text-foreground"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </aside>

      <main className="relative min-h-screen lg:ml-72">
        <header className="sticky top-0 z-30 border-b border-white/10 bg-background/70 px-4 py-3 backdrop-blur-xl sm:px-6">
          <div className="flex items-center gap-4">
            <button onClick={() => setSidebarOpen(!sidebarOpen)} className="rounded-lg border border-white/10 bg-white/[0.03] p-2 text-foreground-muted hover:text-foreground lg:hidden">
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <div className="flex min-w-0 flex-1 items-center gap-3">
              <Activity className="h-4 w-4 text-accent" />
              <div className="truncate text-xs uppercase tracking-[0.28em] text-foreground-subtle">Recruiting intelligence workstation</div>
            </div>
            <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-foreground-muted sm:flex">
              <span className="h-1.5 w-1.5 rounded-full bg-success" />
              Live API
            </div>
          </div>
        </header>

        <div className="relative z-10 p-4 sm:p-6 xl:p-8">{children}</div>
      </main>
    </div>
  );
}
