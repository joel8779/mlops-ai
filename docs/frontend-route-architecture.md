# Frontend Route Architecture

## Overview

The Resume AI frontend uses Next.js 15 with the App Router for routing. The application has a clear separation between public pages (landing, auth) and authenticated pages (dashboard, candidates, etc.).

## Route Structure

### Public Routes

```
/                          → Landing page (redirects to /dashboard if authenticated)
/sign-in                   → Sign in page
/sign-up                   → Sign up page
/landing                   → Landing page component
```

### Authenticated Routes

```
/dashboard                 → Main dashboard
/candidates                → Candidates list
/candidates/[id]           → Candidate detail page
/copilot                   → AI copilot chat interface
/search                    → Semantic search
/analytics                 → Analytics dashboard (OLD - needs migration)
/jobs                      → Job management (OLD - needs migration)
/resumes                   → Resume upload (OLD - needs migration)
```

## Page Architecture

### Root Page (`/`)

**Purpose:** Entry point that routes based on authentication state

**Component:** `apps/web/app/page.tsx`

**Logic:**
- If user is authenticated → redirect to `/dashboard`
- If user is not authenticated → show `LandingPage`

**Code:**
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
    if (!authLoading && user) {
      router.push("/dashboard");
    }
  }, [authLoading, user, router]);

  if (authLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return <LandingPage />;
}
```

**Issues:**
- Uses `useEffect` for redirect (can cause hydration mismatch)
- Shows loading state during auth check

**Recommendation:** Consider server-side redirect or middleware

---

### Landing Page (`/landing`)

**Purpose:** Public-facing marketing page

**Component:** `apps/web/app/landing/page.tsx`

**Status:** ✅ Migrated to monochromatic theme

**Sections:**
- Hero with CTA
- AI Recruiting features
- Semantic Search showcase
- ATS Scoring showcase
- AI Copilot showcase
- Document Intelligence showcase
- Analytics showcase
- Feature grid
- Testimonials
- CTA section
- Footer

**Animation System:**
- Uses centralized variants from `lib/animations.ts`
- No `whileInView` animations (prevents hydration issues)
- Subtle fade-in animations (0.3s duration)

---

### Dashboard (`/dashboard`)

**Purpose:** Main application dashboard

**Component:** `apps/web/app/dashboard/page.tsx`

**Status:** ✅ Migrated to monochromatic theme

**Layout:**
- Inline sidebar (collapsible on mobile)
- Main content area with stats, charts, and activity feed

**Features:**
- Stats grid (candidates, jobs, interviews, time to hire)
- Hiring pipeline visualization
- Semantic search quick action
- AI recommendations
- Recent activity feed

**Animation System:**
- Uses inline animations (not centralized yet)
- Staggered delays for stats and lists
- Sidebar slide animation

**Issues:**
- Not using centralized animation variants
- Excessive staggered delays (0.3, 0.4, 0.5, 0.6, 0.7s)

---

### Candidates (`/candidates`)

**Purpose:** Candidate management and listing

**Component:** `apps/web/app/candidates/page.tsx`

**Status:** ✅ Migrated to monochromatic theme

**Layout:**
- Inline sidebar (collapsible on mobile)
- Main content area with candidate cards

**Features:**
- Candidate cards with AI scores
- Skill tags
- Filter options
- Search functionality

**Animation System:**
- Uses inline animations
- Staggered delays for candidate cards

**Issues:**
- Not using centralized animation variants

---

### Candidate Detail (`/candidates/[id]`)

**Purpose:** Individual candidate profile

**Component:** `apps/web/app/candidates/[id]/page.tsx`

**Status:** ❌ OLD - Uses AppShell, needs migration

**Layout:**
- Uses `AppShell` component (old layout system)
- Slate/white color scheme

**Issues:**
- Uses old AppShell layout
- Slate/white color scheme
- Not monochromatic

**Recommendation:** Migrate to inline sidebar layout with monochromatic theme

---

### AI Copilot (`/copilot`)

**Purpose:** AI-powered recruiting assistant

**Component:** `apps/web/app/copilot/page.tsx`

**Status:** ✅ Migrated to monochromatic theme

**Layout:**
- Inline sidebar (collapsible on mobile)
- Chat interface with message bubbles

**Features:**
- Chat interface with streaming responses
- AI thought indicators
- Quick actions
- Message history

**Animation System:**
- Uses inline animations
- Message fade-in animations
- Typing indicator rotation

**Issues:**
- Not using centralized animation variants

---

### Semantic Search (`/search`)

**Purpose:** Semantic candidate search

**Component:** `apps/web/app/search/page.tsx`

**Status:** ✅ Migrated to monochromatic theme

**Layout:**
- Inline sidebar (collapsible on mobile)
- Filters sidebar
- Search results area

**Features:**
- Natural language search
- Filter options
- Relevance scores
- Result cards

**Animation System:**
- Uses inline animations
- Staggered delays for results

**Issues:**
- Not using centralized animation variants

---

### Analytics (`/analytics`)

**Purpose:** Analytics dashboard

**Component:** `apps/web/app/analytics/page.tsx`

**Status:** ❌ OLD - Uses AppShell, needs migration

**Layout:**
- Uses `AppShell` component (old layout system)
- Slate/white color scheme

**Features:**
- Executive metrics
- Hiring funnel visualization
- Top skills demand
- Ranking quality

**Issues:**
- Uses old AppShell layout
- Slate/white color scheme
- "signal" accent color
- Not monochromatic

**Recommendation:** Migrate to inline sidebar layout with monochromatic theme

---

### Jobs (`/jobs`)

**Purpose:** Job description management

**Component:** `apps/web/app/jobs/page.tsx`

**Status:** ❌ OLD - Uses AppShell, needs migration

**Layout:**
- Uses `AppShell` component (old layout system)
- Slate/white color scheme

**Features:**
- Job listing
- Job creation form
- Skill extraction

**Issues:**
- Uses old AppShell layout
- Slate/white color scheme
- "signal" accent color
- Not monochromatic

**Recommendation:** Migrate to inline sidebar layout with monochromatic theme

---

### Resumes (`/resumes`)

**Purpose:** Resume upload and processing

**Component:** `apps/web/app/resumes/page.tsx`

**Status:** ❌ OLD - Uses AppShell, needs migration

**Layout:**
- Uses `AppShell` component (old layout system)
- Slate/white color scheme

**Features:**
- File upload (drag & drop)
- Processing status
- OCR extraction
- Skill extraction

**Issues:**
- Uses old AppShell layout
- Slate/white color scheme
- "signal" accent color
- Not monochromatic

**Recommendation:** Migrate to inline sidebar layout with monochromatic theme

---

### Sign In (`/sign-in`)

**Purpose:** User authentication

**Component:** `apps/web/app/sign-in/page.tsx`

**Status:** ❌ OLD - Light theme, needs migration

**Layout:**
- Centered card
- Slate-50 background (light theme)

**Issues:**
- Light theme (slate-50 background)
- White card
- No dark mode
- Inconsistent with monochromatic theme

**Recommendation:** Migrate to monochromatic dark theme

---

### Sign Up (`/sign-up`)

**Purpose:** User registration

**Component:** `apps/web/app/sign-up/page.tsx`

**Status:** ❌ OLD - Light theme, needs migration

**Layout:**
- Centered card
- Slate-50 background (light theme)

**Issues:**
- Light theme (slate-50 background)
- White card
- No dark mode
- Inconsistent with monochromatic theme

**Recommendation:** Migrate to monochromatic dark theme

---

## Layout Systems

### Current State: Two Layout Systems Coexist

#### OLD LAYOUT SYSTEM (AppShell)

**Component:** `apps/web/components/app-shell.tsx`

**Characteristics:**
- Fixed sidebar on desktop
- Slate/white color scheme
- "signal" accent color
- Used by: analytics, jobs, resumes, candidates/[id]

**Navigation:**
```tsx
const nav = [
  { href: "/", label: "Dashboard", icon: BarChart3 },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/search", label: "Search", icon: Search },
  { href: "/resumes", label: "Uploads", icon: UploadCloud },
  { href: "/jobs", label: "Jobs", icon: BriefcaseBusiness },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/copilot", label: "Copilot", icon: Bot }
];
```

**Issues:**
- Inconsistent with new design system
- Slate/white color scheme
- "signal" accent color
- Duplicate navigation logic

#### NEW LAYOUT SYSTEM (Inline Sidebar)

**Characteristics:**
- Inline sidebar in each page
- Collapsible on mobile
- Monochromatic dark theme
- "accent" color (#3b82f6)
- Used by: dashboard, candidates, copilot, search

**Navigation Pattern:**
```tsx
<motion.div
  initial={{ x: -300 }}
  animate={{ x: sidebarOpen ? 0 : -300 }}
  className="fixed left-0 top-0 z-50 h-full w-72 bg-background-card border-r border-background-border lg:static lg:translate-x-0"
>
  {/* Sidebar content */}
</motion.div>
```

**Benefits:**
- Consistent with monochromatic theme
- More flexible
- Better mobile experience

### Recommendation: Migrate to Single Layout System

**Target:** Use inline sidebar layout for all pages

**Migration Steps:**
1. Create reusable sidebar component
2. Migrate analytics page
3. Migrate jobs page
4. Migrate resumes page
5. Migrate candidates/[id] page
6. Deprecate AppShell component

---

## Component Architecture

### Shared Components

#### UI Components (`components/ui/`)

- `button.tsx` - Button component
- `card.tsx` - Card component
- `input.tsx` - Input component
- `modal.tsx` - Modal component
- `skeleton.tsx` - Skeleton loading component

#### Custom Components (`components/`)

- `app-shell.tsx` - OLD layout wrapper (to be deprecated)
- `animated-dashboard.tsx` - Unused, to be removed
- `ai-copilot-panel.tsx` - Unused, to be removed
- `analytics-charts.tsx` - Charts for analytics page
- `ranking-visualization.tsx` - Ranking visualization component

#### Theme Components (`components/ui/` - Monochromatic)

- `glass-card.tsx` - Glassmorphism card
- `gradient-button.tsx` - Button with gradient (now monochromatic)
- `ai-badge.tsx` - AI score badge
- `skill-tag.tsx` - Skill tag
- `futuristic-table.tsx` - Table component

---

## Navigation Flow

### Unauthenticated User Flow

```
/ → Landing page
   ↓
   Click "Get Started"
   ↓
/sign-up → Sign up page
   ↓
   After successful registration
   ↓
/dashboard
```

### Authenticated User Flow

```
/ → Redirect to /dashboard
   ↓
/dashboard → Main dashboard
   ↓
   Navigate to:
   - /candidates
   - /search
   - /copilot
   - /analytics (old)
   - /jobs (old)
   - /resumes (old)
```

---

## Route Protection

### Current Implementation

**Auth Context:** `lib/auth-context.ts`

**Protection Pattern:**
```tsx
const { user, loading } = useAuth();

useEffect(() => {
  if (!loading && !user) {
    router.push("/sign-in");
  }
}, [loading, user, router]);
```

**Issues:**
- Client-side only (no server-side protection)
- Can cause hydration mismatch
- Shows loading state

### Recommendation: Middleware Protection

**Implementation:**
```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token');
  const isAuthPage = request.nextUrl.pathname.startsWith('/sign-in') || 
                     request.nextUrl.pathname.startsWith('/sign-up');
  
  if (!token && !isAuthPage && !request.nextUrl.pathname === '/') {
    return NextResponse.redirect(new URL('/sign-in', request.url));
  }
  
  if (token && isAuthPage) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/candidates/:path*', '/copilot/:path*', '/search/:path*']
};
```

---

## Hydration Issues

### Root Page Hydration

**Issue:** `useEffect` redirect can cause hydration mismatch

**Current:**
```tsx
useEffect(() => {
  if (!authLoading && user) {
    router.push("/dashboard");
  }
}, [authLoading, user, router]);
```

**Recommendation:** Use middleware for server-side redirect

### Landing Page Hydration

**Issue:** Previously used `whileInView` which caused hydration issues

**Fix:** Removed `whileInView`, now uses `animate` prop only

**Current:**
```tsx
<motion.div {...fadeInUp}>
  Content
</motion.div>
```

---

## Performance Considerations

### Code Splitting

**Current:** All pages are client components

**Recommendation:** Consider server components for static content

**Example:**
```tsx
// landing/page.tsx - Keep as client for animations
// candidates/[id]/page.tsx - Could be server component
// analytics/page.tsx - Could be server component
```

### Image Optimization

**Current:** No images on landing page

**Recommendation:** Use Next.js Image component when adding images

```tsx
import Image from 'next/image';

<Image
  src="/logo.png"
  alt="Logo"
  width={200}
  height={50}
/>
```

---

## Migration Priority

### HIGH PRIORITY (User-facing)

1. **Sign In / Sign Up** - First touchpoint for users
2. **Analytics** - Frequently used
3. **Jobs** - Frequently used
4. **Resumes** - Frequently used
5. **Candidate Detail** - Frequently used

### MEDIUM PRIORITY (Infrastructure)

1. **Middleware** - Server-side route protection
2. **Reusable Sidebar Component** - Centralize navigation
3. **AppShell Deprecation** - Remove old layout

### LOW PRIORITY (Cleanup)

1. **Remove Unused Components** - animated-dashboard, ai-copilot-panel
2. **Server Components** - Where applicable
3. **Image Optimization** - When adding images

---

## Future Enhancements

### Potential Additions

- **Middleware** - Server-side route protection
- **Reusable Sidebar** - Centralized navigation component
- **Loading States** - Consistent loading patterns
- **Error Boundaries** - Better error handling
- **404 Page** - Custom not found page
- **500 Page** - Custom error page

### Architecture Improvements

- **Server Components** - For static content
- **Streaming** - For large data sets
- **Parallel Routes** - For complex layouts
- **Route Groups** - Better organization

---

## Success Criteria

- ✅ All pages use monochromatic theme
- ✅ All pages use consistent layout (inline sidebar)
- ✅ No "signal" color references
- ✅ No slate/white color scheme
- ✅ Consistent navigation across all pages
- ✅ Server-side route protection
- ✅ No hydration warnings
- ✅ Clean component architecture

---

## File Structure

```
apps/web/
├── app/
│   ├── layout.tsx              # Root layout
│   ├── page.tsx                # Root page (redirect logic)
│   ├── globals.css            # Global styles
│   ├── landing/
│   │   └── page.tsx           # Landing page
│   ├── dashboard/
│   │   └── page.tsx           # Dashboard
│   ├── candidates/
│   │   ├── page.tsx           # Candidates list
│   │   └── [id]/
│   │       └── page.tsx       # Candidate detail
│   ├── copilot/
│   │   └── page.tsx           # AI copilot
│   ├── search/
│   │   └── page.tsx           # Semantic search
│   ├── analytics/
│   │   └── page.tsx           # Analytics (OLD)
│   ├── jobs/
│   │   └── page.tsx           # Jobs (OLD)
│   ├── resumes/
│   │   └── page.tsx           # Resumes (OLD)
│   ├── sign-in/
│   │   └── page.tsx           # Sign in (OLD)
│   └── sign-up/
│       └── page.tsx           # Sign up (OLD)
├── components/
│   ├── providers.tsx          # Context providers
│   ├── app-shell.tsx          # OLD layout (to deprecate)
│   ├── animated-dashboard.tsx # Unused (to remove)
│   ├── ai-copilot-panel.tsx   # Unused (to remove)
│   ├── analytics-charts.tsx   # Charts component
│   ├── ranking-visualization.tsx # Ranking viz
│   └── ui/
│       ├── button.tsx
│       ├── card.tsx
│       ├── input.tsx
│       ├── modal.tsx
│       ├── skeleton.tsx
│       ├── glass-card.tsx
│       ├── gradient-button.tsx
│       ├── ai-badge.tsx
│       ├── skill-tag.tsx
│       └── futuristic-table.tsx
├── lib/
│   ├── auth-context.ts        # Auth context
│   ├── api.ts                 # API client
│   └── animations.ts          # Animation variants
└── tailwind.config.ts         # Tailwind config
```

---

## Conclusion

The frontend route architecture is functional but has two coexisting layout systems. The new inline sidebar layout with monochromatic theme is the target state. Migration of old pages to the new system is required for consistency and maintainability.
