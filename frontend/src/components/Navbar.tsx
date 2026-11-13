import React, { useState, useEffect } from 'react';
import { Wallet, Menu, X, ArrowRight } from 'lucide-react';

interface NavbarProps {
  onOpenAuth: (mode: 'signin' | 'signup') => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAuth }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 40);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { name: 'Home', href: '#home' },
    { name: 'Features', href: '#features' },
    { name: 'Screenshots', href: '#screenshots' },
    { name: 'Dashboard', href: '#dashboard-preview' },
    { name: 'Help Center', href: '#help-center' },
  ];

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'bg-white/95 backdrop-blur-md border-b border-[#EEEEEE] shadow-xs py-3.5'
          : 'bg-transparent py-5'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          {/* Brand Logo */}
          <a href="#home" className="flex items-center gap-2.5 group">
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center transition-all ${
                isScrolled
                  ? 'bg-[#FF665C] text-white shadow-md shadow-[#FF665C]/25'
                  : 'bg-white/20 text-white backdrop-blur-xs border border-white/30'
              }`}
            >
              <Wallet className="w-5 h-5 stroke-[2.2]" />
            </div>
            <div className="flex items-center gap-1.5">
              <span
                className={`font-extrabold text-xl tracking-tight font-sans transition-colors ${
                  isScrolled ? 'text-[#171717]' : 'text-white'
                }`}
              >
                SpendWise
              </span>
            </div>
          </a>

          {/* Center Navigation Links (Desktop) */}
          <div className="hidden md:flex items-center gap-6 lg:gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className={`text-[14px] font-semibold transition-colors ${
                  isScrolled
                    ? 'text-[#555555] hover:text-[#171717]'
                    : 'text-white/90 hover:text-white'
                }`}
              >
                {link.name}
              </a>
            ))}
          </div>

          {/* Right Action Buttons */}
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={() => onOpenAuth('signin')}
              className={`text-[14px] font-semibold px-3 py-1.5 transition-colors ${
                isScrolled
                  ? 'text-[#171717] hover:text-[#FF665C]'
                  : 'text-white/90 hover:text-white'
              }`}
            >
              Open demo
            </button>
            <button
              onClick={() => onOpenAuth('signup')}
              className={`inline-flex items-center gap-1.5 px-4.5 py-2 rounded-xl text-[14px] font-bold transition-all shadow-md ${
                isScrolled
                  ? 'bg-[#FF665C] hover:bg-[#EE554B] text-white shadow-[#FF665C]/25'
                  : 'bg-white hover:bg-white/95 text-[#FF665C] shadow-black/10'
              }`}
            >
              <span>Get Started</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Mobile Menu Trigger */}
          <div className="flex md:hidden items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className={`p-2 rounded-lg transition-colors ${
                isScrolled ? 'text-[#171717]' : 'text-white'
              }`}
              aria-label="Toggle Navigation Menu"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-white border-b border-[#EEEEEE] px-4 pt-3 pb-6 space-y-3 shadow-xl animate-in slide-in-from-top-3 duration-200">
          <div className="flex flex-col space-y-1">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                className="px-3.5 py-2.5 rounded-lg text-[15px] font-medium text-[#444444] hover:text-[#171717] hover:bg-[#F7F8FA]"
              >
                {link.name}
              </a>
            ))}
          </div>
          <div className="pt-3 border-t border-[#EEEEEE] flex flex-col gap-2.5">
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenAuth('signin');
              }}
              className="w-full text-center py-2.5 rounded-xl border border-[#EEEEEE] text-[14px] font-semibold text-[#171717]"
            >
              Open demo
            </button>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                onOpenAuth('signup');
              }}
              className="w-full text-center py-2.5 rounded-xl bg-[#FF665C] text-white text-[14px] font-semibold shadow-md shadow-[#FF665C]/25"
            >
              Try the demo
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};
