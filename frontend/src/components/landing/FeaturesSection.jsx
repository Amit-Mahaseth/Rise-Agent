import { useRef } from 'react';
import { motion, useInView } from 'framer-motion';
import { ArrowRight, Check } from 'lucide-react';
import WordsPullUpMultiStyle from './WordsPullUpMultiStyle';

const CARD_EASE = [0.22, 1, 0.36, 1];

function FeatureCard({ children, index }) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-100px' });

  return (
    <motion.div
      ref={ref}
      initial={{ scale: 0.95, opacity: 0 }}
      animate={isInView ? { scale: 1, opacity: 1 } : { scale: 0.95, opacity: 0 }}
      transition={{
        delay: index * 0.15,
        duration: 0.7,
        ease: CARD_EASE,
      }}
      className="rounded-2xl overflow-hidden h-full"
    >
      {children}
    </motion.div>
  );
}

function CheckItem({ text }) {
  return (
    <div className="flex items-start gap-2">
      <Check className="w-4 h-4 text-primary flex-shrink-0 mt-0.5" />
      <span className="text-gray-400 text-xs sm:text-sm">{text}</span>
    </div>
  );
}

function LearnMoreLink() {
  return (
    <a href="#" className="inline-flex items-center gap-1 text-gray-500 hover:text-primary text-xs sm:text-sm transition-colors group mt-auto">
      Learn more
      <ArrowRight className="w-3.5 h-3.5 -rotate-45 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
    </a>
  );
}

export default function FeaturesSection() {
  const headingSegments = [
    { text: 'Multilingual AI that reaches every lead.', className: 'text-[#E1E0CC]' },
    { text: 'Qualifies them. Hands them off perfectly.', className: 'text-gray-500' }, 
    
   
  ];

  return (
    <section className="relative min-h-screen bg-black py-20 sm:py-28 md:py-36 px-4 sm:px-6 overflow-hidden">
      {/* Noise overlay */}
      <div className="absolute inset-0 bg-noise opacity-[0.15] pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Header text */}
        <div className="text-center mb-12 sm:mb-16 md:mb-20">
          <h2 className="text-xl sm:text-2xl md:text-3xl lg:text-4xl font-normal">
            <WordsPullUpMultiStyle segments={headingSegments} />
          </h2>
        </div>

        {/* 4-column card grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-2 md:gap-1 lg:h-[480px]">

          {/* Card 1 — Video */}
          <FeatureCard index={0}>
            <div className="relative h-full min-h-[300px] lg:min-h-0 rounded-2xl overflow-hidden">
              <video
                src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260406_133058_0504132a-0cf3-4450-a370-8ea3b05c95d4.mp4"
                autoPlay
                loop
                muted
                playsInline
                className="absolute inset-0 w-full h-full object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
              <p className="absolute bottom-5 left-5 text-[#E1E0CC] text-sm sm:text-base font-medium">
                Every lead. Every language. Every time.
              </p>
            </div>
          </FeatureCard>

          {/* Card 2 — Project Storyboard */}
          <FeatureCard index={1}>
            <div className="bg-[#212121] rounded-2xl p-5 sm:p-6 h-full flex flex-col gap-4">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171918_4a5edc79-d78f-4637-ac8b-53c43c220606.png&w=1280&q=85"
                alt="Storyboard icon"
                className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg object-cover"
              />
              <div>
                <span className="text-gray-500 text-xs">01</span>
                <h3 className="text-[#E1E0CC] text-base sm:text-lg font-medium mt-1">
                  Instant Multilingual Outreach.
                </h3>
              </div>
              <div className="flex flex-col gap-2.5 flex-1">
                <CheckItem text="Calls every lead within 5 minutes of arrival" />
                <CheckItem text=" Speaks Hindi, Tamil, Telugu, Marathi, Gujarati" />
                <CheckItem text="Detects language automatically — no menu prompts" />
                <CheckItem text="Switches mid-call if the lead code-mixes" />
              </div>
              <LearnMoreLink />
            </div>
          </FeatureCard>

          {/* Card 3 — Smart Critiques */}
          <FeatureCard index={2}>
            <div className="bg-[#212121] rounded-2xl p-5 sm:p-6 h-full flex flex-col gap-4">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171741_ed9845ab-f5b2-4018-8ce7-07cc01823522.png&w=1280&q=85"
                alt="Critiques icon"
                className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg object-cover"
              />
              <div>
                <span className="text-gray-500 text-xs">02</span>
                <h3 className="text-[#E1E0CC] text-base sm:text-lg font-medium mt-1">
                  Context-Aware Conversations.
                </h3>
              </div>
              <div className="flex flex-col gap-2.5 flex-1">
                <CheckItem text="RAG over Rupeezy's AP sales script" />
                <CheckItem text="Handles all 5 core objections — never repeats one" />
                <CheckItem text="Powered by Groq + Gemini with automatic failover" />
              </div>
              <LearnMoreLink />
            </div>
          </FeatureCard>

          {/* Card 4 — Immersion Capsule */}
          <FeatureCard index={3}>
            <div className="bg-[#212121] rounded-2xl p-5 sm:p-6 h-full flex flex-col gap-4">
              <img
                src="https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260405_171809_f56666dc-c099-4778-ad82-9ad4f209567b.png&w=1280&q=85"
                alt="Immersion icon"
                className="w-10 h-10 sm:w-12 sm:h-12 rounded-lg object-cover"
              />
              <div>
                <span className="text-gray-500 text-xs">03</span>
                <h3 className="text-[#E1E0CC] text-base sm:text-lg font-medium mt-1">
                   Intelligent Lead Routing.
                </h3>
              </div>
              <div className="flex flex-col gap-2.5 flex-1">
                <CheckItem text="Weighted 5-signal scoring engine" />
                <CheckItem text="Hot → RM queue with full context packet" />
                <CheckItem text="Warm → WhatsApp auto-follow up + sign-up link" />
              </div>
              <LearnMoreLink />
            </div>
          </FeatureCard>
        </div>
      </div>
    </section>
  );
}
