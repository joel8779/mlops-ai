import type { Metadata } from "next";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ScrollRestoration } from "@/components/scroll-restoration";

export const metadata: Metadata = {
  title: "Resume Intelligence",
  description: "Operational intelligence infrastructure for modern recruiting teams"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
        <ScrollRestoration />
      </body>
    </html>
  );
}
