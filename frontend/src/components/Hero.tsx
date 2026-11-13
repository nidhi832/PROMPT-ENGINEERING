import React from 'react';
import { ArrowRight, Sparkles } from 'lucide-react';

interface HeroProps {
  onGetStarted: () => void;
  onExplore: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onGetStarted, onExplore }) => {
  return (
    <section id="home" className="relative pt-28 pb-16 md:pt-36 md:pb-24 overflow-hidden realbyte-hero-bg text-white">
      {/* floating decorative background geometric icons and circles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden select-none">
        {/* Top left hollow ring */}
        <div className="absolute top-16 left-12 w-28 h-28 rounded-full border-2 border-white/35 animate-rb-drift-slow" />
        {/* Top left small solid dot */}
        <div className="absolute top-28 left-48 w-4 h-4 rounded-full bg-white/40 animate-rb-drift-medium" />
        {/* Mid left ring */}
        <div className="absolute top-80 left-20 w-16 h-16 rounded-full border border-white/25 animate-rb-drift-reverse" />
        {/* Upper center subtle halo */}
        <div className="absolute top-8 left-1/2 -translate-x-1/2 w-96 h-96 rounded-full bg-white/5 blur-2xl pointer-events-none" />
        {/* Mid right big hollow circle */}
        <div className="absolute top-36 right-16 w-52 h-52 rounded-full border-2 border-white/20 animate-rb-drift-medium" />
        {/* Bottom right floating ring */}
        <div className="absolute bottom-16 right-36 w-36 h-36 rounded-full border-2 border-white/25 animate-rb-drift-slow" />
        {/* Floating small circles near right phone */}
        <div className="absolute top-64 right-1/3 w-6 h-6 rounded-full bg-white/30 animate-rb-drift-reverse" />
        <div className="absolute bottom-32 right-1/4 w-8 h-8 rounded-full border border-white/40 animate-rb-drift-medium" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-8 items-center">
          {/* Left Column: Title & call to action */}
          <div className="lg:col-span-5 text-center lg:text-left pt-4 lg:pt-0">
            {/* Cursive handwritten style */}
            <div className="font-cursive text-3xl sm:text-4xl text-white/95 -rotate-2 origin-left inline-block mb-1">
              The easiest way
            </div>
            
            <div className="text-xl sm:text-2xl text-white/95 font-medium tracking-tight">
              to manage personal finances
            </div>

            {/* Giant Brand Name */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-extrabold text-white tracking-tight mt-1 mb-6">
              SpendWise
            </h1>

            <p className="text-white/85 text-base sm:text-lg max-w-md mx-auto lg:mx-0 leading-relaxed mb-8">
              Track expenses, manage budgets, understand your spending patterns, and make smarter financial decisions — all in one place.
            </p>

            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-4 mb-8">
              <button
                onClick={onGetStarted}
                className="px-6 py-3 rounded-xl bg-white text-[#FF665C] font-bold shadow-lg shadow-black/20 hover:scale-105 transition-all active:scale-95"
              >
                Try the live demo
              </button>
            </div>

            {/* Quick Feature Badges */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-2 text-xs">
              <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-xs font-semibold">
                ✓ Course project prototype
              </span>
              <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-xs font-semibold">
                ✓ Synthetic demo data
              </span>
              <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-xs font-semibold">
                ✓ Not financial advice
              </span>
            </div>
          </div>

          {/* Right Column: 3-Phones Moving Fan Display */}
          <div className="lg:col-span-7 relative flex items-center justify-center pt-6 lg:pt-0">
            <div className="relative flex items-center justify-center w-full max-w-2xl">
              
              {/* Phone 1 (Left - Tilted Splash Screen with gentle float) */}
              <div className="hidden sm:block absolute -left-4 sm:left-2 lg:left-0 z-10 w-52 sm:w-60 animate-rb-float-left">
                <div className="rb-phone">
                  <div className="rb-phone-notch" />
                  <div className="rb-phone-screen h-[420px] bg-gradient-to-b from-[#FF665C] to-[#EE5253] flex flex-col items-center justify-between p-6 text-white text-center">
                    <div className="pt-8">
                      <div className="text-[10px] tracking-widest uppercase font-bold text-white/80">SpendWise</div>
                    </div>
                    {/* Cute Piggy Emblem with gentle breathing pulse */}
                    <div className="flex flex-col items-center">
                      <div className="w-20 h-20 rounded-3xl bg-white text-[#FF665C] flex items-center justify-center text-4xl shadow-xl shadow-black/15 animate-rb-piggy">
                        🐷
                      </div>
                      <div className="mt-4 font-extrabold text-lg text-white">SpendWise</div>
                      <div className="text-[11px] text-white/80">Money Manager</div>
                    </div>
                    <div className="text-[10px] tracking-widest font-bold text-white/70 pb-2">
                      Prototype UI
                    </div>
                  </div>
                </div>
              </div>

              {/* Phone 2 (Center - Prominent Front Daily Transaction Ledger with gentle vertical float) */}
              <div className="relative z-30 w-64 sm:w-72 shadow-2xl animate-rb-float">
                <div className="rb-phone border-4 border-black/80">
                  <div className="rb-phone-notch" />
                  <div className="rb-phone-screen bg-white text-[#171717] h-[480px] flex flex-col justify-between overflow-hidden">
                    {/* Header */}
                    <div className="pt-7 px-4 pb-2 border-b border-[#EEEEEE]">
                      <div className="flex items-center justify-between text-xs font-bold text-[#858585] mb-2">
                        <span>🔍</span>
                        <span className="text-[#171717] font-extrabold">&lt; Nov 2026 &gt;</span>
                        <span>⭐ ⚙️</span>
                      </div>

                      {/* Tabs */}
                      <div className="flex items-center justify-between text-[11px] font-bold text-[#858585] pt-1">
                        <span className="text-[#FF665C] border-b-2 border-[#FF665C] pb-1">Daily</span>
                        <span>Calendar</span>
                        <span>Weekly</span>
                        <span>Monthly</span>
                        <span>Summary</span>
                      </div>
                    </div>

                    {/* Summary Bar */}
                    <div className="bg-[#FAFAFA] px-4 py-2 border-b border-[#EEEEEE] grid grid-cols-3 text-center">
                      <div>
                        <div className="text-[9px] font-bold uppercase text-[#858585]">Income</div>
                        <div className="text-xs font-extrabold text-[#3498F3]">₹85,000</div>
                      </div>
                      <div>
                        <div className="text-[9px] font-bold uppercase text-[#858585]">Expenses</div>
                        <div className="text-xs font-extrabold text-[#FF665C]">₹42,860</div>
                      </div>
                      <div>
                        <div className="text-[9px] font-bold uppercase text-[#858585]">Total</div>
                        <div className="text-xs font-extrabold text-[#171717]">₹42,140</div>
                      </div>
                    </div>

                    {/* Daily Ledger List */}
                    <div className="p-3 space-y-2.5 overflow-hidden flex-1 text-xs">
                      {/* 12 Nov */}
                      <div>
                        <div className="flex justify-between items-center text-[10px] font-bold text-[#858585] mb-1">
                          <span className="bg-[#EEEEEE] px-1.5 py-0.5 rounded text-[#171717]">12 Wed</span>
                          <span className="text-[#3498F3]">+₹85,000.00</span>
                        </div>
                        <div className="flex justify-between items-center py-1 border-b border-[#F5F5F5]">
                          <div>
                            <div className="font-bold text-[#171717]">Monthly Salary Credit</div>
                            <div className="text-[10px] text-[#858585]">Salary • Salary Account</div>
                          </div>
                          <span className="font-extrabold text-[#3498F3]">+₹85,000</span>
                        </div>
                      </div>

                      {/* 11 Nov */}
                      <div>
                        <div className="flex justify-between items-center text-[10px] font-bold text-[#858585] mb-1">
                          <span className="bg-[#EEEEEE] px-1.5 py-0.5 rounded text-[#171717]">11 Tue</span>
                          <span className="text-[#FF665C]">-₹7,730.00</span>
                        </div>
                        <div className="space-y-1">
                          <div className="flex justify-between items-center py-0.5">
                            <div>
                              <div className="font-bold text-[#171717]">IKEA Work Desk</div>
                              <div className="text-[10px] text-[#858585]">Shopping • Credit Card</div>
                            </div>
                            <span className="font-extrabold text-[#FF665C]">-₹6,450</span>
                          </div>
                          <div className="flex justify-between items-center py-0.5">
                            <div>
                              <div className="font-bold text-[#171717]">Swiggy Gourmet Dinner</div>
                              <div className="text-[10px] text-[#858585]">Food • UPI</div>
                            </div>
                            <span className="font-extrabold text-[#FF665C]">-₹1,280</span>
                          </div>
                        </div>
                      </div>

                      {/* 10 Nov */}
                      <div>
                        <div className="flex justify-between items-center text-[10px] font-bold text-[#858585] mb-1">
                          <span className="bg-[#EEEEEE] px-1.5 py-0.5 rounded text-[#171717]">10 Mon</span>
                          <span className="text-[#FF665C]">-₹850.00</span>
                        </div>
                        <div className="flex justify-between items-center py-0.5">
                          <div>
                            <div className="font-bold text-[#171717]">Uber Premier Airport</div>
                            <div className="text-[10px] text-[#858585]">Transport • UPI</div>
                          </div>
                          <span className="font-extrabold text-[#FF665C]">-₹850</span>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Nav on Phone */}
                    <div className="bg-[#FAFAFA] border-t border-[#EEEEEE] px-4 py-2 flex justify-between text-[10px] text-[#858585] font-bold">
                      <span className="text-[#FF665C]">Ledger</span>
                      <span>Stats</span>
                      <span>Accounts</span>
                      <span>Settings</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Phone 3 (Right - Tilted Dark Mode Stats Screen with delayed float) */}
              <div className="hidden sm:block absolute -right-4 sm:right-2 lg:right-0 z-10 w-52 sm:w-60 animate-rb-float-delayed">
                <div className="rb-phone">
                  <div className="rb-phone-notch" />
                  <div className="rb-phone-screen h-[420px] bg-[#18181B] text-white flex flex-col justify-between p-4 overflow-hidden">
                    <div className="pt-6">
                      <div className="flex justify-between text-xs font-bold text-white/70 mb-2">
                        <span className="text-[#FF665C] border-b border-[#FF665C] pb-0.5">Stats</span>
                        <span>Budget</span>
                        <span>Note</span>
                      </div>
                      <div className="text-center my-3">
                        <div className="text-[10px] text-white/60">Expenses: ₹42,860.00</div>
                        {/* Mini Circular Wedge Representation */}
                        <div className="w-24 h-24 mx-auto my-2 rounded-full border-4 border-[#FF665C] border-t-[#3498F3] border-r-[#FF78B9] border-l-[#FFA502] flex items-center justify-center animate-spin" style={{ animationDuration: '30s' }}>
                          <span className="text-[10px] font-extrabold">Nov</span>
                        </div>
                      </div>
                    </div>

                    {/* Category List */}
                    <div className="space-y-1.5 text-[10px]">
                      <div className="flex justify-between items-center p-1 rounded bg-white/5">
                        <span className="text-[#FF665C] font-bold">● Food & Dining</span>
                        <span>33.2% • ₹14,250</span>
                      </div>
                      <div className="flex justify-between items-center p-1 rounded bg-white/5">
                        <span className="text-[#FF78B9] font-bold">● Shopping</span>
                        <span>20.8% • ₹8,900</span>
                      </div>
                      <div className="flex justify-between items-center p-1 rounded bg-white/5">
                        <span className="text-[#FFA502] font-bold">● Bills</span>
                        <span>18.3% • ₹7,850</span>
                      </div>
                      <div className="flex justify-between items-center p-1 rounded bg-white/5">
                        <span className="text-[#3498F3] font-bold">● Transport</span>
                        <span>10.5% • ₹4,500</span>
                      </div>
                    </div>

                    <div className="text-center text-[9px] text-white/50 pt-2 border-t border-white/10">
                      Prototype UI
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
