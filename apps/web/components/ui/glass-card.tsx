import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  hover?: boolean;
}

export function GlassCard({ 
  children, 
  className, 
  hover = true,
  ...props 
}: GlassCardProps) {
  return (
    <motion.div
      whileHover={hover ? { scale: 1.01 } : undefined}
      transition={{ duration: 0.2 }}
      className={cn(
        "rounded-xl bg-background-card border border-background-border",
        hover && "hover:border-accent/50 transition-colors",
        className
      )}
      {...props}
    >
      {children}
    </motion.div>
  );
}
