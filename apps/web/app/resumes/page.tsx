import { UploadCloud } from "lucide-react";

export default function ResumeUploadPage() {
  return (
    <main className="mx-auto min-h-screen max-w-4xl px-6 py-8">
      <div className="mb-6">
        <a href="/" className="text-sm font-medium text-signal">
          Dashboard
        </a>
        <h1 className="mt-2 text-2xl font-semibold">Resume Upload</h1>
      </div>

      <form className="rounded-md border border-slate-200 bg-white p-6">
        <label
          htmlFor="resume"
          className="flex min-h-64 cursor-pointer flex-col items-center justify-center rounded-md border border-dashed border-slate-300 bg-mist px-6 text-center"
        >
          <UploadCloud size={32} className="text-signal" />
          <span className="mt-3 text-sm font-medium">Drop a PDF, DOCX, PNG, or JPG resume</span>
          <span className="mt-1 text-xs text-slate-600">Files are parsed asynchronously after upload.</span>
          <input id="resume" name="resume" type="file" className="sr-only" />
        </label>
      </form>
    </main>
  );
}
