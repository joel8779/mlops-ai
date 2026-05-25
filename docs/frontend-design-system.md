# Frontend Design System

## Overview

This document defines the design system for the Resume AI frontend application. The design system follows a futuristic, AI-native aesthetic inspired by Linear, Vercel, Perplexity, and other modern AI SaaS platforms.

## Color Palette

### Primary Colors
- **Violet**: `#8b5cf6` (primary accent)
- **Blue**: `#3b82f6` (secondary accent)
- **Gradient**: Violet to Blue gradient (`from-violet-600 to-blue-600`)

### Neutral Colors
- **Black**: `#000000` (background)
- **Slate-900**: `#0f172a` (dark backgrounds)
- **Slate-800**: `#1e293b` (card backgrounds)
- **Slate-400**: `#94a3b8` (secondary text)
- **Slate-300**: `#cbd5e1` (primary text)
- **White**: `#ffffff` (text and highlights)

### Semantic Colors
- **Green**: `#22c55e` (success, high relevance)
- **Red**: `#ef4444` (errors, high priority)
- **Yellow**: `#eab308` (warnings, medium priority)
- **Orange**: `#f97316` (info, low priority)

## Typography

### Font Family
- Primary: System sans-serif (Inter, SF Pro, Segoe UI)
- Monospace: System monospace (for code snippets)

### Font Sizes
- **xs**: `0.75rem` (12px)
- **sm**: `0.875rem` (14px)
- **base**: `1rem` (16px)
- **lg**: `1.125rem` (18px)
- **xl**: `1.25rem` (20px)
- **2xl**: `1.5rem` (24px)
- **3xl**: `1.875rem` (30px)
- **4xl**: `2.25rem` (36px)

### Font Weights
- **normal**: `400`
- **medium**: `500`
- **semibold**: `600`
- **bold**: `700`

## Spacing

### Scale
- **1**: `0.25rem` (4px)
- **2**: `0.5rem` (8px)
- **3**: `0.75rem` (12px)
- **4**: `1rem` (16px)
- **5**: `1.25rem` (20px)
- **6**: `1.5rem` (24px)
- **8**: `2rem` (32px)
- **10**: `2.5rem` (40px)
- **12**: `3rem` (48px)

## Border Radius

- **sm**: `0.375rem` (6px)
- **md**: `0.5rem` (8px)
- **lg**: `0.75rem` (12px)
- **xl**: `1rem` (16px)
- **2xl**: `1.5rem` (24px)
- **3xl**: `2rem` (32px)

## Components

### Glass Card
A glassmorphism card with backdrop blur and gradient background.

```tsx
import { GlassCard } from "@/components/ui/glass-card";

<GlassCard hover={true} gradient={true}>
  <div>Card content</div>
</GlassCard>
```

**Props:**
- `hover`: Enable hover scale effect (default: true)
- `gradient`: Use gradient background (default: true)
- `className`: Additional CSS classes

### Gradient Button
A gradient button with loading state and animations.

```tsx
import { GradientButton } from "@/components/ui/gradient-button";

<GradientButton variant="primary" size="md" loading={false}>
  Click me
</GradientButton>
```

**Props:**
- `variant`: "primary" | "secondary" | "ghost" (default: "primary")
- `size`: "sm" | "md" | "lg" (default: "md")
- `loading`: Show loading spinner (default: false)
- `disabled`: Disable button (default: false)

### AI Badge
A badge displaying AI scores or relevance metrics.

```tsx
import { AIBadge } from "@/components/ui/ai-badge";

<AIBadge score={85} label="AI Score" variant="score" size="md" />
```

**Props:**
- `score`: Numeric score (0-100)
- `label`: Optional label text
- `variant`: "score" | "relevance" | "match" (default: "score")
- `size`: "sm" | "md" | "lg" (default: "md")

### Skill Tag
A tag for displaying skills with hover effects.

```tsx
import { SkillTag } from "@/components/ui/skill-tag";

<SkillTag skill="Python" variant="default" size="md" />
```

**Props:**
- `skill`: Skill name
- `variant`: "default" | "highlighted" | "muted" (default: "default")
- `size`: "sm" | "md" | "lg" (default: "md")
- `onClick`: Optional click handler

### Modal
A modal dialog with backdrop blur and animations.

```tsx
import { Modal } from "@/components/ui/modal";

<Modal isOpen={true} onClose={() => {}} title="Modal Title" size="md">
  <div>Modal content</div>
</Modal>
```

**Props:**
- `isOpen`: Whether modal is open
- `onClose`: Close handler
- `title`: Optional title
- `size`: "sm" | "md" | "lg" | "xl" (default: "md")

### Futuristic Table
A table with glassmorphism styling and row animations.

```tsx
import { FuturisticTable } from "@/components/ui/futuristic-table";

<FuturisticTable
  headers={["Name", "Role", "Score"]}
  data={[
    ["John Doe", "Engineer", "85%"],
    ["Jane Smith", "Designer", "92%"],
  ]}
/>
```

**Props:**
- `headers`: Array of column headers
- `data`: 2D array of cell content
- `className`: Additional CSS classes

## Effects

### Glassmorphism
- Background: `bg-gradient-to-br from-slate-900/50 to-slate-800/50`
- Backdrop blur: `backdrop-blur-sm`
- Border: `border border-white/10`
- Hover: `hover:border-violet-500/50`

### Gradients
- Primary: `bg-gradient-to-r from-violet-600 to-blue-600`
- Hover: `hover:from-violet-500 hover:to-blue-500`
- Shadow: `shadow-lg shadow-violet-500/25`

### Animations
- Page load: `initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}`
- Stagger: `transition={{ delay: index * 0.05 }}`
- Hover: `whileHover={{ scale: 1.02 }}`
- Tap: `whileTap={{ scale: 0.98 }}`

## Iconography

### Icon Library
- Primary: Lucide React
- Usage: Import from `lucide-react`

### Common Icons
- `Sparkles`: AI/magic
- `Bot`: AI assistant
- `Search`: Search functionality
- `User`: User/profile
- `Settings`: Settings
- `Menu`: Hamburger menu
- `X`: Close/dismiss
- `Star`: Ratings/scores
- `TrendingUp`: Analytics/growth
- `ArrowUpRight`: Navigation/external links

## Responsive Breakpoints

- **sm**: `640px`
- **md`: `768px`
- **lg**: `1024px`
- **xl**: `1280px`
- **2xl**: `1536px`

## Accessibility

### Color Contrast
- All text meets WCAG AA standards (4.5:1 contrast ratio)
- Interactive elements have clear focus states

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Tab order follows logical flow
- Focus indicators are visible

### Screen Readers
- Semantic HTML elements used throughout
- ARIA labels where necessary
- Alt text for images

## Best Practices

### Component Usage
- Use design system components instead of custom styling
- Maintain consistent spacing and sizing
- Follow the established color palette
- Use animations sparingly and purposefully

### Performance
- Lazy load components where appropriate
- Optimize images and assets
- Use React.memo for expensive components
- Implement proper loading states

### Code Organization
- Keep components focused and reusable
- Use TypeScript for type safety
- Follow consistent naming conventions
- Document complex components
