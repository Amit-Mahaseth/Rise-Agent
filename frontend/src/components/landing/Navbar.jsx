import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react';

const NAV_LINKS = [
  { label: 'HOW IT WORKS', href: '#features' },
  { label: 'FEATURES ', href: '#features' },
  { label: 'GITHUB', href: 'https://github.com/anand-1109/RiseAgent', isRoute: true },
  { label: 'ABOUT', href: '#about ' },
  { label: 'DASHBOARD', href: '/dashboard', isRoute: true },
];

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <header className="absolute top-0 left-0 right-0 z-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3 group">
              <div className="w-5 h-5 rounded-lg bg-white/10 backdrop-blur-sm border border-white/10 flex items-center justify-center group-hover:bg-rise-green/20 transition-all duration-300">
                <span className="text-rise-green font-bold text-sm">R</span>
              </div>
              <span className="text-white font-italic font-serif text-lg tracking-tight">
                Rise<span className="text-rise-green">Agent</span>
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {NAV_LINKS.map(({ label, href, isRoute }) =>
                isRoute ? (
                  <Link
                    key={label}
                    to={href}
                    className="text-[14px] font-medium text-white/60 hover:text-rise-green transition-colors duration-300 tracking-wide"
                  >
                    {label}
                  </Link>
                ) : (
                  <a
                    key={label}
                    href={href}
                    className="text-[14px] font-medium text-white/60 hover:text-rise-green transition-colors duration-300 tracking-wide"
                  >
                    {label}
                  </a>
                )
              )}
            </nav>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="md:hidden relative z-50 w-10 h-10 flex items-center justify-center rounded-lg bg-white/5 border border-white/10 hover:bg-white/10 transition-all"
              aria-label="Toggle menu"
            >
              {isOpen ? (
                <X className="w-5 h-5 text-white" />
              ) : (
                <Menu className="w-5 h-5 text-white" />
              )}
            </button>
          </div>
        </div>
      </header>

      {/* Mobile menu overlay */}
      <div
        className={`fixed inset-0 z-40 bg-[#070b0a]/95 backdrop-blur-xl transition-all duration-500 md:hidden ${
          isOpen
            ? 'opacity-100 pointer-events-auto'
            : 'opacity-0 pointer-events-none'
        }`}
      >
        <nav className="flex flex-col items-center justify-center h-full gap-8">
          {NAV_LINKS.map(({ label, href, isRoute }, i) =>
            isRoute ? (
              <Link
                key={label}
                to={href}
                onClick={() => setIsOpen(false)}
                className="text-2xl font-bold text-white/80 hover:text-rise-green transition-colors duration-300 tracking-wide"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                {label}
              </Link>
            ) : (
              <a
                key={label}
                href={href}
                onClick={() => setIsOpen(false)}
                className="text-2xl font-bold text-white/80 hover:text-rise-green transition-colors duration-300 tracking-wide"
                style={{ animationDelay: `${i * 100}ms` }}
              >
                {label}
              </a>
            )
          )}
        </nav>
      </div>
    </>
  );
}
