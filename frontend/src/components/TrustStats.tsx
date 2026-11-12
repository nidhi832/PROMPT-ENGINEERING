import React from 'react';
import { Download, MessageSquare, Star, Award } from 'lucide-react';

export const TrustStats: React.FC = () => {
  const stats = [
    {
      num: '20M+',
      label: 'Downloads',
      icon: <Download className="w-4 h-4 sm:w-5 sm:h-5 text-[#171717] animate-rb-icon-1" />,
      sub: 'Trusted globally',
    },
    {
      num: '270K',
      label: 'Reviews',
      icon: <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5 text-[#171717] animate-rb-icon-2" />,
      sub: 'User verified feedback',
    },
    {
      num: '4.7',
      label: 'Ratings',
      icon: <Star className="w-4 h-4 sm:w-5 sm:h-5 text-[#171717] animate-rb-twinkle" />,
      sub: 'Top-rated finance app',
    },
    {
      num: "Editors'",
      label: 'Choice',
      sublabel: 'Google Play',
      icon: <Award className="w-4 h-4 sm:w-5 sm:h-5 text-[#171717] animate-rb-wobble" />,
      sub: 'Award winning UX',
    },
  ];

  return (
    <section className="py-10 sm:py-14 bg-white border-b border-[#EEEEEE]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 items-center justify-center">
          {stats.map((s, idx) => (
            <div key={idx} className="flex items-center justify-center gap-1.5 sm:gap-2.5">
              {/* Left Laurel Wreath Branch SVG */}
              <svg className="w-5 h-11 sm:w-7 sm:h-14 text-[#A0A0A0] flex-shrink-0" viewBox="0 0 40 80" fill="currentColor">
                <path d="M30 75C22 68 15 58 12 45C10 35 12 22 22 10C24 8 26 9 25 11C18 20 16 32 18 42C20 52 26 62 33 71C34 73 32 76 30 75Z" opacity="0.6"/>
                <path d="M26 18C20 16 12 18 8 24C6 26 8 28 10 27C15 23 21 22 26 23C28 23 28 19 26 18Z"/>
                <path d="M22 34C15 32 8 35 4 41C2 43 5 45 7 43C12 39 18 38 23 39C25 40 25 35 22 34Z"/>
                <path d="M22 50C15 49 9 52 5 58C3 60 6 62 8 60C12 56 18 54 23 55C25 56 25 51 22 50Z"/>
              </svg>

              {/* Center Content */}
              <div className="flex flex-col items-center text-center">
                <div className="mb-0.5 text-[#171717]">{s.icon}</div>
                <div className="text-lg sm:text-2xl font-extrabold text-[#171717] leading-none">
                  {s.num}
                </div>
                <div className="text-[11px] sm:text-sm font-bold text-[#444444] mt-0.5 whitespace-nowrap">
                  {s.label}
                </div>
                {s.sublabel && (
                  <div className="text-[9px] sm:text-[11px] font-semibold text-[#858585] leading-none mt-0.5 whitespace-nowrap">
                    {s.sublabel}
                  </div>
                )}
              </div>

              {/* Right Laurel Wreath Branch SVG */}
              <svg className="w-5 h-11 sm:w-7 sm:h-14 text-[#A0A0A0] flex-shrink-0 transform scale-x-[-1]" viewBox="0 0 40 80" fill="currentColor">
                <path d="M30 75C22 68 15 58 12 45C10 35 12 22 22 10C24 8 26 9 25 11C18 20 16 32 18 42C20 52 26 62 33 71C34 73 32 76 30 75Z" opacity="0.6"/>
                <path d="M26 18C20 16 12 18 8 24C6 26 8 28 10 27C15 23 21 22 26 23C28 23 28 19 26 18Z"/>
                <path d="M22 34C15 32 8 35 4 41C2 43 5 45 7 43C12 39 18 38 23 39C25 40 25 35 22 34Z"/>
                <path d="M22 50C15 49 9 52 5 58C3 60 6 62 8 60C12 56 18 54 23 55C25 56 25 51 22 50Z"/>
              </svg>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
