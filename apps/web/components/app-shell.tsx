"use client";

import { BarChart3, Bot, BriefcaseBusiness, LogOut, Search, UploadCloud, Users } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuth } from "@/lib/auth-context";

const nav = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/search", label: "Search", icon: Search },
  { href: "/resumes", label: "Uploads", icon: UploadCloud },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/copilot", label: "Copilot", icon: Bot }
] as const;

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push("/sign-in");
    }
  }, [loading, router, user]);

  if (loading || !user) {
    return (
      <div className="min-h-screen bg-slate-50 p-6">
        <div className="h-16 rounded-md border border-slate-200 bg-white" />
        <div className="mt-6 grid gap-4 md:grid-cols-4">
          {[0, 1, 2, 3].map((item) => (
            <div key={item} className="h-28 animate-pulse rounded-md bg-slate-200" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white lg:block">
        <div className="border-b border-slate-200 px-5 py-4">
          <div className="text-base font-semibold">Resume Intelligence</div>
          <div className="truncate text-xs text-slate-500">{user.email}</div>
        </div>
        <nav className="space-y-1 p-3" aria-label="Primary navigation">
          {nav.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-md px-3 py-2 text-sm ${
                  active ? "bg-signal text-white" : "text-slate-700 hover:bg-slate-100"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="absolute inset-x-0 bottom-0 border-t border-slate-200 p-3">
          <button
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </aside>
      <main className="lg:pl-64">{children}</main>
    </div>
  );
}
