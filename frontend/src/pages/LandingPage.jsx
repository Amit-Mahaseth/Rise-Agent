import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import VideoBackground from '../components/landing/VideoBackground';
import GridOverlay from '../components/landing/GridOverlay';
import CentralGlow from '../components/landing/CentralGlow';
import LiquidGlassCard from '../components/landing/LiquidGlassCard';
import Navbar from '../components/landing/Navbar';

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-[#070b0a] overflow-hidden">
      {/* Background layers */}
      <VideoBackground />
      <GridOverlay />
      <CentralGlow />

      {/* Navigation */}
      <Navbar />

      {/* Hero Section */}
      <section className="relative z-10 min-h-screen flex flex-col items-start justify-center px-6 lg:px-0">
        <div className="max-w-7xl mx-auto w-full">
          <div className="max-w-3xl">
            {/* Liquid Glass Card */}
            <div className="mb-4 opacity-0 animate-fade-in" style={{ animationDelay: '0.2s' }}>
              <LiquidGlassCard />
            </div>

            {/* Eyebrow */}
            <div
              className="opacity-0 animate-fade-in-up"
              style={{ animationDelay: '0.4s' }}
            >
              <span className="font-jakarta font-bold text-[11px] uppercase tracking-[0.2em] text-rise-green">
                Career-Ready Curriculum
              </span>
            </div>

            {/* Main headline */}
            <h1
              className="mt-5 text-[40px] sm:text-[52px] md:text-[60px] lg:text-[72px] font-black uppercase leading-[0.95] tracking-tight text-white opacity-0 animate-fade-in-up"
              style={{ animationDelay: '0.6s' }}
            >
              LAUNCH YOUR
              <br />
              CODING CAREER
              <span className="text-rise-green">.</span>
            </h1>

            {/* Description */}
            <p
              className="mt-6 text-[14px] leading-relaxed text-white/50 max-w-[512px] opacity-0 animate-fade-in-up"
              style={{ animationDelay: '0.8s' }}
            >
              Master in-demand coding skills with project-based learning,
              mentorship from industry professionals, and a curriculum designed
              to get you hired at top tech companies.
            </p>

            {/* CTA Button */}
            <div
              className="mt-10 opacity-0 animate-fade-in-up"
              style={{ animationDelay: '1s' }}
            >
              <Link
                to="/dashboard"
                className="group inline-flex items-center gap-2.5 px-7 py-3.5 bg-rise-green text-[#070b0a] font-bold text-[13px] uppercase tracking-wider rounded-full hover:bg-[#4ec28c] transition-all duration-300 hover:shadow-lg hover:shadow-rise-green/25 active:scale-[0.97]"
              >
                Get Started
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-300" />
              </Link>
            </div>

            {/* Stats row */}
            <div
              className="mt-16 flex items-center gap-10 opacity-0 animate-fade-in-up"
              style={{ animationDelay: '1.2s' }}
            >
              <div>
                <p className="text-2xl font-bold text-white">50K+</p>
                <p className="text-[11px] text-white/30 uppercase tracking-wider mt-1">
                  Students Enrolled
                </p>
              </div>
              <div className="w-px h-10 bg-white/10" />
              <div>
                <p className="text-2xl font-bold text-white">95%</p>
                <p className="text-[11px] text-white/30 uppercase tracking-wider mt-1">
                  Placement Rate
                </p>
              </div>
              <div className="w-px h-10 bg-white/10 hidden sm:block" />
              <div className="hidden sm:block">
                <p className="text-2xl font-bold text-white">200+</p>
                <p className="text-[11px] text-white/30 uppercase tracking-wider mt-1">
                  Industry Mentors
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Scroll indicator */}
      <div className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 opacity-0 animate-fade-in" style={{ animationDelay: '1.5s' }}>
        <div className="flex flex-col items-center gap-2">
          <span className="text-[10px] uppercase tracking-[0.3em] text-white/20">Scroll</span>
          <div className="w-px h-8 bg-gradient-to-b from-white/20 to-transparent" />
        </div>
      </div>
    </div>
  );
}
