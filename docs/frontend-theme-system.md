# Frontend Theme System

## Overview

The Resume AI frontend uses a monochromatic dark-first design system with a single accent color. This theme system ensures consistency across all pages and components while maintaining a premium, minimal, AI-native aesthetic.

## Color Palette

### Background Colors
- `background`: `#000000` - Pure black for main backgrounds
- `background-surface`: `#0a0a0a` - Slightly elevated surface
- `background-elevated`: `#111111` - Elevated elements
- `background-card`: `#161616` - Card backgrounds
- `background-border`: `#262626` - Border color

### Foreground Colors
- `foreground`: `#ffffff` - Primary text
- `foreground-muted`: `#a3a3a3` - Secondary text
- `foreground-subtle`: `#737373` - Subtle/disabled text
- `foreground-disabled`: `#525252` - Disabled text

### Accent Color
- `accent`: `#3b82f6` - Primary accent (muted electric blue)
- `accent-muted`: `#1e40af` - Muted accent variant
- `accent-subtle`: `#60a5fa` - Subtle accent variant

### Semantic Colors
- `success`: `#22c55e` - Success states
- `success-muted`: `#166534` - Muted success
- `warning`: `#eab308` - Warning states
- `warning-muted`: `#a16207` - Muted warning
- `error`: `#ef4444` - Error states
- `error-muted`: `#991b1b` - Muted error

## Spacing Scale

- `xs`: `0.25rem` (4px)
- `sm`: `0.5rem` (8px)
- `md`: `1rem` (16px)
- `lg`: `1.5rem` (24px)
- `xl`: `2rem` (32px)
- `2xl`: `3rem` (48px)
- `3xl`: `4rem` (64px)

## Border Radius

- `sm`: `0.375rem` (6px)
- `md`: `0.5rem` (8px)
- `lg`: `0.75rem` (12px)
- `xl`: `1rem` (16px)
- `2xl`: `1.5rem` (24px)

## Shadows

- `shadow-subtle`: `0 1px 2px 0 rgba(0, 0, 0, 0.05)`
- `shadow-medium`: `0 4px 6px -1px rgba(0, 0, 0, 0.1)`
- `shadow-large`: `0 10px 15px -3px rgba(0, 0, 0, 0.1)`

## Typography

### Font Families
- Sans: `Inter`, `system-ui`, `sans-serif`
- Mono: `SF Mono`, `Monaco`, `Consolas`, `monospace`

### Typography Hierarchy
- Headings: Bold, large font sizes
- Body: Regular weight, readable
- Secondary: Muted color for less important text
- Labels: Small, uppercase for form labels

## Component Patterns

### Cards
- Background: `background-card`
- Border: `background-border`
- Border radius: `lg` or `xl`
- Hover: Border color changes to `accent/50`

### Buttons
- Primary: `accent` background, white text
- Secondary: `background-card` background, `foreground` text
- Ghost: Transparent background, `foreground-muted` text
- Hover states: Slight background color change

### Inputs
- Background: `background-elevated`
- Border: `background-border`
- Focus: Border changes to `accent/50`
- Placeholder: `foreground-subtle`

### Badges
- Accent: `accent/10` background, `accent` text
- Success: `success/10` background, `success` text
- Warning: `warning/10` background, `warning` text
- Error: `error/10` background, `error` text

## Animation Guidelines

### Principles
- Subtle and restrained
- Smooth transitions (0.2-0.4s)
- Minimal movement
- No flashy effects

### Common Animations
- Fade-in: `opacity: 0 → 1`, `translateY: 10px → 0`
- Stagger: `delay: i * 0.05` for lists
- Hover: `transition-colors` for color changes
- Loading: Simple rotation

## Usage Examples

### Tailwind Classes
```tsx
// Background
className="bg-background"
className="bg-background-card"
className="bg-background-elevated"

// Text
className="text-foreground"
className="text-foreground-muted"
className="text-accent"

// Border
className="border-background-border"
className="border-accent/30"

// Interactive
className="hover:bg-background-elevated hover:border-accent/50 transition-colors"
```

### Component Example
```tsx
<div className="rounded-xl bg-background-card border border-background-border p-6 hover:border-accent/50 transition-colors">
  <h2 className="text-xl font-semibold text-foreground mb-2">Title</h2>
  <p className="text-foreground-muted">Description text</p>
</div>
```

## Dark Mode

The theme is dark-first by default. All components are designed for dark mode with proper contrast ratios. No light mode variant is currently implemented.

## Accessibility

- Text contrast ratios meet WCAG AA standards
- Focus states use accent color for visibility
- Disabled states use muted colors
- Semantic colors provide clear visual feedback

## File Locations

- Theme tokens: `apps/web/tailwind.config.ts`
- Global styles: `apps/web/app/globals.css`
- Components: `apps/web/components/ui/`
- Pages: `apps/web/app/`

## Best Practices

1. Always use theme tokens instead of hardcoded colors
2. Maintain consistent spacing using the spacing scale
3. Use accent color sparingly for emphasis only
4. Keep animations subtle and fast
5. Ensure proper contrast for text
6. Use semantic colors for status indicators
7. Maintain consistent border radius across components
