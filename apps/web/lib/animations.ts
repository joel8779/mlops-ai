// Centralized animation variants for consistent motion system
// All animations are subtle, fast, and restrained

export const fadeInUp = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
};

export const fadeInLeft = {
  initial: { opacity: 0, x: -10 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
};

export const fadeInRight = {
  initial: { opacity: 0, x: 10 },
  animate: { opacity: 1, x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
};

export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
};

export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.2, ease: "easeOut" }
};

// Staggered animations for lists (minimal delay)
export const staggerContainer = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.3, ease: "easeOut" }
};

export const staggerItem = {
  initial: { opacity: 0, y: 5 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.2, ease: "easeOut" }
};

// Sidebar animation
export const sidebarSlide = {
  initial: { x: -300 },
  animate: { x: 0 },
  transition: { duration: 0.3, ease: "easeOut" }
};

// Overlay animation
export const overlayFade = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  transition: { duration: 0.2, ease: "easeOut" }
};
