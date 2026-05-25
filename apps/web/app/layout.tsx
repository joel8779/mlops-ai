import type { Metadata } from "next";
import { Suspense } from "react";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ScrollRestoration } from "@/components/scroll-restoration";

export const metadata: Metadata = {
  title: "Neural Ops",
  description: "Cyberpunk recruiting command center for AI hiring operations"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
        <Suspense fallback={null}>
          <ScrollRestoration />
        </Suspense>
      </body>
    </html>
  );
}
