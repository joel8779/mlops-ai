"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function SignInPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await login(email, password);
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-background p-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-xl border border-background-border bg-background-card p-6">
        <h1 className="text-xl font-semibold text-foreground">Sign in</h1>
        {error && <p className="mt-2 text-sm text-error">{error}</p>}
        <input
          className="mt-4 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
          placeholder="Email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          className="mt-3 w-full rounded-lg border border-background-border bg-background-elevated px-4 py-3 text-sm text-foreground outline-none focus:border-accent/50 transition-colors"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <Button className="mt-4 w-full bg-accent hover:bg-accent/90" disabled={loading}>
          {loading ? "Signing in..." : "Continue"}
        </Button>
        <p className="mt-4 text-center text-sm text-foreground-muted">
          Don't have an account?{" "}
          <a href="/sign-up" className="text-accent hover:underline">
            Sign up
          </a>
        </p>
      </form>
    </main>
  );
}
