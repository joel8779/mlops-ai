import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface FuturisticTableProps {
  headers: string[];
  data: React.ReactNode[][];
  className?: string;
}

export function FuturisticTable({ headers, data, className }: FuturisticTableProps) {
  return (
    <div className={cn("overflow-hidden rounded-xl border border-background-border bg-background-card", className)}>
      <table className="w-full">
        <thead>
          <tr className="border-b border-background-border bg-background-elevated">
            {headers.map((header, i) => (
              <th key={i} className="px-6 py-4 text-left text-sm font-semibold text-foreground-muted">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <motion.div
              key={rowIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: rowIndex * 0.05 }}
            >
              <tr className="border-b border-background-border last:border-0 hover:bg-background-elevated transition-colors">
                {row.map((cell, cellIndex) => (
                  <td key={cellIndex} className="px-6 py-4 text-sm text-foreground">
                    {cell}
                  </td>
                ))}
              </tr>
            </motion.div>
          ))}
        </tbody>
      </table>
    </div>
  );
}
