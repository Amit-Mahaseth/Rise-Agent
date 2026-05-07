import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';

/**
 * WordsPullUpMultiStyle
 * Takes an array of { text, className } segments.
 * Splits all text into individual words, preserving per-word className.
 * Each word animates with a pull-up stagger effect.
 */
export default function WordsPullUpMultiStyle({ segments, containerClassName = '' }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  // Build flat word list with per-word className
  const allWords = [];
  segments.forEach((seg) => {
    const words = seg.text.split(' ').filter(Boolean);
    words.forEach((word) => {
      allWords.push({ word, className: seg.className || '' });
    });
  });

  return (
    <span ref={ref} className={`inline-flex flex-wrap justify-center ${containerClassName}`}>
      {allWords.map((item, i) => (
        <motion.span
          key={i}
          initial={{ y: 20, opacity: 0 }}
          animate={isInView ? { y: 0, opacity: 1 } : { y: 20, opacity: 0 }}
          transition={{
            delay: i * 0.08,
            duration: 0.6,
            ease: [0.16, 1, 0.3, 1],
          }}
          className={`inline-block mr-[0.25em] ${item.className}`}
        >
          {item.word}
        </motion.span>
      ))}
    </span>
  );
}
