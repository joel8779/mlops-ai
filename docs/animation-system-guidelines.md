# Animation System Guidelines

## Overview

The Resume AI frontend uses a minimal, restrained animation system powered by Framer Motion. All animations are designed to be subtle, fast, and purposeful - never flashy or distracting.

## Design Philosophy

- **Subtle**: Animations should enhance, not dominate
- **Fast**: 0.2-0.4s duration maximum
- **Smooth**: Use ease-out easing function
- **Purposeful**: Every animation should have a clear purpose
- **Restrained**: No excessive motion, no chaotic effects

## Centralized Animation System

All animation variants are centralized in `lib/animations.ts` for consistency across the application.

### Available Variants

```typescript
// Fade in with upward translation
fadeInUp = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Fade in from left
fadeInLeft = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Fade in from right
fadeInRight = {
  initial: { opacity: 0, x: 10 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Scale in
scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Simple fade
fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.2, ease: "easeOut" }
}

// Staggered list container
staggerContainer = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Staggered list item
staggerItem = {
  initial: { opacity: 0, y: 5 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.2, ease: "easeOut" }
}

// Sidebar slide
sidebarSlide = {
  initial: { x: -300 },
  animate: { x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
}

// Overlay fade
overlayFade = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.2, ease: "easeOut" }
}
```

## Usage Patterns

### Import Variants

```tsx
import { fadeInUp, fadeInLeft, fadeInRight, scaleIn } from "@/lib/animations";
```

### Apply to Motion Components

```tsx
<motion.div {...fadeInUp}>
  Content
</motion.div>
```

### Add Staggered Delays

```tsx
{items.map((item, i) => (
  <motion.div
    key={i}
    {...fadeInUp}
    transition={{ delay: i * 0.05 }}
  >
    {item}
  </motion.div>
))}
```

## Animation Patterns by Use Case

### Page Load Animations

**Hero Section:**
```tsx
<motion.div {...fadeInUp} className="text-center">
  <h1>Hero Title</h1>
</motion.div>
```

**Dashboard Preview:**
```tsx
<motion.div
  {...fadeInUp}
  transition={{ delay: 0.2 }}
  className="dashboard-preview"
>
  Preview content
</motion.div>
```

### Section Transitions

**Left-to-Right Layout:**
```tsx
<motion.div {...fadeInLeft} className="text-content">
  Text content
</motion.div>
<motion.div {...fadeInRight} className="visual-content">
  Visual content
</motion.div>
```

**Right-to-Left Layout:**
```tsx
<motion.div {...fadeInRight} className="text-content">
  Text content
</motion.div>
<motion.div {...fadeInLeft} className="visual-content">
  Visual content
</motion.div>
```

### List Animations

**Feature Grid:**
```tsx
{features.map((feature, i) => (
  <motion.div
    key={i}
    {...fadeInUp}
    transition={{ delay: i * 0.1 }}
    className="feature-card"
  >
    {feature}
  </motion.div>
))}
```

**Testimonials:**
```tsx
{testimonials.map((testimonial, i) => (
  <motion.div
    key={i}
    {...fadeInUp}
    transition={{ delay: i * 0.1 }}
    className="testimonial-card"
  >
    {testimonial}
  </motion.div>
))}
```

### Interactive Elements

**Sidebar:**
```tsx
<motion.div
  initial={{ x: -300 }}
  animate={{ x: sidebarOpen ? 0 : -300 }}
  transition={{ duration: 0.3, ease: "easeOut" }}
  className="sidebar"
>
  Sidebar content
</motion.div>
```

**Overlay:**
```tsx
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0 }}
  transition={{ duration: 0.2 }}
  className="overlay"
>
  Overlay content
</motion.div>
```

### Progress Animations

**Progress Bars:**
```tsx
<motion.div
  initial={{ width: 0 }}
  animate={{ width: `${percentage}%` }}
  transition={{ duration: 0.8, ease: "easeOut" }}
  className="progress-bar"
/>
```

## Anti-Patterns

### Avoid

❌ **Excessive Delays**
```tsx
// BAD: Too many staggered delays
transition={{ delay: i * 0.2 }}
```

❌ **Large Translations**
```tsx
// BAD: Too much movement
initial={{ opacity: 0, y: 100 }}
animate={{ opacity: 1, y: 0 }}
```

❌ **Long Durations**
```tsx
// BAD: Too slow
transition={{ duration: 1.5 }}
```

❌ **Complex Easing**
```tsx
// BAD: Unnecessary complexity
transition={{ ease: [0.25, 0.1, 0.25, 1] }}
```

❌ **whileInView Overuse**
```tsx
// BAD: Can cause hydration issues
<motion.div whileInView={{ opacity: 1 }}>
  Content
</motion.div>
```

❌ **Nested Animations**
```tsx
// BAD: Performance impact
<motion.div animate={{ x: 100 }}>
  <motion.div animate={{ y: 100 }}>
    Content
  </motion.div>
</motion.div>
```

### Preferred

✅ **Minimal Delays**
```tsx
// GOOD: Subtle stagger
transition={{ delay: i * 0.05 }}
```

✅ **Small Translations**
```tsx
// GOOD: Subtle movement
initial={{ opacity: 0, y: 10 }}
animate={{ opacity: 1, y: 0 }}
```

✅ **Fast Durations**
```tsx
// GOOD: Quick and smooth
transition={{ duration: 0.3 }}
```

✅ **Simple Easing**
```tsx
// GOOD: Standard easing
transition={{ ease: "easeOut" }}
```

✅ **Use Centralized Variants**
```tsx
// GOOD: Consistent
<motion.div {...fadeInUp}>
  Content
</motion.div>
```

✅ **Animate on Mount**
```tsx
// GOOD: Predictable
<motion.div
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
>
  Content
</motion.div>
```

## Performance Guidelines

### GPU Acceleration

Use transform and opacity for GPU-accelerated animations:
```tsx
// GOOD: GPU accelerated
<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
/>

// BAD: Not GPU accelerated
<motion.div
  initial={{ top: 100 }}
  animate={{ top: 0 }}
/>
```

### Avoid Layout Thrashing

Don't animate properties that trigger layout reflows:
- `top`, `left`, `right`, `bottom`
- `width`, `height`
- `margin`, `padding`

Instead use:
- `transform: translateX/Y`
- `opacity`

### Reduce Re-renders

Use `layout` prop sparingly - it's expensive:
```tsx
// BAD: Expensive
<motion.div layout>

// GOOD: Cheaper
<motion.div animate={{ height: "auto" }}>
```

## Hydration Best Practices

### Avoid whileInView

The `whileInView` prop can cause hydration mismatches. Use `animate` instead:

```tsx
// BAD: Can cause hydration issues
<motion.div whileInView={{ opacity: 1 }} viewport={{ once: true }}>

// GOOD: Predictable
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
```

### Use "use client" Boundaries

Mark components that use animations as client components:
```tsx
"use client";

import { motion } from "framer-motion";

export default function AnimatedComponent() {
  return <motion.div {...fadeInUp}>Content</motion.div>;
}
```

### Avoid Random Values

Don't use random values during render:
```tsx
// BAD: Different on server and client
const randomDelay = Math.random();

// GOOD: Deterministic
const delay = index * 0.1;
```

## Accessibility

### Respect Reduced Motion

Check for `prefers-reduced-motion`:
```tsx
const prefersReducedMotion = useReducedMotion();

<motion.div
  {...(prefersReducedMotion ? {} : fadeInUp)}
>
  Content
</motion.div>
```

### Provide Alternatives

Ensure content is accessible without animations:
```tsx
<motion.div {...fadeInUp} aria-live="polite">
  Content
</motion.div>
```

## Page-Specific Guidelines

### Landing Page

- Hero: `fadeInUp` with 0.2s delay for preview
- Features: `fadeInUp` with staggered delays (0.1s)
- Testimonials: `fadeInUp` with staggered delays (0.1s)
- CTA: `scaleIn` for emphasis

### Dashboard

- Stats: `fadeInUp` with staggered delays (0.05s)
- Charts: `fadeInUp` with 0.3s delay
- Lists: `fadeInUp` with staggered delays (0.05s)

### Candidates

- Cards: `fadeInUp` with staggered delays (0.05s)
- Filters: `fadeInLeft` for sidebar
- Details: `fadeInUp` for content

### AI Copilot

- Messages: `fadeInUp` with staggered delays
- Typing indicator: Simple rotation
- Quick actions: `fadeInUp`

### Search

- Input: `fadeInUp`
- Filters: `fadeInLeft`
- Results: `fadeInUp` with staggered delays (0.05s)

## Testing

### Visual Testing

- Test animations at 60fps
- Check for stuttering or jank
- Verify smooth transitions
- Test on mobile devices

### Performance Testing

- Use Chrome DevTools Performance tab
- Monitor frame rate
- Check for layout shifts
- Measure animation impact

### Accessibility Testing

- Test with screen readers
- Verify keyboard navigation
- Test with reduced motion preference
- Check focus states

## Troubleshooting

### Animation Not Playing

**Cause:** Missing `initial` prop
**Fix:** Always provide both `initial` and `animate`

```tsx
// GOOD
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>

// BAD
<motion.div animate={{ opacity: 1 }}>
```

### Hydration Mismatch

**Cause:** Using `whileInView` or random values
**Fix:** Use `animate` instead of `whileInView`, avoid random values

### Performance Issues

**Cause:** Too many animations or expensive properties
**Fix:** Reduce animation count, use GPU-accelerated properties

### Layout Shifts

**Cause:** Animating layout properties
**Fix:** Use transform instead of top/left/width/height

## Migration Guide

### Old Pattern

```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.6 }}
>
  Content
</motion.div>
```

### New Pattern

```tsx
import { fadeInUp } from "@/lib/animations";

<motion.div {...fadeInUp}>
  Content
</motion.div>
```

## Future Enhancements

### Potential Additions

- Scroll-triggered animations (if needed)
- Parallax effects (minimal, if needed)
- Micro-interactions (hover, focus)
- Loading skeletons with animation

### Considerations

- Keep animations minimal
- Prioritize performance over effects
- Maintain consistency across pages
- Document any new patterns

## Conclusion

The animation system is designed to be minimal, fast, and consistent. Always use the centralized variants from `lib/animations.ts` and follow the guidelines above to ensure a premium, smooth user experience.
