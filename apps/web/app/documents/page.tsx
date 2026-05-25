"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, CheckCircle, AlertCircle, Loader2 } from "lucide-react";
import { resumesApi } from "@/lib/api";
import AppShell from "@/components/app-shell";

type UploadStatus = "idle" | "uploading" | "complete" | "error";

export default function DocumentsPage() {
  const router = useRouter();
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [error, setError] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);

  const handleFileSelect = useCallback((selectedFile: File) => {
    // Validate file type
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
    ];
    
    if (!validTypes.includes(selectedFile.type)) {
      setError("Please upload a PDF or DOCX file");
      return;
    }

    // Validate file size (max 10MB)
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size must be less than 10MB");
      return;
    }

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

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleUpload = async () => {
    if (!file) return;

    setStatus("uploading");
    setError("");

    try {
      const result = await resumesApi.upload(file);
      setUploadResult(result);
      setStatus("complete");
    } catch (err: any) {
      setStatus("error");
      setError(err.message || "Failed to upload resume");
    }
  };

  const handleReset = () => {
    setFile(null);
    setUploadResult(null);
    setStatus("idle");
    setError("");
  };

  return (
    <AppShell>
      <div>
        <div className="mb-8">
          <h1 className="text-xl font-semibold mb-2">Documents</h1>
          <p className="text-sm text-foreground-muted">
            Upload resumes and documents to parse candidates
          </p>
        </div>

        {status === "idle" && (
          <div className="max-w-2xl">
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-background-border rounded-lg p-12 text-center hover:border-foreground/50 transition-colors cursor-pointer"
            >
              <input
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(e) => {
                  const selectedFile = e.target.files?.[0];
                  if (selectedFile) handleFileSelect(selectedFile);
                }}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <div className="flex flex-col items-center">
                  <UploadCloud className="h-12 w-12 text-foreground-muted mb-4" />
                  <p className="text-base font-medium mb-2">
                    Drop your resume here or click to browse
                  </p>
                  <p className="text-sm text-foreground-muted mb-4">
                    PDF or DOCX, up to 10MB
                  </p>
                  <button className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors">
                    Select File
                  </button>
                </div>
              </label>
            </div>

            {error && (
              <div className="mt-4 flex items-center gap-2 text-sm text-error">
                <AlertCircle className="h-4 w-4" />
                {error}
              </div>
            )}

            {file && (
              <div className="mt-6 p-4 rounded-lg bg-background-card border border-background-border">
                <div className="flex items-center gap-3">
                  <FileText className="h-8 w-8 text-foreground-muted" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{file.name}</p>
                    <p className="text-xs text-foreground-muted">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    onClick={handleUpload}
                    className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors"
                  >
                    Upload
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {status === "uploading" && (
          <div className="max-w-2xl">
            <div className="p-6 rounded-lg bg-background-card border border-background-border">
              <div className="flex items-center gap-4">
                <Loader2 className="h-8 w-8 text-foreground-muted animate-spin" />
                <div className="flex-1">
                  <p className="text-sm font-medium">Uploading document...</p>
                  <p className="text-xs text-foreground-muted mt-1">
                    {file?.name}
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {status === "complete" && uploadResult && (
          <div className="max-w-2xl">
            <div className="p-6 rounded-lg bg-background-card border border-background-border">
              <div className="flex items-center gap-4 mb-6">
                <CheckCircle className="h-8 w-8 text-success" />
                <div>
                  <p className="text-sm font-medium">Upload successful</p>
                  <p className="text-xs text-foreground-muted mt-1">
                    Document processed and candidate created
                  </p>
                </div>
              </div>

              {uploadResult.candidate_id && (
                <div className="space-y-4">
                  <div className="p-4 rounded-md bg-background-elevated">
                    <p className="text-xs text-foreground-muted mb-1">Candidate ID</p>
                    <p className="text-sm font-mono">{uploadResult.candidate_id}</p>
                  </div>

                  <div className="flex gap-3">
                    <button
                      onClick={() => router.push(`/candidates/${uploadResult.candidate_id}`)}
                      className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors"
                    >
                      View Candidate
                    </button>
                    <button
                      onClick={handleReset}
                      className="inline-flex items-center gap-2 rounded-lg bg-background-elevated border border-background-border px-4 py-2 text-sm font-medium hover:bg-background-elevated/80 transition-colors"
                    >
                      Upload Another
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {status === "error" && (
          <div className="max-w-2xl">
            <div className="p-6 rounded-lg bg-background-card border border-background-border">
              <div className="flex items-center gap-4 mb-6">
                <AlertCircle className="h-8 w-8 text-error" />
                <div>
                  <p className="text-sm font-medium">Upload failed</p>
                  <p className="text-xs text-foreground-muted mt-1">{error}</p>
                </div>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={handleReset}
                  className="inline-flex items-center gap-2 rounded-lg bg-foreground text-background px-4 py-2 text-sm font-medium hover:bg-foreground/90 transition-colors"
                >
                  Try Again
                </button>
                <button
                  onClick={() => router.push("/dashboard")}
                  className="inline-flex items-center gap-2 rounded-lg bg-background-elevated border border-background-border px-4 py-2 text-sm font-medium hover:bg-background-elevated/80 transition-colors"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
