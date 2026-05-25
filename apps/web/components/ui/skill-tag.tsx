import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SkillTagProps {
  skill: string;
  variant?: "default" | "highlighted" | "muted";
  size?: "sm" | "md" | "lg";
  onClick?: () => void;
}

export function SkillTag({ skill, variant = "default", size = "md", onClick }: SkillTagProps) {
  const sizes = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  const variants = {
    default: "bg-background-card border border-background-border text-foreground-muted hover:border-accent/50",
    highlighted: "bg-accent/10 border border-accent/20 text-accent",
    muted: "bg-background-elevated border border-background-border text-foreground-subtle",
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={onClick ? { scale: 1.05 } : undefined}
      whileTap={onClick ? { scale: 0.95 } : undefined}
      onClick={onClick}
      className={cn(
        "inline-flex items-center rounded-lg transition-colors cursor-default",
        sizes[size],
        variants[variant],
        onClick && "cursor-pointer"
      )}
    >
      {skill}
    </motion.div>
  );
}
