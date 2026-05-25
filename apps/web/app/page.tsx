"use client";

import LandingPage from "./landing/page";

export default function HomePage() {
  // Middleware handles auth protection and redirects
  // This page just renders the landing page for unauthenticated users
  // Authenticated users are redirected to /dashboard by middleware
  return <LandingPage />;
}
