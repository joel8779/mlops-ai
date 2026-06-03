"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ArrowLeft, Radar } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";
import { authApi } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [formData, setFormData] = useState({
    organization_name: "",
    full_name: "",
    email: "",
    password: "",
    organization_pin: "",
  });
  const [otpCode, setOtpCode] = useState("");
  const [awaitingOtp, setAwaitingOtp] = useState(false);
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(formData);
      setAwaitingOtp(true);
      setNotice("Account created. Enter the verification code sent to your email.");
    } catch (err: any) {
      setError(err.message || "Unable to create account");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.verifyOtp(formData.email, otpCode);
      router.replace("/login");
    } catch (err: any) {
      setError(err.message || "Unable to verify code");
    } finally {
      setLoading(false);
    }
  };

  const resendOtp = async () => {
    setError("");
    setNotice("");
    try {
      await authApi.sendOtp(formData.email);
      setNotice("A new verification code was sent.");
    } catch (err: any) {
      setError(err.message || "Unable to resend verification code");
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
        <form onSubmit={awaitingOtp ? verifyOtp : handleSubmit} className="ops-panel-strong scanline rounded-xl p-6">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 shadow-glow">
              <Radar className="h-5 w-5 text-accent" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Create operator account</h1>
              <p className="text-sm text-foreground-muted">Initialize a recruiting workspace.</p>
            </div>
          </div>
          {error && <div className="mt-4 rounded-md border border-error/30 bg-error/10 p-3 text-sm text-error">{error}</div>}
          {notice && <div className="mt-4 rounded-md border border-accent/30 bg-accent/10 p-3 text-sm text-accent">{notice}</div>}
          {!awaitingOtp ? (
            <>
              {[
                ["organization_name", "Organization"],
                ["full_name", "Full name"],
                ["email", "Email"],
                ["password", "Password"],
                ["organization_pin", "Organization PIN"],
              ].map(([key, label]) => (
                <label key={key} className="mt-4 block text-sm text-foreground-muted">
                  {label}
                  <input
                    className="ops-input mt-2 w-full rounded-md px-3 py-3"
                    type={key === "password" || key === "organization_pin" ? "password" : key === "email" ? "email" : "text"}
                    value={formData[key as keyof typeof formData]}
                    onChange={(event) => setFormData({ ...formData, [key]: event.target.value })}
                    minLength={key === "organization_pin" ? 6 : undefined}
                    maxLength={key === "organization_pin" ? 6 : undefined}
                    required
                  />
                </label>
              ))}
            </>
          ) : (
            <label className="mt-4 block text-sm text-foreground-muted">
              Email verification code
              <input
                className="ops-input mt-2 w-full rounded-md px-3 py-3"
                value={otpCode}
                onChange={(event) => setOtpCode(event.target.value)}
                minLength={6}
                maxLength={6}
                inputMode="numeric"
                required
              />
            </label>
          )}
          <Button className="ops-button mt-5 w-full" disabled={loading}>
            {loading ? "Working..." : awaitingOtp ? "Verify email" : "Launch workspace"}
          </Button>
          {awaitingOtp && (
            <button type="button" onClick={resendOtp} className="mt-3 w-full text-sm text-accent hover:underline">
              Resend verification code
            </button>
          )}
          <p className="mt-4 text-center text-sm text-foreground-muted">
            Already registered?{" "}
            <Link href="/login" className="text-accent hover:underline">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </main>
  );
}
