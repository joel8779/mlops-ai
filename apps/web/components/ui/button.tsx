import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-md bg-signal px-4 text-sm font-medium text-white transition hover:bg-slate-900 disabled:opacity-50",
        className
      )}
      {...props}
    />
  );
}
