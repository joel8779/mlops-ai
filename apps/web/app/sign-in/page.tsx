import { Button } from "@/components/ui/button";

export default function SignInPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
      <form className="w-full max-w-sm rounded-md border border-slate-200 bg-white p-6">
        <h1 className="text-xl font-semibold">Sign in</h1>
        <input className="mt-4 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none" placeholder="Email" />
        <input className="mt-3 w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none" placeholder="Password" type="password" />
        <Button className="mt-4 w-full">Continue</Button>
      </form>
    </main>
  );
}
