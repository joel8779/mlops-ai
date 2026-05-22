import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resume Intelligence",
  description: "AI hiring infrastructure for recruiters and talent teams"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
