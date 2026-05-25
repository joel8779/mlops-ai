"use client";

import AppShell from "@/components/app-shell";
import { useAuth } from "@/lib/auth-context";

export default function SettingsPage() {
  const { user, logout } = useAuth();

  return (
    <AppShell>
      <div className="space-y-6">
        <div className="ops-panel-strong rounded-xl p-5">
          <div className="text-xs uppercase tracking-[0.28em] text-accent">Operator settings</div>
          <h1 className="mt-2 text-xl font-semibold">Settings</h1>
          <p className="text-sm text-foreground-muted">Authenticated workspace and account state.</p>
        </div>
        <section className="ops-panel rounded-xl p-5">
          <h2 className="text-base font-semibold">Account</h2>
          <div className="mt-4 grid gap-3 text-sm">
            <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
              <div className="text-foreground-muted">Name</div>
              <div className="mt-1">{user?.full_name || "Not provided"}</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
              <div className="text-foreground-muted">Email</div>
              <div className="mt-1">{user?.email || "Not available"}</div>
            </div>
            <div className="rounded-md border border-white/10 bg-white/[0.03] p-3">
              <div className="text-foreground-muted">Organization</div>
              <div className="mt-1">{user?.organization_id || "Not available"}</div>
            </div>
          </div>
        </section>
        <section className="ops-panel rounded-xl p-5">
          <h2 className="text-base font-semibold">Workspace controls</h2>
          <p className="mt-2 text-sm text-foreground-muted">
            Session state is stored locally and sent to backend APIs through bearer authentication.
          </p>
          <button onClick={logout} className="ops-button-secondary mt-4 rounded-lg px-4 py-2 text-sm">
            Logout
          </button>
        </section>
      </div>
    </AppShell>
  );
}
