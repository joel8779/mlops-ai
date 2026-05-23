"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

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
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to sign up");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm rounded-md border border-slate-200 bg-white p-6">
        <h1 className="text-xl font-semibold">Create account</h1>
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
        <input
          className="mt-4 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
          placeholder="Organization name"
          value={formData.organization_name}
          onChange={(e) => setFormData({ ...formData, organization_name: e.target.value })}
          required
        />
        <input
          className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
          placeholder="Full name"
          value={formData.full_name}
          onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
          required
        />
        <input
          className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
          placeholder="Email"
          type="email"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
        />
        <input
          className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none"
          placeholder="Password"
          type="password"
          value={formData.password}
          onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          required
        />
        <Button className="mt-4 w-full" disabled={loading}>
          {loading ? "Creating account..." : "Sign up"}
        </Button>
        <p className="mt-4 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <a href="/sign-in" className="text-blue-600 hover:underline">
            Sign in
          </a>
        </p>
      </form>
    </main>
  );
}
