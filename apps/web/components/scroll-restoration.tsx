"use client";

import { useEffect } from "react";
import { usePathname, useSearchParams } from "next/navigation";

export function ScrollRestoration() {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  useEffect(() => {
    // Restore scroll position when pathname or search params change
    const scrollY = sessionStorage.getItem(`scroll-${pathname}`);
    if (scrollY) {
      window.scrollTo(0, parseInt(scrollY, 10));
    }
  }, [pathname, searchParams]);

  useEffect(() => {
    // Save scroll position before navigation
    const handleBeforeUnload = () => {
      sessionStorage.setItem(`scroll-${pathname}`, window.scrollY.toString());
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => {
      window.removeEventListener("beforeunload", handleBeforeUnload);
    };
  }, [pathname]);

  return null;
}
