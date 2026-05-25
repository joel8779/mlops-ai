import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { Star, Target, Zap } from "lucide-react";

interface AIBadgeProps {
  score: number;
  label?: string;
  size?: "sm" | "md" | "lg";
  variant?: "score" | "relevance" | "match";
}

export function AIBadge({ score, label, size = "md", variant = "score" }: AIBadgeProps) {
  const sizes = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  const variants = {
    score: {
      bg: "bg-accent/10",
      border: "border-accent/20",
      text: "text-accent",
      icon: Star,
    },
    relevance: {
      bg: "bg-success/10",
      border: "border-success/20",
      text: "text-success",
      icon: Target,
    },
    match: {
      bg: "bg-accent/10",
      border: "border-accent/20",
      text: "text-accent",
      icon: Zap,
    },
  };

  const config = variants[variant];
  const Icon = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        "inline-flex items-center gap-1.5 rounded-lg border font-medium",
        config.bg,
        config.border,
        config.text,
        sizes[size]
      )}
    >
      <Icon className="h-3 w-3 fill-current" />
      <span>{Math.round(score)}%</span>
      {label && <span className="opacity-70">{label}</span>}
    </motion.div>
  );
}
