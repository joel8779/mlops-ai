# Frontend Visual Guidelines

## Design Philosophy

The Resume AI frontend follows a minimal, monochromatic, dark-first design philosophy inspired by premium AI-native SaaS products like Linear, OpenAI, and Perplexity. The design prioritizes:

- **Minimalism**: Clean interfaces with essential elements only
- **Monochromatic**: Grayscale palette with single accent color
- **Premium feel**: Subtle animations, refined typography, consistent spacing
- **AI-native**: Visual language that feels intelligent and futuristic
- **Cohesion**: Unified visual language across all pages and components

## Visual Hierarchy

### Primary Elements
- **Headings**: Bold, large font sizes (text-2xl, text-xl)
- **Actions**: Accent color buttons for primary CTAs
- **Key metrics**: Large numbers with accent color highlights

### Secondary Elements
- **Body text**: Regular weight, foreground-muted color
- **Labels**: Small, uppercase, muted color
- **Metadata**: Subtle color, smaller font size

### Tertiary Elements
- **Borders**: Subtle background-border color
- **Backgrounds**: Layered background colors for depth
- **Decorations**: Minimal, purposeful only

## Layout Principles

### Grid Systems
- **Dashboard**: 4-column grid for stats, flexible for content
- **Cards**: Consistent padding (p-6), rounded corners (rounded-xl)
- **Lists**: Vertical stack with consistent spacing (gap-4, gap-6)

### Spacing
- **Section spacing**: 3xl (4rem) between major sections
- **Component spacing**: lg (1.5rem) between components
- **Element spacing**: md (1rem) between related elements
- **Tight spacing**: sm (0.5rem) for related items

### Alignment
- **Left alignment**: Default for text and content
- **Center alignment**: Hero sections, empty states
- **Right alignment**: Actions, metadata

## Component Design

### Cards
- **Background**: `background-card`
- **Border**: `background-border`
- **Radius**: `xl` (1rem)
- **Padding**: `p-6`
- **Hover**: Border color changes to `accent/50`
- **Shadow**: None (clean, flat design)

### Buttons
- **Primary**: `accent` background, white text, rounded-lg
- **Secondary**: `background-card` background, foreground text, rounded-lg
- **Ghost**: Transparent, foreground-muted text, rounded-lg
- **Size**: Standard height (h-10 or h-12)
- **Padding**: px-6 py-3 for standard buttons
- **Hover**: Background color darkens by 10%

### Inputs
- **Background**: `background-elevated`
- **Border**: `background-border`
- **Radius**: `lg` (0.75rem)
- **Padding**: px-4 py-3
- **Focus**: Border changes to `accent/50`
- **Placeholder**: `foreground-subtle`

### Badges
- **Background**: Accent/semantic color at 10% opacity
- **Border**: Accent/semantic color at 20% opacity
- **Text**: Full accent/semantic color
- **Radius**: `lg` (0.75rem)
- **Padding**: px-3 py-1
- **Font size**: `text-sm`

## Typography

### Font Family
- **Primary**: Inter (system-ui fallback)
- **Monospace**: SF Mono (Monaco fallback)

### Font Sizes
- **H1**: text-3xl (30px)
- **H2**: text-2xl (24px)
- **H3**: text-xl (20px)
- **Body**: text-base (16px)
- **Small**: text-sm (14px)
- **Tiny**: text-xs (12px)

### Font Weights
- **Bold**: font-bold (700) - headings
- **Semibold**: font-semibold (600) - emphasis
- **Medium**: font-medium (500) - labels
- **Regular**: font-normal (400) - body

### Line Heights
- **Tight**: leading-tight (1.25)
- **Normal**: leading-normal (1.5)
- **Relaxed**: leading-relaxed (1.625)

### Color Usage
- **Primary text**: `foreground` (white)
- **Secondary text**: `foreground-muted` (#a3a3a3)
- **Tertiary text**: `foreground-subtle` (#737373)
- **Accent text**: `accent` (#3b82f6) - emphasis only
- **Links**: `accent` with hover to `accent-subtle`

## Color Usage Guidelines

### Accent Color
- **Primary buttons**: Full accent background
- **Active states**: Accent border or background
- **Highlights**: Accent text for emphasis
- **Icons**: Accent for interactive elements
- **Usage**: Sparingly, for CTAs and active states only

### Semantic Colors
- **Success**: Positive outcomes, completed states
- **Warning**: Cautionary states, pending actions
- **Error**: Negative outcomes, error messages
- **Usage**: Status indicators, feedback only

### Grayscale
- **Backgrounds**: Layered grays for depth
- **Borders**: Subtle gray for separation
- **Text**: Muted grays for hierarchy
- **Usage**: Everything else

## Iconography

### Icon Style
- **Library**: Lucide React
- **Size**: h-4 to h-6 depending on context
- **Color**: Inherit from text or accent for emphasis
- **Weight**: Default (stroke-based)

### Icon Usage
- **Navigation**: h-5, foreground-muted → foreground on hover
- **Actions**: h-5, accent for primary actions
- **Status**: h-4, semantic colors
- **Decorative**: h-4, foreground-muted

## Animation Guidelines

### Principles
- **Subtle**: Minimal movement, no flashy effects
- **Fast**: 0.2-0.4s duration
- **Smooth**: Ease-out easing function
- **Purposeful**: Only when it adds value

### Common Animations
- **Fade-in**: opacity 0→1, translateY 10px→0
- **Stagger**: delay i * 0.05 for lists
- **Hover**: transition-colors for color changes
- **Loading**: Simple rotation, 1s duration
- **Sidebar**: x -300→0 for mobile menu

### Animation Properties
```tsx
// Fade-in
initial={{ opacity: 0, y: 10 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.3, ease: "easeOut" }}

// Stagger
transition={{ delay: i * 0.05 }}

// Hover
className="transition-colors duration-200"
```

## Responsive Design

### Breakpoints
- **Mobile**: < 640px (hidden sidebar, stacked layout)
- **Tablet**: 640px - 1024px (compact sidebar)
- **Desktop**: > 1024px (full sidebar, grid layouts)

### Mobile Adaptations
- **Sidebar**: Collapsible with hamburger menu
- **Grid**: Stack to single column
- **Cards**: Full width
- **Typography**: Smaller font sizes

### Desktop Enhancements
- **Sidebar**: Fixed, always visible
- **Grid**: Multi-column layouts
- **Cards**: Constrained width
- **Typography**: Larger font sizes

## Accessibility

### Contrast
- **Text**: Minimum 4.5:1 contrast ratio
- **UI elements**: Minimum 3:1 contrast ratio
- **Focus states**: Visible accent color outline

### Focus States
- **Inputs**: accent/50 border on focus
- **Buttons**: Slight background darkening
- **Links**: Underline on focus

### Keyboard Navigation
- **Tab order**: Logical left-to-right, top-to-bottom
- **Skip links**: Not currently implemented
- **ARIA labels**: Add where needed

## Page-Specific Guidelines

### Landing Page
- **Hero**: Centered, large heading, accent CTA
- **Features**: Grid layout, icon + text
- **Testimonials**: Cards with quotes
- **CTA**: Full-width accent section

### Dashboard
- **Stats**: 4-column grid, large numbers
- **Charts**: Card-based, accent highlights
- **Lists**: Vertical stack, hover states
- **Sidebar**: Fixed left navigation

### Candidates
- **Cards**: Horizontal layout, avatar + content
- **Skills**: Tag pills, background-elevated
- **Actions**: Button group, accent primary
- **Filters**: Collapsible sidebar

### AI Copilot
- **Messages**: Chat bubble layout
- **User**: Right-aligned, accent background
- **AI**: Left-aligned, card background
- **Input**: Full-width, large text area

### Semantic Search
- **Search**: Large input, accent button
- **Filters**: Sidebar, collapsible
- **Results**: Cards with relevance scores
- **Empty states**: Centered, accent icon

## Common Patterns

### Empty States
- **Icon**: Large, accent/10 background
- **Heading**: text-xl, semibold
- **Description**: text-sm, foreground-muted
- **CTA**: Accent button, if applicable

### Loading States
- **Spinner**: Simple rotation, accent border
- **Skeleton**: Not currently implemented
- **Text**: "Loading..." with foreground-muted

### Error States
- **Background**: error/10
- **Border**: error/20
- **Text**: error color
- **Icon**: Error icon, optional

## Best Practices

1. **Consistency**: Use the same patterns across pages
2. **Simplicity**: Remove unnecessary elements
3. **Hierarchy**: Use size, color, and spacing for visual hierarchy
4. **Whitespace**: Generous spacing for breathing room
5. **Contrast**: Ensure text is readable
6. **Performance**: Keep animations lightweight
7. **Accessibility**: Consider all users
8. **Responsiveness**: Test on all screen sizes

## Anti-Patterns

1. **Colorful gradients**: Avoid multi-color gradients
2. **Excessive glow**: No neon or glow effects
3. **Complex animations**: Keep animations simple
4. **Mixed styles**: Don't combine different design languages
5. **Hardcoded colors**: Always use theme tokens
6. **Over-decoration**: Remove unnecessary visual elements
7. **Inconsistent spacing**: Use the spacing scale
8. **Poor contrast**: Ensure text is readable
