declare module "framer-motion" {
  import * as React from "react";

  type MotionProps = React.HTMLAttributes<HTMLElement> & {
    initial?: unknown;
    animate?: unknown;
    exit?: unknown;
    transition?: unknown;
    whileHover?: unknown;
    whileTap?: unknown;
    variants?: unknown;
  };

  export const motion: {
    div: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLDivElement>>;
    section: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLElement>>;
    button: React.ForwardRefExoticComponent<MotionProps & React.RefAttributes<HTMLButtonElement>>;
  };

  export const AnimatePresence: React.FC<React.PropsWithChildren<{ mode?: string }>>;
}
