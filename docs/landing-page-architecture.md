# Landing Page Architecture

## Overview

The landing page (`apps/web/app/landing/page.tsx`) is the public-facing entry point for Resume AI. It follows a minimal, monochromatic design philosophy with a clean, premium aesthetic inspired by modern AI-native SaaS products.

## Design Philosophy

- **Minimal**: Clean, uncluttered interface with essential elements only
- **Monochromatic**: Grayscale palette with single accent color (blue #3b82f6)
- **Premium**: Subtle animations, refined typography, consistent spacing
- **AI-native**: Visual language that feels intelligent and futuristic
- **Conversion-focused**: Clear CTAs, compelling value proposition

## Page Structure

### Hero Section
- **Purpose**: Capture attention, communicate value proposition
- **Elements**:
  - Large heading (text-5xl, font-bold)
  - Subheading (text-xl, foreground-muted)
  - Primary CTA button (accent background)
  - Secondary CTA link (foreground-muted)
- **Layout**: Centered, max-w-4xl container
- **Animation**: Fade-in with subtle Y translation

### Features Section
- **Purpose**: Showcase key capabilities
- **Elements**:
  - Section heading (text-3xl, font-bold)
  - Grid of feature cards (3 columns on desktop)
  - Each card: Icon, title, description
- **Layout**: Grid with gap-8, responsive to single column on mobile
- **Animation**: Staggered fade-in for cards

### Social Proof Section
- **Purpose**: Build trust and credibility
- **Elements**:
  - Section heading (text-3xl, font-bold)
  - Testimonial cards (2 columns on desktop)
  - Each testimonial: Quote, author, role
- **Layout**: Grid with gap-6, responsive
- **Animation**: Staggered fade-in

### CTA Section
- **Purpose**: Drive conversion
- **Elements**:
  - Large heading (text-4xl, font-bold)
  - Description (text-lg, foreground-muted)
  - Primary CTA button (accent background)
  - Secondary CTA link
- **Layout**: Centered, accent background card
- **Animation**: Scale-in effect

### Footer
- **Purpose**: Navigation and legal information
- **Elements**:
  - Logo and tagline
  - Navigation links (columns)
  - Copyright notice
- **Layout**: Grid with gap-12
- **Style**: Minimal, foreground-muted text

## Component Architecture

### Hero Component
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6 }}
  className="text-center"
>
  <h1 className="text-5xl font-bold mb-6">
    AI-Powered Recruiting
  </h1>
  <p className="text-xl text-foreground-muted mb-8">
    Find the perfect candidates with semantic search and AI ranking
  </p>
  <div className="flex gap-4 justify-center">
    <Link href="/sign-up" className="bg-accent px-8 py-3 rounded-lg">
      Get Started
    </Link>
  </div>
</motion.div>
```

### Feature Card Component
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: index * 0.1 }}
  className="rounded-xl bg-background-card border border-background-border p-6"
>
  <div className="h-12 w-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
    <Icon className="h-6 w-6 text-accent" />
  </div>
  <h3 className="text-xl font-semibold mb-2">Feature Title</h3>
  <p className="text-foreground-muted">Feature description</p>
</motion.div>
```

### Testimonial Card Component
```tsx
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: index * 0.1 }}
  className="rounded-xl bg-background-card border border-background-border p-6"
>
  <p className="text-foreground mb-4">"Quote text"</p>
  <div className="flex items-center gap-3">
    <div className="h-10 w-10 rounded-full bg-accent/20" />
    <div>
      <div className="font-semibold">Author Name</div>
      <div className="text-sm text-foreground-muted">Role</div>
    </div>
  </div>
</motion.div>
```

### CTA Section Component
```tsx
<motion.div
  initial={{ opacity: 0, scale: 0.9 }}
  animate={{ opacity: 1, scale: 1 }}
  className="rounded-2xl bg-accent p-12 text-center"
>
  <h2 className="text-4xl font-bold mb-4 text-white">
    Ready to Transform Your Hiring?
  </h2>
  <p className="text-lg text-white/80 mb-8">
    Join hundreds of recruiting teams using AI
  </p>
  <Link href="/sign-up" className="bg-white text-accent px-8 py-3 rounded-lg">
    Start Free Trial
  </Link>
</motion.div>
```

## Styling Guidelines

### Colors
- **Background**: `background` (#000000)
- **Cards**: `background-card` (#161616)
- **Borders**: `background-border` (#262626)
- **Text primary**: `foreground` (#ffffff)
- **Text secondary**: `foreground-muted` (#a3a3a3)
- **Accent**: `accent` (#3b82f6)
- **Accent hover**: `accent/90`

### Typography
- **Hero heading**: text-5xl, font-bold
- **Section heading**: text-3xl, font-bold
- **Card heading**: text-xl, font-semibold
- **Body text**: text-base, text-foreground
- **Description**: text-lg or text-base, text-foreground-muted

### Spacing
- **Section padding**: py-24 (6rem)
- **Card padding**: p-6 (1.5rem)
- **Gap between elements**: gap-4 to gap-8
- **Container max-width**: max-w-4xl or max-w-6xl

### Border Radius
- **Cards**: rounded-xl (1rem)
- **Buttons**: rounded-lg (0.75rem)
- **Icons**: rounded-lg (0.75rem)
- **Avatars**: rounded-full

### Shadows
- **Cards**: No shadow (clean, flat design)
- **Buttons**: No shadow
- **Hover states**: Border color change only

## Animation Strategy

### Principles
- **Subtle**: Minimal movement, no flashy effects
- **Fast**: 0.3-0.6s duration
- **Smooth**: Ease-out easing function
- **Staggered**: Sequential animations for lists

### Animation Patterns
```tsx
// Fade-in with Y translation
initial={{ opacity: 0, y: 20 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.6 }}

// Staggered list
transition={{ delay: index * 0.1 }}

// Scale-in for emphasis
initial={{ opacity: 0, scale: 0.9 }}
animate={{ opacity: 1, scale: 1 }}
transition={{ duration: 0.5 }}
```

### Animation Timing
- **Hero**: 0.6s duration
- **Feature cards**: 0.1s stagger
- **Testimonials**: 0.1s stagger
- **CTA section**: 0.5s duration

## Responsive Design

### Mobile (< 640px)
- **Hero**: Single column, smaller text (text-4xl)
- **Features**: Single column stack
- **Testimonials**: Single column stack
- **CTA**: Full-width buttons
- **Footer**: Single column

### Tablet (640px - 1024px)
- **Hero**: Centered, text-5xl
- **Features**: 2-column grid
- **Testimonials**: 2-column grid
- **CTA**: Centered
- **Footer**: 2-column grid

### Desktop (> 1024px)
- **Hero**: Centered, text-5xl
- **Features**: 3-column grid
- **Testimonials**: 2-column grid
- **CTA**: Centered
- **Footer**: 4-column grid

## Performance Considerations

### Code Splitting
- **Lazy loading**: Not currently implemented
- **Dynamic imports**: Consider for large sections
- **Image optimization**: Use Next.js Image component

### Animation Performance
- **GPU acceleration**: Use transform and opacity
- **Avoid layout thrashing**: Use transform instead of top/left
- **Reduce reflows**: Batch DOM updates

### Bundle Size
- **Tree shaking**: Framer Motion exports
- **Minification**: Automatic in production
- **Code splitting**: Consider for future optimization

## Accessibility

### Semantic HTML
- **Headings**: Proper h1-h6 hierarchy
- **Links**: Descriptive text
- **Buttons**: Clear labels
- **Landmarks**: Use semantic elements

### Keyboard Navigation
- **Tab order**: Logical left-to-right, top-to-bottom
- **Focus states**: Visible accent color outline
- **Skip links**: Not currently implemented

### Screen Readers
- **ARIA labels**: Add where needed
- **Alt text**: For images (if added)
- **Semantic structure**: Use proper HTML elements

## SEO Considerations

### Meta Tags
- **Title**: Resume AI - AI-Powered Recruiting
- **Description**: Find the perfect candidates with semantic search and AI ranking
- **Keywords**: AI recruiting, semantic search, candidate ranking

### Open Graph
- **Title**: Resume AI
- **Description**: AI-powered recruiting platform
- **Image**: Add OG image
- **URL**: Canonical URL

### Structured Data
- **Organization**: Add schema markup
- **Product**: Add product schema
- **Reviews**: Add review schema (if applicable)

## Conversion Optimization

### CTA Placement
- **Hero**: Primary CTA above fold
- **Features**: Secondary CTAs in cards
- **Testimonials**: No CTAs (social proof only)
- **Bottom CTA**: Final conversion push

### CTA Design
- **Primary**: Accent background, white text
- **Secondary**: Transparent, foreground-muted text
- **Hover**: Background darkening
- **Size**: Consistent (px-8 py-3)

### Value Proposition
- **Hero**: Clear headline, specific benefit
- **Features**: Benefit-focused descriptions
- **Testimonials**: Social proof, specific results
- **CTA**: Clear action, low friction

## Future Enhancements

### Planned Features
- **Interactive demo**: Embedded product tour
- **Video section**: Product walkthrough
- **Pricing table**: Clear pricing tiers
- **FAQ section**: Common questions
- **Blog preview**: Latest content

### Potential Improvements
- **A/B testing**: Test different headlines
- **Personalization**: Dynamic content based on source
- **Live chat**: Support widget
- **Social proof**: Logos, case studies
- **Analytics**: Conversion tracking

## File Structure

```
apps/web/app/landing/
└── page.tsx          # Main landing page component
```

## Dependencies

### Required
- **Next.js**: React framework
- **Framer Motion**: Animation library
- **Lucide React**: Icon library
- **Tailwind CSS**: Styling

### Optional (Future)
- **React Intersection Observer**: Scroll animations
- **React Hook Form**: Contact forms
- **Zustand**: State management
- **SWR**: Data fetching

## Testing Considerations

### Visual Testing
- **Screenshot testing**: Ensure consistent rendering
- **Responsive testing**: Test all breakpoints
- **Cross-browser testing**: Chrome, Firefox, Safari

### Performance Testing
- **Lighthouse**: Score > 90
- **Core Web Vitals**: All green
- **Bundle size**: Monitor size

### Accessibility Testing
- **axe DevTools**: No violations
- **Keyboard navigation**: Fully functional
- **Screen reader**: Compatible with NVDA, JAWS

## Maintenance

### Content Updates
- **Testimonials**: Regular updates
- **Features**: Add new features as released
- **Pricing**: Update as needed
- **Blog**: Link to latest posts

### Design Updates
- **Theme tokens**: Update in tailwind.config.ts
- **Components**: Reuse from components/ui/
- **Animations**: Keep subtle and fast
- **Responsive**: Test on new devices

## Analytics Integration

### Tracking
- **Page views**: Track landing page visits
- **CTA clicks**: Track button interactions
- **Scroll depth**: Track engagement
- **Time on page**: Track interest

### Tools
- **Google Analytics**: Page views, events
- **Hotjar**: Heatmaps, recordings
- **Mixpanel**: User behavior
- **PostHog**: Alternative to Mixpanel

## Security Considerations

### Form Handling
- **CSRF protection**: Use Next.js CSRF
- **Input validation**: Server-side validation
- **Rate limiting**: Prevent abuse
- **Sanitization**: Prevent XSS

### External Links
- **Rel="noopener"**: For external links
- **Rel="noreferrer"**: For privacy
- **HTTPS only**: All links secure
- **Tracking**: Respect privacy settings

## Browser Support

### Target Browsers
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

### Fallbacks
- **CSS**: Graceful degradation
- **JavaScript**: Progressive enhancement
- **Animations**: Disable if prefers-reduced-motion
- **Images**: Alt text for accessibility

## Deployment

### Build Process
- **Static generation**: Pre-render at build time
- **Incremental**: Revalidate on demand
- **CDN**: Serve from edge network
- **Caching**: Aggressive caching policy

### Environment Variables
- **NEXT_PUBLIC_SITE_URL**: Canonical URL
- **NEXT_PUBLIC_ANALYTICS_ID**: Analytics tracking
- **NEXT_PUBLIC_FEATURE_FLAGS**: Feature toggles

## Monitoring

### Error Tracking
- **Sentry**: Error monitoring
- **LogRocket**: Session replay
- **Vercel Analytics**: Performance monitoring

### Performance Monitoring
- **Core Web Vitals**: Track metrics
- **Lighthouse CI**: Automated testing
- **RUM**: Real user monitoring

## Conclusion

The landing page architecture prioritizes simplicity, performance, and conversion. By following the monochromatic design system and maintaining consistent patterns, the page delivers a premium user experience that aligns with the overall Resume AI brand identity.
