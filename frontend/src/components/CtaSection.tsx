import React from 'react';
import { ArrowRight, Sparkles, ShieldCheck } from 'lucide-react';

interface CtaProps {
  onGetStarted: () => void;
  onExplore: () => void;
}

export const CtaSection: React.FC<CtaProps> = ({ onGetStarted, onExplore }) => {
  return (
    <section className="py-20 bg-gradient-to-b from-white to-[#F7F8FA] border-t border-[#EEEEEE]">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative rounded-3xl p-10 sm:p-14 bg-gradient-to-br from-[#FFF5F4] via-[#FFFFFF] to-[#FFF0EE] border border-[#FF665C]/25 shadow-xl overflow-hidden text-center">
          {/* Subtle decorative circles */}
          <div className="absolute -top-16 -right-16 w-56 h-56 rounded-full bg-[#FF665C]/10 blur-2xl pointer-events-none" />
          <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full bg-[#3498F3]/10 blur-2xl pointer-events-none" />

          <div className="relative z-10 max-w-2xl mx-auto">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white border border-[#FF665C]/30 text-[12px] font-bold text-[#FF665C] mb-4 shadow-2xs">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Double-Entry Simplicity</span>
            </div>

            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight leading-tight">
              Start making smarter financial decisions today.
            </h2>

            <p className="mt-4 text-base sm:text-lg text-[#666666] leading-relaxed">
              Bring your income, expenses and savings together in one simple experience.
            </p>

            <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5">
              <button
                onClick={onGetStarted}
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-[#FF665C] hover:bg-[#EE554B] text-white text-[15px] font-bold shadow-lg shadow-[#FF665C]/25 hover:shadow-xl hover:shadow-[#FF665C]/35 hover:-translate-y-0.5 transition-all duration-150 flex items-center justify-center gap-2"
              >
                <span>Get Started Now</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={onExplore}
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl bg-white hover:bg-[#F7F8FA] border border-[#EEEEEE] text-[#171717] text-[15px] font-semibold hover:border-[#DDDDDD] transition-all duration-150"
              >
                Explore SpendWise
              </button>
            </div>

            <div className="mt-6 flex items-center justify-center gap-4 text-xs text-[#858585]">
              <span className="flex items-center gap-1.5">
                <ShieldCheck className="w-4 h-4 text-[#2ED573]" /> Free Tier
              </span>
              <span>•</span>
              <span>No Credit Card Required</span>
              <span>•</span>
              <span>100% Client-Side Privacy</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
