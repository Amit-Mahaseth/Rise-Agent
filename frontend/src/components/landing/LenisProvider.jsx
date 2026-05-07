import { useEffect } from 'react';
import Lenis from 'lenis';

/**
 * LenisProvider
 * Initializes Lenis smooth scrolling with autoRaf for buttery-smooth scroll.
 */
export default function LenisProvider({ children }) {
  useEffect(() => {
    const lenis = new Lenis({
      autoRaf: true,
      duration: 1.2,
      easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
      orientation: 'vertical',
      gestureOrientation: 'vertical',
      smoothWheel: true,
    });

    return () => {
      lenis.destroy();
    };
  }, []);

  return children;
}
