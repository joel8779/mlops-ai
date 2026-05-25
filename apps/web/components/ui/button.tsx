import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "ghost" | "outline";
  size?: "default" | "sm" | "lg" | "icon";
};

export function Button({ className, variant = "default", size = "default", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-md text-sm font-medium transition disabled:opacity-50",
        variant === "default" && "bg-signal text-white hover:bg-slate-900",
        variant === "ghost" && "bg-transparent text-slate-700 hover:bg-slate-100",
        variant === "outline" && "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
        size === "default" && "h-10 px-4",
        size === "sm" && "h-8 px-3",
        size === "lg" && "h-12 px-5",
        size === "icon" && "h-10 w-10",
        className
      )}
      {...props}
    />
  );
}
