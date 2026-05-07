import WordsPullUpMultiStyle from './WordsPullUpMultiStyle';
import ScrollRevealText from './ScrollRevealText';

export default function AboutSection() {
  const headingSegments = [
    { text: 'We built RiseAgent AI', className: 'font-normal' },
    { text: 'to fix a broken process.', className: 'italic font-serif' },
    { text: 'Every Lead Every Time Always...', className: 'font-normal' },
    { text: 'No Delay Anymore!', className: 'font-normal' },
  ];

  return (
    <section className="bg-black py-20 sm:py-28 md:py-36 px-4 sm:px-6">
      <div className="max-w-6xl mx-auto">
        <div className="bg-[#101010] rounded-3xl py-16 sm:py-20 md:py-28 px-6 sm:px-10 md:px-16 text-center">
          {/* Label */}
          <p className="text-primary text-[10px] sm:text-xs uppercase tracking-[0.3em] mb-8 sm:mb-10">
            RISE AGENT
          </p>

          {/* Multi-style heading */}
          <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl max-w-3xl mx-auto leading-[0.95] sm:leading-[0.9]">
            <WordsPullUpMultiStyle segments={headingSegments} />
          </h2>

          {/* Scroll-reveal paragraph — centered */}
          <div className="mt-10 sm:mt-14 md:mt-16 max-w-lg mx-auto text-center">
            <ScrollRevealText
              text="Built by Team MINDBOT at Technocrats Institute of Technology, Bhopal — using Groq, Gemini, Sarvam AI, LangChain, and React 18. Every lead contacted. Every conversation remembered. Every RM empowered with full context.."
              className="text-[#DEDBC8] text-xs sm:text-sm md:text-base"
              style={{ lineHeight: 1.2 }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
