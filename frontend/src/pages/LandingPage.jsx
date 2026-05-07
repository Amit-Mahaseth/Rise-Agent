import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import VideoBackground from '../components/landing/VideoBackground';
import GridOverlay from '../components/landing/GridOverlay';
import CentralGlow from '../components/landing/CentralGlow';
import LiquidGlassCard from '../components/landing/LiquidGlassCard';
import Navbar from '../components/landing/Navbar';
import WordsPullUp from '../components/landing/WordsPullUp';
import AboutSection from '../components/landing/AboutSection';
import FeaturesSection from '../components/landing/FeaturesSection';
import LenisProvider from '../components/landing/LenisProvider';

const CUSTOM_EASE = [0.16, 1, 0.3, 1];

export default function LandingPage() {
  return (
    <LenisProvider>
      <div className="bg-[#070b0a]">

        {/* ─── SECTION 1: HERO ─── */}
        <section className="relative min-h-screen overflow-hidden">
          {/* Background layers */}
          <VideoBackground />
          <GridOverlay />
          <CentralGlow />

          {/* Navigation */}
          <Navbar />

          {/* Bottom-positioned 12-col grid */}
          <div className="absolute bottom-0 left-0 right-0 z-10 px-4 sm:px-6 lg:px-10 pb-8 sm:pb-12 md:pb-16">
            <div className="max-w-[1600px] mx-auto grid grid-cols-12 gap-4 items-end">

              {/* Left 8 columns — Giant heading "Prisma" */}
              <div className="col-span-12 lg:col-span-8">
                {/* Liquid Glass Card floating above */}
                <div className="mb-4 opacity-0 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                  <LiquidGlassCard />
                </div>

                <h1 className="text-[26vw] sm:text-[24vw] md:text-[22vw] lg:text-[20vw] xl:text-[19vw] 2xl:text-[20vw] font-medium leading-[0.85] tracking-[-0.07em] text-[#E1E0CC]">
                  <WordsPullUp text="Rise.AI" showAsterisk />
                </h1>
              </div>

              {/* Right 4 columns — Description + CTA */}
              <div className="col-span-12 lg:col-span-4 pb-2 lg:pb-4">
                {/* Description */}
                <motion.p
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.5, duration: 0.8, ease: CUSTOM_EASE }}
                  className="text-primary/70 text-xs sm:text-sm md:text-base leading-[1.2] mb-6 sm:mb-8"
                >
                  82% of sales leads go cold before
                  anyone picks up the phone.

                  RiseAgent calls every lead within
                  5 minutes — in their language,
                  with the right answer, every time.

                </motion.p>

                {/* CTA Buttons */}
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.7, duration: 0.8, ease: CUSTOM_EASE }}
                  className="flex flex-wrap items-center gap-3"
                >
                  <Link
                    to="/dashboard"
                    className="group inline-flex items-center gap-2 hover:gap-3 bg-primary rounded-full pl-5 sm:pl-6 pr-1.5 py-1.5 transition-all duration-300"
                  >
                    <span className="text-white font-medium text-sm sm:text-base">
                      SEE IT LIVE 
                    </span>
                    <span className="bg-black rounded-full w-9 h-9 sm:w-10 sm:h-10 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                      <ArrowRight className="w-4 h-4 sm:w-5 sm:h-5 text-[#E1E0CC]" />
                    </span>
                  </Link>
                </motion.div>
              </div>
            </div>
          </div>

          {/* Scroll indicator */}
          <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 opacity-0 animate-fade-in hidden lg:flex" style={{ animationDelay: '1.5s' }}>
            <div className="flex flex-col items-center gap-2">
              <span className="text-[10px] uppercase tracking-[0.3em] text-white/20">Scroll</span>
              <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
            </div>
          </div>
        </section>

        {/* ─── SECTION 2: ABOUT ─── */}
        <AboutSection />

        {/* ─── SECTION 3: FEATURES ─── */}
        <FeaturesSection />

      </div>
    </LenisProvider>
  );
}
