"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { ArrowLeft, KeyRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { authApi } from "@/lib/api";

type Step = "email" | "otp" | "reset" | "success";

export default function ForgotPasswordPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [otpCode, setOtpCode] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const requestReset = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setLoading(true);
    try {
      const response = await authApi.forgotPassword(email);
      setNotice(response.message);
      setStep("otp");
    } catch (err: any) {
      setError(err.message || "Unable to request reset code");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setNotice("");
    setLoading(true);
    try {
      const response = await authApi.verifyResetOtp(email, otpCode);
      setResetToken(response.reset_token);
      setNotice(response.message);
      setStep("reset");
    } catch (err: any) {
      setError(err.message || "Unable to verify reset code");
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (event: FormEvent) => {
    event.preventDefault();
    setError("");
    setNotice("");
    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await authApi.resetPassword({
        email,
        reset_token: resetToken,
        new_password: newPassword,
        confirm_password: confirmPassword,
      });
      setStep("success");
      window.setTimeout(() => router.replace("/login"), 1500);
    } catch (err: any) {
      setError(err.message || "Unable to reset password");
    } finally {
      setLoading(false);
    }
  };

  const resendCode = async () => {
    setError("");
    setNotice("");
    try {
      const response = await authApi.forgotPassword(email);
      setNotice(response.message);
    } catch (err: any) {
      setError(err.message || "Unable to resend reset code");
    }
  };

  return (
    <main className="neural-bg relative flex min-h-screen items-center justify-center p-6 text-foreground">
      <div className="pointer-events-none fixed inset-0 ops-grid opacity-70" />
      <div className="relative w-full max-w-md">
        <Link href="/login" className="mb-6 inline-flex items-center gap-2 text-sm text-foreground-muted hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
          Back to sign in
        </Link>
        <form
          onSubmit={step === "email" ? requestReset : step === "otp" ? verifyOtp : resetPassword}
          className="ops-panel-strong scanline rounded-xl p-6"
        >
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-lg border border-accent/30 bg-accent/10 shadow-glow">
              <KeyRound className="h-5 w-5 text-accent" />
            </div>
            <div>
              <h1 className="text-xl font-semibold">Reset password</h1>
              <p className="text-sm text-foreground-muted">
                {step === "email" && "Enter your account email."}
                {step === "otp" && "Enter the reset code sent by email."}
                {step === "reset" && "Choose a new password."}
                {step === "success" && "Password updated. Redirecting to sign in."}
              </p>
            </div>
          </div>

          {error && <div className="mt-4 rounded-md border border-error/30 bg-error/10 p-3 text-sm text-error">{error}</div>}
          {notice && <div className="mt-4 rounded-md border border-accent/30 bg-accent/10 p-3 text-sm text-accent">{notice}</div>}

          {step === "email" && (
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
          )}

          {step === "otp" && (
            <>
              <label className="mt-5 block text-sm text-foreground-muted">
                Reset code
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
              <button type="button" onClick={resendCode} className="mt-3 w-full text-sm text-accent hover:underline">
                Resend reset code
              </button>
            </>
          )}

          {step === "reset" && (
            <>
              <label className="mt-5 block text-sm text-foreground-muted">
                New password
                <input
                  className="ops-input mt-2 w-full rounded-md px-3 py-3"
                  type="password"
                  value={newPassword}
                  onChange={(event) => setNewPassword(event.target.value)}
                  minLength={8}
                  required
                />
              </label>
              <label className="mt-4 block text-sm text-foreground-muted">
                Confirm password
                <input
                  className="ops-input mt-2 w-full rounded-md px-3 py-3"
                  type="password"
                  value={confirmPassword}
                  onChange={(event) => setConfirmPassword(event.target.value)}
                  minLength={8}
                  required
                />
              </label>
            </>
          )}

          {step !== "success" ? (
            <Button className="ops-button mt-5 w-full" disabled={loading}>
              {loading ? "Working..." : step === "email" ? "Send reset code" : step === "otp" ? "Verify code" : "Reset password"}
            </Button>
          ) : (
            <Button type="button" className="ops-button mt-5 w-full" onClick={() => router.replace("/login")}>
              Return to sign in
            </Button>
          )}
        </form>
      </div>
    </main>
  );
}
