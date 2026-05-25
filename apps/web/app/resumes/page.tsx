"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2, Menu, X, LogOut, Home, UserSearch, MessageSquare, UploadCloud as UploadIcon, BriefcaseBusiness, BarChart3, Target } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { resumesApi } from "@/lib/api";
import { fadeInUp } from "@/lib/animations";

type UploadStatus = "idle" | "uploading" | "processing" | "complete" | "error";

export default function ResumeUploadPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleFileSelect = useCallback((selectedFile: File) => {
    setFile(selectedFile);
    setError("");
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  }, [handleFileSelect]);

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    setProgress(0);
    setError("");

    try {
      // Simulate upload progress
      const uploadInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 30) {
            clearInterval(uploadInterval);
            return 30;
          }
          return prev + 10;
        });
      }, 200);

      const result = await resumesApi.upload(file);
      clearInterval(uploadInterval);

      setStatus("processing");
      setProgress(30);

      // Simulate processing progress
      const processInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(processInterval);
            setStatus("complete");
            return 100;
          }
          return prev + 15;
        });
      }, 500);

      setUploadResult(result);
    } catch (err: any) {
      setStatus("error");
      setError(err.message || "Failed to upload resume");
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      <motion.div
        initial={{ x: -300 }}
        animate={{ x: sidebarOpen ? 0 : -300 }}
        className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
      >
        <div className="border-b border-background-border px-6 py-4">
          <div className="text-lg font-semibold text-foreground">Resume AI</div>
          <div className="text-sm text-foreground-muted">Uploads</div>
        </div>
        <nav className="space-y-1 p-4">
          {[
            { href: "/dashboard", label: "Dashboard", icon: Home },
            { href: "/candidates", label: "Candidates", icon: UserSearch },
            { href: "/search", label: "Search", icon: Target },
            { href: "/resumes", label: "Uploads", icon: UploadIcon },
            { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
            { href: "/analytics", label: "Analytics", icon: BarChart3 },
            { href: "/copilot", label: "Copilot", icon: MessageSquare }
          ].map((item) => {
            const Icon = item.icon;
            return (
              <a
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-4 py-3 text-sm transition-colors ${
                  item.href === "/resumes" ? "bg-accent text-white" : "text-foreground-muted hover:bg-background-elevated hover:text-foreground"
                }`}
              >
                <Icon size={18} />
                {item.label}
              </a>
            );
          })}
        </nav>
        <div className="absolute bottom-0 left-0 right-0 border-t border-background-border p-4">
          <button
            onClick={() => logout()}
            className="flex w-full items-center gap-3 rounded-lg px-4 py-3 text-sm text-foreground-muted hover:bg-background-elevated hover:text-foreground transition-colors"
          >
            <LogOut size={18} />
            Sign out
          </button>
        </div>
      </motion.div>

      {/* Mobile overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      {/* Main content */}
      <main className="lg:pl-72">
        <div className="border-b border-background-border bg-background-card px-6 py-4 flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-background-elevated transition-colors"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h1 className="text-xl font-semibold text-foreground">Resume Upload</h1>
        </div>

        <div className="mx-auto max-w-4xl px-6 py-8">
          <motion.div {...fadeInUp}>
            <div className="mb-6">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-sm font-medium text-accent hover:underline"
              >
                ← Dashboard
              </button>
              <h2 className="mt-2 text-2xl font-semibold text-foreground">Resume Upload</h2>
              <p className="mt-1 text-sm text-foreground-muted">
                Upload resumes for AI-powered parsing, skill extraction, and candidate creation
              </p>
            </div>

            {status === "complete" && uploadResult ? (
              <div className="rounded-xl border border-success/20 bg-success/10 p-6">
                <div className="flex items-center gap-3">
                  <CheckCircle className="text-success" size={24} />
                  <div>
                    <h3 className="font-semibold text-foreground">Resume uploaded successfully</h3>
                    <p className="text-sm text-foreground-muted">
                      Your resume is being processed. You can view the candidate profile once parsing is complete.
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => router.push("/dashboard")}
                  className="mt-4 rounded-lg bg-success px-4 py-2 text-sm font-medium text-white hover:bg-success/90 transition-colors"
                >
                  View Dashboard
                </button>
              </div>
            ) : (
              <div className="rounded-xl bg-background-card border border-background-border p-6">
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                  className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-background-border bg-background-elevated px-6 text-center transition-colors hover:border-accent/50 hover:bg-accent/5"
                >
                  <input
                    type="file"
                    onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                    accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                    className="sr-only"
                  />
                  {status === "idle" ? (
                    <>
                      <UploadCloud size={32} className="text-accent" />
                      <span className="mt-3 text-sm font-medium text-foreground">Drop a PDF, DOCX, PNG, or JPG resume</span>
                      <span className="mt-1 text-xs text-foreground-muted">or click to browse files</span>
                    </>
                  ) : status === "uploading" ? (
                    <>
                      <Loader2 className="animate-spin text-accent" size={32} />
                      <span className="mt-3 text-sm font-medium text-foreground">Uploading...</span>
                      <span className="mt-1 text-xs text-foreground-muted">{progress}% complete</span>
                    </>
                  ) : status === "processing" ? (
                    <>
                      <Loader2 className="animate-spin text-accent" size={32} />
                      <span className="mt-3 text-sm font-medium text-foreground">Processing with AI...</span>
                      <span className="mt-1 text-xs text-foreground-muted">{progress}% complete</span>
                    </>
                  ) : status === "error" ? (
                    <>
                      <AlertCircle className="text-error" size={32} />
                      <span className="mt-3 text-sm font-medium text-error">Upload failed</span>
                      <span className="mt-1 text-xs text-foreground-muted">{error}</span>
                    </>
                  ) : null}
                </div>

                {file && status === "idle" && (
                  <div className="mt-4 flex items-center justify-between rounded-lg border border-background-border bg-background-elevated p-3">
                    <div className="flex items-center gap-2">
                      <FileText size={18} className="text-foreground-muted" />
                      <span className="text-sm font-medium text-foreground">{file.name}</span>
                      <span className="text-xs text-foreground-muted">({(file.size / 1024).toFixed(1)} KB)</span>
                    </div>
                    <button
                      onClick={handleUpload}
                      className="rounded-lg bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent/90 transition-colors"
                    >
                      Upload
                    </button>
                  </div>
                )}

                {status === "processing" && (
                  <div className="mt-4 space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-foreground-muted">Upload</span>
                      <span className="text-success">✓ Complete</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-foreground-muted">OCR Extraction</span>
                      {progress >= 40 ? <span className="text-success">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-foreground-muted">Text Parsing</span>
                      {progress >= 60 ? <span className="text-success">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-foreground-muted">Skill Extraction</span>
                      {progress >= 80 ? <span className="text-success">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-foreground-muted">Embedding Generation</span>
                      {progress >= 100 ? <span className="text-success">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </div>
      </main>
    </div>
  );
}
