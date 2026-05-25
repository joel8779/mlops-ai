"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ArrowLeft, Radar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message || "Unable to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="neural-bg relative flex min-h-screen items-center justify-center p-6 text-foreground">
      <div className="pointer-events-none fixed inset-0 ops-grid opacity-70" />
      <div className="relative w-full max-w-md">
        <Link href="/" className="mb-6 inline-flex items-center gap-2 text-sm text-foreground-muted hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back to Neural Ops
        </Link>
        <form onSubmit={handleSubmit} className="ops-panel-strong scanline rounded-xl p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 shadow-glow">
              <Radar className="h-5 w-5 text-accent" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Operator sign in</h1>
              <p className="text-sm text-foreground-muted">Access the recruiting command center.</p>
            </div>
          </div>
          {error && <div className="mt-4 rounded-md border border-error/30 bg-error/10 p-3 text-sm text-error">{error}</div>}
          <label className="mt-5 block text-sm text-foreground-muted">
            Email
            <input
              className="ops-input mt-2 w-full rounded-md px-3 py-3"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label className="mt-4 block text-sm text-foreground-muted">
            Password
            <input
              className="ops-input mt-2 w-full rounded-md px-3 py-3"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          <Button className="ops-button mt-5 w-full" disabled={loading}>
            {loading ? "Authenticating..." : "Enter command center"}
          </Button>
          <p className="mt-4 text-center text-sm text-foreground-muted">
            Need an account?{" "}
            <Link href="/signup" className="text-accent hover:underline">
              Sign up
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
