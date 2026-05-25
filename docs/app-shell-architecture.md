# App Shell Architecture

## Root Layout

`apps/web/app/layout.tsx` is the only App Router layout. It wraps all routes with:

- `Providers`
- `AuthProvider`
- `QueryClientProvider`
- `ScrollRestoration`

No nested layout currently swallows or replaces `children`.

## Authenticated Shell

Authenticated routes render their own `AppShell` component. The shell is responsible for:

- Session guard and redirect to `/login`.
- Fixed sidebar navigation.
- Sticky top status bar.
- Visible child content region.

## Layout Rules

The sidebar must not participate in normal desktop document flow. It remains fixed so page content is never pushed below the first viewport.

Main content must reserve sidebar width with margin, not padding on a block rendered after a static sidebar:

- Correct: `lg:ml-72`
- Avoid: static desktop sidebar followed by padded main content

## Content Slot

`{children}` is rendered directly inside the shell content wrapper:

```tsx
<main className="relative min-h-screen lg:ml-72">
  <header>...</header>
  <div className="relative z-10 p-4 sm:p-6 xl:p-8">{children}</div>
</main>
```

This keeps route pages visible, scrollable, and above background grid layers.
