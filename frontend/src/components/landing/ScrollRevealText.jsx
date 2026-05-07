import { useRef } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';

/**
 * AnimatedChar
 * A single character whose opacity is driven by scroll position.
 */
function AnimatedChar({ char, charProgress, scrollYProgress }) {
  const start = Math.max(charProgress - 0.1, 0);
  const end = Math.min(charProgress + 0.05, 1);
  const opacity = useTransform(scrollYProgress, [start, end], [0.2, 1]);

  return (
    <motion.span style={{ opacity }}>
      {char}
    </motion.span>
  );
}

/**
 * AnimatedWord
 * Wraps each character of a word in AnimatedChar.
 * Words are rendered as inline-block so they wrap naturally at word boundaries.
 */
function AnimatedWord({ word, startIndex, totalChars, scrollYProgress }) {
  return (
    <span className="inline-block whitespace-nowrap">
      {word.split('').map((char, i) => (
        <AnimatedChar
          key={i}
          char={char}
          charProgress={(startIndex + i) / totalChars}
          scrollYProgress={scrollYProgress}
        />
      ))}
    </span>
  );
}

/**
 * ScrollRevealText
 * Splits text into words and renders each as an AnimatedWord.
 * Spaces between words allow natural line wrapping while
 * characters within words stay together.
 */
export default function ScrollRevealText({ text, className = '', style = {} }) {
  const ref = useRef(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start 0.8', 'end 0.2'],
  });

  const words = text.split(' ');
  const totalChars = text.length;

  let charIndex = 0;

  return (
    <p ref={ref} className={className} style={style}>
      {words.map((word, wi) => {
        const wordStartIndex = charIndex;
        charIndex += word.length + 1; // +1 for the space
        return (
          <span key={wi}>
            <AnimatedWord
              word={word}
              startIndex={wordStartIndex}
              totalChars={totalChars}
              scrollYProgress={scrollYProgress}
            />
            {wi < words.length - 1 && ' '}
          </span>
        );
      })}
    </p>
  );
}
