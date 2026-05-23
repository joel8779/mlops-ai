"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { AppShell } from "@/components/app-shell";
import { resumesApi } from "@/lib/api";

type UploadStatus = "idle" | "uploading" | "processing" | "complete" | "error";

export default function ResumeUploadPage() {
  const router = useRouter();
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

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
    <AppShell>
      <main className="mx-auto min-h-screen max-w-4xl px-6 py-8">
        <div className="mb-6">
          <button
            onClick={() => router.push("/")}
            className="text-sm font-medium text-signal hover:underline"
          >
            ← Dashboard
          </button>
          <h1 className="mt-2 text-2xl font-semibold">Resume Upload</h1>
          <p className="mt-1 text-sm text-slate-600">
            Upload resumes for AI-powered parsing, skill extraction, and candidate creation
          </p>
        </div>

        {status === "complete" && uploadResult ? (
          <div className="rounded-md border border-green-200 bg-green-50 p-6">
            <div className="flex items-center gap-3">
              <CheckCircle className="text-green-600" size={24} />
              <div>
                <h2 className="font-semibold text-green-900">Resume uploaded successfully</h2>
                <p className="text-sm text-green-700">
                  Your resume is being processed. You can view the candidate profile once parsing is complete.
                </p>
              </div>
            </div>
            <button
              onClick={() => router.push("/")}
              className="mt-4 rounded-md bg-green-600 px-4 py-2 text-sm font-medium text-white hover:bg-green-700"
            >
              View Dashboard
            </button>
          </div>
        ) : (
          <div className="rounded-md border border-slate-200 bg-white p-6">
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed border-slate-300 bg-slate-50 px-6 text-center transition-colors hover:border-signal hover:bg-signal/5"
            >
              <input
                type="file"
                onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                accept=".pdf,.docx,.doc,.png,.jpg,.jpeg"
                className="sr-only"
              />
              {status === "idle" ? (
                <>
                  <UploadCloud size={32} className="text-signal" />
                  <span className="mt-3 text-sm font-medium">Drop a PDF, DOCX, PNG, or JPG resume</span>
                  <span className="mt-1 text-xs text-slate-600">or click to browse files</span>
                </>
              ) : status === "uploading" ? (
                <>
                  <Loader2 className="animate-spin text-signal" size={32} />
                  <span className="mt-3 text-sm font-medium">Uploading...</span>
                  <span className="mt-1 text-xs text-slate-600">{progress}% complete</span>
                </>
              ) : status === "processing" ? (
                <>
                  <Loader2 className="animate-spin text-signal" size={32} />
                  <span className="mt-3 text-sm font-medium">Processing with AI...</span>
                  <span className="mt-1 text-xs text-slate-600">{progress}% complete</span>
                </>
              ) : status === "error" ? (
                <>
                  <AlertCircle className="text-red-500" size={32} />
                  <span className="mt-3 text-sm font-medium text-red-600">Upload failed</span>
                  <span className="mt-1 text-xs text-slate-600">{error}</span>
                </>
              ) : null}
            </div>

            {file && status === "idle" && (
              <div className="mt-4 flex items-center justify-between rounded-md border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-center gap-2">
                  <FileText size={18} className="text-slate-600" />
                  <span className="text-sm font-medium">{file.name}</span>
                  <span className="text-xs text-slate-600">({(file.size / 1024).toFixed(1)} KB)</span>
                </div>
                <button
                  onClick={handleUpload}
                  className="rounded-md bg-signal px-4 py-2 text-sm font-medium text-white hover:bg-signal/90"
                >
                  Upload
                </button>
              </div>
            )}

            {status === "processing" && (
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Upload</span>
                  <span className="text-green-600">✓ Complete</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">OCR Extraction</span>
                  {progress >= 40 ? <span className="text-green-600">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Text Parsing</span>
                  {progress >= 60 ? <span className="text-green-600">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Skill Extraction</span>
                  {progress >= 80 ? <span className="text-green-600">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">Embedding Generation</span>
                  {progress >= 100 ? <span className="text-green-600">✓ Complete</span> : <Loader2 className="animate-spin" size={14} />}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </AppShell>
  );
}
