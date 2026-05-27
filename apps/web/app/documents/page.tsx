"use client";

import Link from "next/link";
import { DragEvent, useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, CheckCircle, Cpu, Database, FileText, Loader2, RefreshCcw, ScanLine, Search, Trash2, UploadCloud, Users, Zap } from "lucide-react";
import AppShell from "@/components/app-shell";
import { API_BASE_URL, getAccessToken, resumesApi } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Resume = {
  id: string;
  candidate_id?: string | null;
  original_filename: string;
  content_type: string;
  status: string;
  parser_version?: string | null;
  metadata_json?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
};

type UploadState = "idle" | "ready" | "uploading" | "processing" | "success" | "error";

const terminalStatuses = new Set(["parsed", "embedded", "failed"]);

function uploadResumeWithProgress(
  file: File,
  candidate: { candidate_name: string; email: string; phone: string; years_experience: string; location: string },
  onProgress: (progress: number) => void
): Promise<Resume> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("candidate_name", candidate.candidate_name);
    if (candidate.email) formData.append("email", candidate.email);
    if (candidate.phone) formData.append("phone", candidate.phone);
    if (candidate.years_experience) formData.append("years_experience", candidate.years_experience);
    if (candidate.location) formData.append("location", candidate.location);
    formData.append("file", file);
    xhr.open("POST", `${API_BASE_URL}/resumes/upload`);
    const token = getAccessToken();
    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }
    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        onProgress(Math.round((event.loaded / event.total) * 100));
      }
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
        return;
      }
      reject(new Error(xhr.responseText || `Upload failed with ${xhr.status}`));
    };
    xhr.onerror = () => reject(new Error("Upload failed. Check API connectivity and try again."));
    xhr.send(formData);
  });
}

export default function DocumentsPage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [documents, setDocuments] = useState<Resume[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<UploadState>("idle");
  const [progress, setProgress] = useState(0);
  const [currentResume, setCurrentResume] = useState<Resume | null>(null);
  const [candidateForm, setCandidateForm] = useState({
    candidate_name: "",
    email: "",
    phone: "",
    years_experience: "",
    location: "",
  });
  const [loadingList, setLoadingList] = useState(true);
  const [error, setError] = useState("");

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      router.replace("/login");
    }
  }, [user, authLoading, router]);

  const loadDocuments = useCallback(async () => {
    if (!user) return;
    setLoadingList(true);
    try {
      setDocuments((await resumesApi.list()) as Resume[]);
    } catch (err: any) {
      setError(err.message || "Unable to load uploaded documents");
    } finally {
      setLoadingList(false);
    }
  }, [user]);

  useEffect(() => {
    if (user) {
      loadDocuments();
    }
  }, [user, loadDocuments]);

  const selectFile = (selectedFile: File) => {
    const validTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ];
    const validExtension = /\.(pdf|docx)$/i.test(selectedFile.name);
    if (!validTypes.includes(selectedFile.type) && !validExtension) {
      setError("Upload a PDF or DOCX resume.");
      setState("error");
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setError("File size must be 10MB or less.");
      setState("error");
      return;
    }
    setFile(selectedFile);
    setCurrentResume(null);
    setError("");
    setProgress(0);
    setState("ready");
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      selectFile(droppedFile);
    }
  };

  const pollResume = async (resumeId: string) => {
    let latest = (await resumesApi.get(resumeId)) as Resume;
    setCurrentResume(latest);
    while (!terminalStatuses.has(latest.status)) {
      await new Promise((resolve) => setTimeout(resolve, 1500));
      latest = (await resumesApi.get(resumeId)) as Resume;
      setCurrentResume(latest);
    }
    setState(latest.status === "failed" ? "error" : "success");
    if (latest.status === "failed") {
      setError("Document processing failed. Review backend worker logs for parser or OCR details.");
    }
    await loadDocuments();
  };

  const upload = async () => {
    if (!file) return;
    if (!candidateForm.candidate_name.trim()) {
      setError("Enter the candidate name before uploading.");
      setState("error");
      return;
    }
    setState("uploading");
    setError("");
    try {
      const uploaded = await uploadResumeWithProgress(file, candidateForm, setProgress);
      setCurrentResume(uploaded);
      setState("processing");
      await pollResume(uploaded.id);
    } catch (err: any) {
      setError(err.message || "Upload failed");
      setState("error");
    }
  };

  const deleteDocument = async (resumeId: string) => {
    setError("");
    try {
      await resumesApi.delete(resumeId);
      await loadDocuments();
    } catch (err: any) {
      setError(err.message || "Unable to delete document");
    }
  };

  return (
    <AppShell>
      <div className="space-y-8">
        <div className="ops-panel-strong rounded-xl p-5 sm:p-6">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs uppercase tracking-[0.28em] text-accent">Candidate intelligence ingestion</div>
            <h1 className="mt-2 text-2xl font-semibold">Documents</h1>
            <p className="text-sm text-foreground-muted">Upload resumes into OCR, parsing, embedding, indexing, and candidate creation workflows.</p>
          </div>
          <button
            onClick={loadDocuments}
            className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm"
          >
            <RefreshCcw className="h-4 w-4" />
            Refresh
          </button>
          </div>
        </div>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_360px]">
          <div className="ops-panel rounded-xl p-6">
            <div
              onDrop={handleDrop}
              onDragOver={(event) => event.preventDefault()}
              className="scanline rounded-xl border-2 border-dashed border-accent/25 bg-background/60 p-10 text-center transition-colors hover:border-accent/60"
            >
              <input
                id="document-upload"
                type="file"
                accept=".pdf,.docx"
                className="hidden"
                onChange={(event) => {
                  const selectedFile = event.target.files?.[0];
                  if (selectedFile) selectFile(selectedFile);
                }}
              />
              <label htmlFor="document-upload" className="block cursor-pointer">
                <UploadCloud className="mx-auto h-12 w-12 text-accent" />
                <div className="mt-4 font-medium">Drop candidate documents here</div>
                <div className="mt-1 text-sm text-foreground-muted">PDF or DOCX resumes, up to 10MB</div>
              </label>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <input
                className="ops-input rounded-md px-3 py-3 text-sm sm:col-span-2"
                value={candidateForm.candidate_name}
                onChange={(event) => setCandidateForm((current) => ({ ...current, candidate_name: event.target.value }))}
                placeholder="Candidate name"
              />
              <input
                className="ops-input rounded-md px-3 py-3 text-sm"
                value={candidateForm.email}
                onChange={(event) => setCandidateForm((current) => ({ ...current, email: event.target.value }))}
                placeholder="Email"
              />
              <input
                className="ops-input rounded-md px-3 py-3 text-sm"
                value={candidateForm.phone}
                onChange={(event) => setCandidateForm((current) => ({ ...current, phone: event.target.value }))}
                placeholder="Phone"
              />
              <input
                className="ops-input rounded-md px-3 py-3 text-sm"
                value={candidateForm.years_experience}
                onChange={(event) => setCandidateForm((current) => ({ ...current, years_experience: event.target.value }))}
                placeholder="Years experience"
                type="number"
                min="0"
              />
              <input
                className="ops-input rounded-md px-3 py-3 text-sm"
                value={candidateForm.location}
                onChange={(event) => setCandidateForm((current) => ({ ...current, location: event.target.value }))}
                placeholder="Location"
              />
            </div>

            {file && (
              <div className="mt-5 rounded-lg border border-white/10 bg-white/[0.03] p-4">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-3">
                    <FileText className="h-8 w-8 flex-shrink-0 text-accent" />
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{file.name}</div>
                      <div className="text-xs text-foreground-muted">{(file.size / 1024 / 1024).toFixed(2)} MB</div>
                    </div>
                  </div>
                  <button
                    onClick={upload}
                    disabled={state === "uploading" || state === "processing"}
                    className="ops-button inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold disabled:opacity-60"
                  >
                    {state === "uploading" || state === "processing" ? <Loader2 className="h-4 w-4 animate-spin" /> : <UploadCloud className="h-4 w-4" />}
                    Upload
                  </button>
                </div>
              </div>
            )}

            {(state === "uploading" || state === "processing" || state === "success" || state === "error") && (
              <div className="mt-5 rounded-lg border border-white/10 bg-white/[0.03] p-4">
                <div className="flex items-start gap-3">
                  {state === "success" ? (
                    <CheckCircle className="h-5 w-5 text-success" />
                  ) : state === "error" ? (
                    <AlertCircle className="h-5 w-5 text-error" />
                  ) : (
                    <Loader2 className="h-5 w-5 animate-spin text-foreground-muted" />
                  )}
                  <div className="flex-1">
                    <div className="text-sm font-medium">
                      {state === "uploading" && "Uploading encrypted payload to backend"}
                      {state === "processing" && `Ingestion pipeline: ${currentResume?.status || "queued"}`}
                      {state === "success" && "Candidate intelligence indexed"}
                      {state === "error" && "Ingestion workflow needs attention"}
                    </div>
                    {state === "uploading" && (
                      <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                        <div className="h-full bg-accent" style={{ width: `${progress}%` }} />
                      </div>
                    )}
                    {state === "processing" && (
                      <p className="mt-1 text-sm text-foreground-muted">Waiting for OCR, parser, embedding generation, indexing, and candidate creation.</p>
                    )}
                    {error && <p className="mt-2 text-sm text-error">{error}</p>}
                    {currentResume?.candidate_id && (
                      <div className="mt-4 flex flex-wrap gap-3">
                        <Link href={`/candidates/${currentResume.candidate_id}`} className="ops-button inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold">
                          <Users className="h-4 w-4" />
                          View candidate
                        </Link>
                        <Link href="/search" className="ops-button-secondary inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm">
                          <Search className="h-4 w-4" />
                          Semantic search
                        </Link>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <aside className="ops-panel rounded-xl p-5">
            <h2 className="text-base font-semibold">Orchestration pipeline</h2>
            <div className="mt-4 space-y-3 text-sm">
              {[
                { status: "upload", icon: UploadCloud },
                { status: "OCR scan", icon: ScanLine },
                { status: "profile parse", icon: Cpu },
                { status: "embedding", icon: Zap },
                { status: "index ready", icon: Database },
              ].map((item) => {
                const Icon = item.icon;
                return (
                <div key={item.status} className="flex items-center justify-between rounded-lg border border-white/10 bg-white/[0.03] px-3 py-3">
                  <span className="flex items-center gap-2 capitalize"><Icon className="h-4 w-4 text-accent" />{item.status}</span>
                  <span className="text-xs text-foreground-muted">backend</span>
                </div>
              )})}
            </div>
          </aside>
        </section>

        <section className="ops-panel rounded-xl p-6">
          <h2 className="text-base font-semibold">Uploaded documents</h2>
          {loadingList ? (
            <div className="mt-6 flex items-center gap-2 text-sm text-foreground-muted">
              <Loader2 className="h-4 w-4 animate-spin" />
              Loading documents
            </div>
          ) : documents.length === 0 ? (
            <div className="mt-6 rounded-lg border border-white/10 bg-white/[0.03] p-6 text-sm text-foreground-muted">
              No documents uploaded yet. Upload a resume to create candidates and unlock search, ATS scores, summaries, and matches.
            </div>
          ) : (
            <div className="mt-4 divide-y divide-white/10">
              {documents.map((document) => (
                <div key={document.id} className="flex flex-col gap-3 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="truncate text-sm font-medium">{document.original_filename}</div>
                    <div className="mt-1 text-xs text-foreground-muted">
                      {document.status} {document.created_at ? `- ${new Date(document.created_at).toLocaleString()}` : ""}
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {document.candidate_id && (
                      <Link href={`/candidates/${document.candidate_id}`} className="rounded-md border border-white/10 px-3 py-2 text-sm hover:bg-white/[0.04]">
                        Candidate
                      </Link>
                    )}
                    <button onClick={() => pollResume(document.id)} className="rounded-md border border-white/10 px-3 py-2 text-sm hover:bg-white/[0.04]">
                      Check status
                    </button>
                    <button
                      title="Delete document"
                      onClick={() => deleteDocument(document.id)}
                      className="rounded-md border border-error/30 px-3 py-2 text-sm text-error hover:bg-error/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </AppShell>
  );
}
