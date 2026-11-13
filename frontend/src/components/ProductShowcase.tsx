import React, { useState } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export const ProductShowcase: React.FC = () => {
  const [themeMode, setThemeMode] = useState<'light' | 'dark'>('light');
  const [activeSlide, setActiveSlide] = useState(0);

  const isDark = themeMode === 'dark';

  const slides = [
    {
      id: 'budget',
      title: 'Budget',
      component: (
        <div className={`rb-phone-screen h-[460px] p-4 flex flex-col justify-between ${isDark ? 'bg-[#18181B] text-white' : 'bg-white text-[#171717]'}`}>
          <div>
            <div className="flex justify-between items-center text-xs font-bold text-[#858585] mb-2 pt-5">
              <span>Stats</span>
              <span className="text-[#FF665C] border-b border-[#FF665C] pb-0.5">Budget</span>
              <span>Note</span>
            </div>
            <div className="text-center my-3">
              <div className="text-[10px] text-[#858585] font-bold">Remaining (Monthly)</div>
              <div className={`text-xl font-black mt-0.5 ${isDark ? 'text-white' : 'text-[#171717]'}`}>
                ₹ -26.00
              </div>
            </div>

            {/* Category Progress Bars */}
            <div className="space-y-2.5 text-[11px] pt-1">
              <div>
                <div className="flex justify-between font-bold mb-1">
                  <span>Monthly</span>
                  <span className="text-[#FF665C]">103% • -₹26.00</span>
                </div>
                <div className="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div className="h-full bg-[#FF665C] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-bold mb-1">
                  <span>Apparel</span>
                  <span className="text-[#FF665C]">109% • -₹13.51</span>
                </div>
                <div className="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div className="h-full bg-[#FF665C] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-bold mb-1">
                  <span>Culture</span>
                  <span className="text-[#FF665C]">124% • -₹24.00</span>
                </div>
                <div className="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div className="h-full bg-[#FF665C] rounded-full" style={{ width: '100%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-bold mb-1">
                  <span>Food &amp; Dining</span>
                  <span className="text-[#3498F3]">92% • ₹17.79</span>
                </div>
                <div className="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div className="h-full bg-[#3498F3] rounded-full" style={{ width: '92%' }} />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-bold mb-1">
                  <span>Health</span>
                  <span className="text-[#3498F3]">89% • ₹10.01</span>
                </div>
                <div className="w-full h-2 rounded-full bg-black/10 overflow-hidden">
                  <div className="h-full bg-[#3498F3] rounded-full" style={{ width: '89%' }} />
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-between text-[9px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            <span>Monthly Setting</span>
            <span>Sub-category Setup</span>
          </div>
        </div>
      ),
    },
    {
      id: 'accounts',
      title: 'Accounts',
      component: (
        <div className={`rb-phone-screen h-[460px] p-4 flex flex-col justify-between ${isDark ? 'bg-[#18181B] text-white' : 'bg-white text-[#171717]'}`}>
          <div>
            <div className="flex justify-between items-center text-xs font-bold pt-5 pb-2 border-b border-[#EEEEEE]">
              <span>Accounts</span>
              <span>✏️ +</span>
            </div>
            
            {/* Top Three Columns */}
            <div className="grid grid-cols-3 text-center my-3 pb-2 border-b border-[#EEEEEE]">
              <div>
                <div className="text-[9px] font-bold text-[#858585]">Account</div>
                <div className="text-xs font-extrabold text-[#3498F3]">₹8,828.12</div>
              </div>
              <div>
                <div className="text-[9px] font-bold text-[#858585]">Liabilities</div>
                <div className="text-xs font-extrabold text-[#FF665C]">₹208,242.65</div>
              </div>
              <div>
                <div className="text-[9px] font-bold text-[#858585]">Total</div>
                <div className="text-xs font-extrabold text-[#171717] dark:text-white">-₹201,614.53</div>
              </div>
            </div>

            {/* Account Rows */}
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center py-1 border-b border-[#F5F5F5]">
                <div className="font-bold">Cash</div>
                <span className="font-extrabold text-[#3498F3]">₹68.45</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-[#F5F5F5]">
                <div>
                  <div className="font-bold">Salary Account</div>
                  <div className="text-[9px] text-[#858585]">Active Checking</div>
                </div>
                <span className="font-extrabold text-[#3498F3]">₹2,768.06</span>
              </div>
              <div className="flex justify-between items-center py-1 border-b border-[#F5F5F5]">
                <div>
                  <div className="font-bold">Credit Card</div>
                  <div className="text-[9px] text-[#858585]">Due in 12 days</div>
                </div>
                <span className="font-extrabold text-[#FF665C]">₹2,183.61</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <div>
                  <div className="font-bold">Savings &amp; Deposit</div>
                  <div className="text-[9px] text-[#858585]">Emergency Fund</div>
                </div>
                <span className="font-extrabold text-[#3498F3]">₹100.00</span>
              </div>
            </div>
          </div>

          <div className="flex justify-between text-[9px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            <span>Asset Ledger</span>
            <span>Double-Entry Balance</span>
          </div>
        </div>
      ),
    },
    {
      id: 'widget',
      title: 'iOS Widget',
      component: (
        <div className="rb-phone-screen h-[460px] bg-gradient-to-br from-[#7F00FF] to-[#E100FF] p-4 flex flex-col justify-between text-white relative">
          <div className="pt-6">
            <div className="w-full bg-white/20 backdrop-blur-md rounded-2xl p-2 flex items-center justify-center text-xs font-medium mb-8">
              🔍 Search
            </div>

            {/* Widget Card */}
            <div className="bg-white/90 backdrop-blur-md rounded-3xl p-5 text-[#171717] shadow-xl">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-base">🐷</span>
                <span className="text-xs font-extrabold">SPENDWISE</span>
                <span className="text-[10px] text-[#858585] ml-auto">Today: ₹0</span>
              </div>

              <div className="grid grid-cols-4 gap-2 text-center text-xs pt-1">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center text-base mb-1">
                    🔍
                  </div>
                  <span className="text-[10px] font-bold text-[#555555]">Search</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center text-base mb-1">
                    ⭐
                  </div>
                  <span className="text-[10px] font-bold text-[#555555]">Bookmark</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center text-base mb-1">
                    ➕
                  </div>
                  <span className="text-[10px] font-bold text-[#555555]">Entry</span>
                </div>
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-[#F5F5F5] flex items-center justify-center text-base mb-1">
                    🧾
                  </div>
                  <span className="text-[10px] font-bold text-[#555555]">Bill</span>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center text-[10px] font-semibold text-white/80 pb-2">
            One-Tap Quick Entry Widget
          </div>
        </div>
      ),
    },
    {
      id: 'calendar',
      title: 'Calendar',
      component: (
        <div className={`rb-phone-screen h-[460px] p-4 flex flex-col justify-between ${isDark ? 'bg-[#18181B] text-white' : 'bg-white text-[#171717]'}`}>
          <div>
            <div className="flex justify-between items-center text-xs font-bold text-[#858585] mb-2 pt-5 border-b border-[#EEEEEE] pb-2">
              <span className="text-[#FF665C]">Calendar</span>
              <span className="font-extrabold text-[#171717] dark:text-white">&lt; Nov 2026 &gt;</span>
              <span>⭐ ⚙️</span>
            </div>

            <div className="grid grid-cols-3 text-center my-2 text-[10px] font-bold">
              <div>
                <span className="text-[#858585]">Income</span>
                <div className="text-[#3498F3]">₹4,831.89</div>
              </div>
              <div>
                <span className="text-[#858585]">Expenses</span>
                <div className="text-[#FF665C]">₹2,442.93</div>
              </div>
              <div>
                <span className="text-[#858585]">Total</span>
                <div className="text-[#171717] dark:text-white">₹2,388.96</div>
              </div>
            </div>

            {/* Calendar Grid with Stamped Numbers */}
            <div className="grid grid-cols-7 gap-1 text-center text-[9px] font-bold mt-2">
              <span className="text-[#FF665C]">Sun</span>
              <span>Mon</span>
              <span>Tue</span>
              <span>Wed</span>
              <span>Thu</span>
              <span>Fri</span>
              <span className="text-[#3498F3]">Sat</span>

              {Array.from({ length: 28 }).map((_, d) => {
                const dayNum = d + 1;
                const isSpend = [4, 7, 11, 14, 18, 22, 28].includes(dayNum);
                const isIncome = [1, 15, 29].includes(dayNum);
                return (
                  <div key={d} className="p-1 rounded flex flex-col items-center justify-center min-h-[32px] hover:bg-black/5">
                    <span>{dayNum}</span>
                    {isIncome && <span className="text-[7px] text-[#3498F3] leading-none">+₹4k</span>}
                    {isSpend && <span className="text-[7px] text-[#FF665C] leading-none">-₹300</span>}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex justify-between text-[9px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            <span>Monthly Grid</span>
            <span>Daily Cashflow</span>
          </div>
        </div>
      ),
    },
  ];

  const handleNext = () => {
    setActiveSlide((prev) => (prev + 1) % slides.length);
  };

  const handlePrev = () => {
    setActiveSlide((prev) => (prev - 1 + slides.length) % slides.length);
  };

  return (
    <section id="screenshots" className="py-24 bg-[#F7F8FA] border-t border-[#EEEEEE] overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header with Title on Left, Light/Dark Switcher on Right */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-14 pb-4 border-b border-[#E5E5E5] gap-4">
          <div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight">
              Screenshots
            </h2>
            <p className="mt-2 text-base text-[#666666]">
              Browse through the major features of SpendWise.
            </p>
          </div>

          {/* Light / Dark Switcher */}
          <div className="flex items-center gap-6 text-sm font-bold">
            <button
              onClick={() => setThemeMode('light')}
              className={`pb-1 transition-all ${
                !isDark
                  ? 'text-[#171717] border-b-2 border-[#FF665C]'
                  : 'text-[#858585] hover:text-[#171717]'
              }`}
            >
              Light
            </button>
            <button
              onClick={() => setThemeMode('dark')}
              className={`pb-1 transition-all ${
                isDark
                  ? 'text-[#171717] border-b-2 border-[#FF665C]'
                  : 'text-[#858585] hover:text-[#171717]'
              }`}
            >
              Dark
            </button>
          </div>
        </div>

        {/* Carousel Viewport */}
        <div className="relative max-w-6xl mx-auto">
          {/* Arrow Left */}
          <button
            onClick={handlePrev}
            className="absolute -left-4 sm:-left-6 top-1/2 -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-white border border-[#EEEEEE] shadow-lg flex items-center justify-center text-[#171717] hover:bg-[#F7F8FA] hover:scale-110 hover:-translate-x-1 transition-all active:scale-95"
            aria-label="Previous Slide"
          >
            <ChevronLeft className="w-6 h-6 stroke-[2]" />
          </button>

          {/* Arrow Right */}
          <button
            onClick={handleNext}
            className="absolute -right-4 sm:-right-6 top-1/2 -translate-y-1/2 z-30 w-12 h-12 rounded-full bg-white border border-[#EEEEEE] shadow-lg flex items-center justify-center text-[#171717] hover:bg-[#F7F8FA] hover:scale-110 hover:translate-x-1 transition-all active:scale-95"
            aria-label="Next Slide"
          >
            <ChevronRight className="w-6 h-6 stroke-[2]" />
          </button>

          {/* Responsive Cards Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 items-center justify-center">
            {slides.map((s, idx) => (
              <div
                key={s.id}
                className={`rb-phone mx-auto w-full max-w-[270px] transition-all duration-300 hover:-translate-y-2.5 ${
                  activeSlide === idx ? 'scale-102 ring-2 ring-[#FF665C]/40 shadow-2xl' : 'opacity-95 hover:opacity-100 shadow-xl'
                }`}
              >
                <div className="rb-phone-notch" />
                {s.component}
              </div>
            ))}
          </div>

          {/* Pagination Dots */}
          <div className="flex justify-center items-center gap-2.5 mt-10">
            {slides.map((_, dotIdx) => (
              <button
                key={dotIdx}
                onClick={() => setActiveSlide(dotIdx)}
                className={`transition-all ${
                  activeSlide === dotIdx
                    ? 'w-7 h-2.5 rounded-full bg-[#FF665C]'
                    : 'w-2.5 h-2.5 rounded-full bg-[#D1D5DB] hover:bg-[#9CA3AF]'
                }`}
                aria-label={`Slide ${dotIdx + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
