# Frontend Application Flow

## Overview

This document describes the current application flow issues and the reconstruction plan for the Resume AI frontend to transform it into a coherent, production-grade AI SaaS application.

## Current Problems

### 1. Landing Page Flashing
**Issue:** Landing page appears briefly then disappears for authenticated users.

**Root Cause:** `apps/web/app/page.tsx` uses client-side `useEffect` to redirect authenticated users to `/dashboard`. This causes:
- Landing page to render
- Auth check to complete
- Redirect to trigger
- Landing page to disappear

**Current Code:**
```tsx
"use client";

export default function HomePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (!authLoading && user && isClient) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router, isClient]);

  if (authLoading || !isClient) {
    return <div>Loading...</div>;
  }

  return <LandingPage />;
}
```

### 2. No Server-Side Route Protection
**Issue:** No middleware for protected routes.

**Current State:** All route protection is client-side via `useEffect` in individual pages.

**Problems:**
- Protected routes flash before redirecting
- No server-side auth check
- SEO and performance impact
- Inconsistent protection across pages

### 3. Dashboard Placeholder Data
**Issue:** Dashboard mixes real API data with hardcoded placeholder data.

**Current Code:**
```tsx
// Real data from API
const stats = [
  { label: "Candidates", value: analytics?.total_candidates?.toString() || "0", ... },
  { label: "Active jobs", value: analytics?.total_jobs?.toString() || "0", ... },
];

// Hardcoded placeholder data
const recentActivities = [
  { action: "New candidate applied", time: "2 min ago", type: "candidate" },
  { action: "Interview scheduled", time: "15 min ago", type: "interview" },
  { action: "AI score updated", time: "1 hour ago", type: "ai" },
  { action: "Job posting created", time: "3 hours ago", type: "job" },
];

const aiRecommendations = [
  { title: "Schedule follow-up with John Doe", priority: "high" },
  { title: "Review top 3 candidates for Senior Engineer", priority: "medium" },
  { title: "Update job requirements for ML Engineer", priority: "low" },
];
```

### 4. Inconsistent Auth Guards
**Issue:** Each authenticated page has its own client-side auth guard.

**Example from dashboard:**
```tsx
useEffect(() => {
  if (!authLoading && !user) {
    router.push("/sign-in");
  }
}, [authLoading, user, router]);
```

**Problem:** Duplicated logic, inconsistent behavior, flashing pages.

### 5. API Layer Issues
**Issue:** API layer is well-structured but not consistently used.

**Current State:**
- Centralized `apiFetch` function in `lib/api.ts`
- Token refresh logic implemented
- All API endpoints defined
- BUT: Some pages may have hardcoded data mixed with API calls

## Expected User Flow

### Unauthenticated User
```
/ → Landing Page (persistent, no redirect)
/login → Login Page
/signup → Signup Page
```

### Authenticated User
```
/ → Redirect to /dashboard
/dashboard → Recruiter Dashboard
/candidates → Candidate Management
/jobs → Job Management
/search → Semantic Search
/copilot → AI Copilot
/analytics → Analytics
```

### Auth Flow
1. User visits `/`
2. If authenticated → redirect to `/dashboard`
3. If not authenticated → show landing page
4. User clicks "Sign In" → `/sign-in`
5. User enters credentials → API call to `/auth/login`
6. On success → store tokens, redirect to `/dashboard`
7. User clicks "Sign Out" → clear tokens, redirect to `/sign-in`

## Reconstruction Plan

### STEP 1: Implement Middleware for Route Protection

**Create `apps/web/middleware.ts`:**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const publicRoutes = ['/', '/sign-in', '/sign-up', '/landing'];

export function middleware(request: NextRequest) {
  const token = request.cookies.get('access_token');
  const { pathname } = request.nextUrl;

  // Check if route is public
  const isPublicRoute = publicRoutes.some(route => pathname === route || pathname.startsWith(route));

  // If no token and trying to access protected route
  if (!token && !isPublicRoute) {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }

  // If has token and trying to access public route (except sign-in/sign-up)
  if (token && (pathname === '/' || pathname === '/landing')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
```

### STEP 2: Fix Root Page Redirect Logic

**Update `apps/web/app/page.tsx`:**
```tsx
"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import LandingPage from "./landing/page";

export default function HomePage() {
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  useEffect(() => {
    // Only redirect if user is authenticated
    // Middleware handles the actual redirect
    // This is just for client-side navigation after login
    if (!authLoading && user) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router]);

  // Don't show loading state - let middleware handle it
  // This prevents the landing page flash
  return <LandingPage />;
}
```

### STEP 3: Remove Client-Side Auth Guards from Protected Pages

**Remove from all authenticated pages:**
```tsx
// DELETE this pattern from dashboard, candidates, jobs, etc.
useEffect(() => {
  if (!authLoading && !user) {
    router.push("/sign-in");
  }
}, [authLoading, user, router]);
```

**Middleware will handle protection server-side.**

### STEP 4: Remove Placeholder Data from Dashboard

**Replace hardcoded data with API calls:**

**Current (placeholder):**
```tsx
const recentActivities = [
  { action: "New candidate applied", time: "2 min ago", type: "candidate" },
  { action: "Interview scheduled", time: "15 min ago", type: "interview" },
  { action: "AI score updated", time: "1 hour ago", type: "ai" },
  { action: "Job posting created", time: "3 hours ago", type: "job" },
];
```

**Target (real API):**
```tsx
const [recentActivities, setRecentActivities] = useState([]);

useEffect(() => {
  loadRecentActivities();
}, []);

const loadRecentActivities = async () => {
  try {
    const data = await analyticsApi.recentActivities();
    setRecentActivities(data);
  } catch (error) {
    console.error("Failed to load recent activities:", error);
  }
};
```

### STEP 5: Audit All Pages for Placeholder Data

**Pages to audit:**
- `app/dashboard/page.tsx` - Remove recentActivities, aiRecommendations placeholders
- `app/candidates/page.tsx` - Verify real API usage
- `app/jobs/page.tsx` - Verify real API usage
- `app/analytics/page.tsx` - Verify real API usage
- `app/search/page.tsx` - Verify real API usage
- `app/copilot/page.tsx` - Verify real API usage

### STEP 6: Implement Proper Auth Flow

**Sign-in page:**
```tsx
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setError("");
  setLoading(true);

  try {
    await login(email, password);
    // Redirect to dashboard
    router.push("/dashboard");
  } catch (err: any) {
    setError(err.message || "Failed to sign in");
  } finally {
    setLoading(false);
  }
};
```

**Sign-out:**
```tsx
const logout = () => {
  authApi.logout();
  // authApi.logout handles token clearing and redirect
};
```

### STEP 7: Create Route Groups for Organization

**Structure:**
```
app/
├── (public)/
│   ├── page.tsx (landing)
│   ├── sign-in/
│   └── sign-up/
├── (protected)/
│   ├── layout.tsx (auth shell)
│   ├── dashboard/
│   ├── candidates/
│   ├── jobs/
│   ├── search/
│   ├── copilot/
│   └── analytics/
└── layout.tsx (root)
```

**Benefits:**
- Clear separation of public vs protected routes
- Shared layout for protected routes
- Easier to apply auth guards

### STEP 8: Implement Loading States

**For protected routes:**
```tsx
export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!user) {
    // Middleware should have redirected, but fallback
    return <div>Redirecting...</div>;
  }

  return <>{children}</>;
}
```

## API Integration Audit

### Current API Layer Status

**Strengths:**
- ✅ Centralized `apiFetch` function
- ✅ Token management (localStorage)
- ✅ Token refresh logic
- ✅ All API endpoints defined
- ✅ Auth headers automatically added
- ✅ 401 handling with token refresh

**Weaknesses:**
- ❌ Not consistently used across all pages
- ❌ Some hardcoded data mixed with API calls
- ❌ No error boundary for API failures
- ❌ No loading state standardization

### API Endpoints

**Auth:**
- `/auth/register` - User registration
- `/auth/login` - User login
- `/auth/me` - Get current user
- `/auth/refresh` - Refresh access token

**Jobs:**
- `/jobs` - List jobs
- `/jobs/{id}` - Get job details
- `/jobs` - Create job

**Resumes:**
- `/resumes/upload` - Upload resume
- `/resumes/{id}` - Get resume details

**Candidates:**
- `/candidates` - List candidates
- `/candidates/{id}` - Get candidate details

**Search:**
- `/search/candidates` - Semantic search

**AI:**
- `/ai/summary` - Generate AI summary
- `/ai/interview-questions` - Generate interview questions
- `/ai/compare` - Compare candidates
- `/ai/copilot` - AI copilot chat

**Matching:**
- `/matching/rank` - Rank candidates for job

**ATS:**
- `/ats/resumes/{id}/score` - Score resume

**Analytics:**
- `/analytics/executive` - Executive analytics

## Implementation Priority

### HIGH PRIORITY (Critical Flow)
1. Implement middleware for route protection
2. Fix root page redirect logic
3. Remove client-side auth guards from protected pages
4. Fix sign-in/sign-up redirect flow

### MEDIUM PRIORITY (Data Integrity)
5. Remove placeholder data from dashboard
6. Audit all pages for placeholder data
7. Ensure all pages use real API calls
8. Implement proper loading states

### LOW PRIORITY (Organization)
9. Create route groups for organization
10. Implement error boundaries
11. Standardize error handling
12. Add loading skeletons

## Validation Checklist

### Landing Page
- [ ] Landing page persists for unauthenticated users
- [ ] No flash before redirect for authenticated users
- [ ] No hydration warnings
- [ ] Smooth transition to dashboard after login

### Auth Flow
- [ ] Sign-in works correctly
- [ ] Sign-up works correctly
- [ ] Redirect to dashboard after successful auth
- [ ] Sign-out clears tokens and redirects to sign-in
- [ ] Token refresh works on 401
- [ ] Session persists on refresh

### Protected Routes
- [ ] Dashboard accessible only when authenticated
- [ ] Candidates accessible only when authenticated
- [ ] Jobs accessible only when authenticated
- [ ] Search accessible only when authenticated
- [ ] Copilot accessible only when authenticated
- [ ] Analytics accessible only when authenticated

### Data Integrity
- [ ] Dashboard shows real data from API
- [ ] No placeholder data in dashboard
- [ ] All pages use real API calls
- [ ] Loading states work correctly
- [ ] Error states work correctly

### UX Stability
- [ ] No page flashing
- [ ] No redirect loops
- [ ] Consistent navigation
- [ ] Smooth transitions
- [ ] Production-grade feel

## Success Criteria

The frontend should:
- ✅ Behave like a real AI recruiting SaaS
- ✅ Have stable application flow
- ✅ Use real backend data everywhere
- ✅ Have proper auth flow
- ✅ Have proper route protection
- ✅ Have no placeholder data
- ✅ Feel production-ready

NOT:
- ❌ Template project
- ❌ Placeholder dashboard
- ❌ Disconnected frontend
- ❌ Broken route demo
