"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function SignUpPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    full_name: "",
    organization_name: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await register(formData);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to sign up");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-6">
      <div className="w-full max-w-sm">
        <Link
          href="/landing"
          className="inline-flex items-center gap-2 text-sm text-foreground-muted hover:text-foreground mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to landing
        </Link>
        <form onSubmit={handleSubmit} className="rounded-xl border border-background-border bg-background-card p-6">
          <h1 className="text-xl font-semibold text-foreground">Create account</h1>
          {error && <p className="mt-2 text-sm text-error">{error}</p>}
          <input
            className="mt-4 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
            placeholder="Organization name"
            value={formData.organization_name}
            onChange={(e) => setFormData({ ...formData, organization_name: e.target.value })}
            required
          />
          <input
            className="mt-3 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
            placeholder="Full name"
            value={formData.full_name}
            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
            required
          />
          <input
            className="mt-3 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
            placeholder="Email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
          />
          <input
            className="mt-3 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
            placeholder="Password"
            type="password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
          />
          <Button className="mt-4 w-full bg-accent hover:bg-accent/90" disabled={loading}>
            {loading ? "Creating account..." : "Sign up"}
          </Button>
          <p className="mt-4 text-center text-sm text-foreground-muted">
            Already have an account?{" "}
            <a href="/sign-in" className="text-accent hover:underline">
              Sign in
            </a>
          </p>
        </form>
      </div>
    </main>
  );
}
