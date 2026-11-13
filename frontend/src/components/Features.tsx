import React, { useState, useEffect } from 'react';
import { 
  UploadCloud, 
  Tag, 
  BarChart3, 
  MessageSquare, 
  Target, 
  FileText,
  CheckCircle2,
  AlertTriangle,
  Bot,
  Sparkles,
  Download
} from 'lucide-react';

export const Features: React.FC = () => {
  const [activeFeature, setActiveFeature] = useState(0);
  const [isPaused, setIsPaused] = useState(false);

  // Auto rotate features every 4.5 seconds for attractive dynamic movement
  useEffect(() => {
    if (isPaused) return;
    const timer = setInterval(() => {
      setActiveFeature((prev) => (prev + 1) % 6);
    }, 4500);
    return () => clearInterval(timer);
  }, [isPaused]);

  const features = [
    {
      id: 0,
      title: 'Expense Import',
      desc: 'Upload CSV containing date, description & amount; preview and validate rows',
      icon: <UploadCloud className="w-7 h-7" />,
      animClass: 'animate-rb-icon-1',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1">Feature 1: Expense Import</div>
            <div className="p-3 rounded-xl bg-[#F7F8FA] border border-[#EEEEEE] mb-2.5">
              <div className="flex items-center justify-between mb-1.5 text-[10px] font-bold text-[#858585]">
                <span>CSV File Upload</span>
                <span className="text-[#2ED573] flex items-center gap-1 font-bold">
                  <CheckCircle2 className="w-3 h-3" /> Validated
                </span>
              </div>
              <div className="text-sm font-extrabold text-[#171717]">sample_expenses.csv</div>
              <div className="text-[10px] text-[#858585] mt-0.5">38 rows detected • 0 invalid rows</div>
            </div>

            <div className="p-2.5 rounded-xl bg-white border border-[#EEEEEE] space-y-1.5 text-[10px]">
              <div className="font-bold text-[#171717]">Auto-Detected Columns:</div>
              <div className="flex flex-wrap gap-1">
                <span className="px-2 py-0.5 rounded bg-[#3498F3]/10 text-[#3498F3] font-bold">date ✓</span>
                <span className="px-2 py-0.5 rounded bg-[#3498F3]/10 text-[#3498F3] font-bold">description ✓</span>
                <span className="px-2 py-0.5 rounded bg-[#3498F3]/10 text-[#3498F3] font-bold">amount ✓</span>
              </div>
              <div className="text-[9px] text-[#858585] pt-1 border-t border-[#EEEEEE]">
                Normalizes descriptions and handles missing fields cleanly.
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            🔒 Session-only parsing • Never stores banking passwords
          </div>
        </div>
      ),
    },
    {
      id: 1,
      title: 'Smart Categorization',
      desc: 'Zero-shot and few-shot classification into 6 categories with review flags',
      icon: <Tag className="w-7 h-7" />,
      animClass: 'animate-rb-icon-2',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1">Feature 2: Smart Categorization</div>
            <div className="space-y-1.5 mb-2">
              <div className="p-2 rounded-lg bg-[#F7F8FA] border border-[#EEEEEE] flex justify-between items-center">
                <div>
                  <div className="font-bold text-xs">Swiggy Gourmet</div>
                  <div className="text-[9px] text-[#858585]">Confidence: 0.95</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-[#FF665C]/15 text-[#FF665C] font-bold text-[10px]">
                  🍔 Food
                </span>
              </div>
              <div className="p-2 rounded-lg bg-[#F7F8FA] border border-[#EEEEEE] flex justify-between items-center">
                <div>
                  <div className="font-bold text-xs">Uber to Airport</div>
                  <div className="text-[9px] text-[#858585]">Confidence: 0.91</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-[#3498F3]/15 text-[#3498F3] font-bold text-[10px]">
                  🚗 Transport
                </span>
              </div>
              <div className="p-2 rounded-lg bg-[#FFF8E7] border border-[#FFEAA7] flex justify-between items-center">
                <div>
                  <div className="font-bold text-xs text-[#D68100]">Amazon Marketplace</div>
                  <div className="text-[9px] text-[#D68100]">Ambiguous Merchant</div>
                </div>
                <span className="px-1.5 py-0.5 rounded bg-[#D68100] text-white font-bold text-[9px] flex items-center gap-0.5">
                  <AlertTriangle className="w-2.5 h-2.5" /> Review
                </span>
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            Zero-shot &amp; Few-shot Prompts • Pydantic Schema Validated
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: 'Spending Analysis',
      desc: 'Category & monthly totals with charts; arithmetic computed in Python',
      icon: <BarChart3 className="w-7 h-7" />,
      animClass: 'animate-rb-icon-3',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1 text-center">Feature 3: Spending Analysis</div>
            <div className="w-24 h-24 mx-auto my-1.5 rounded-full border-4 border-[#FF665C] border-t-[#3498F3] border-r-[#FF78B9] border-l-[#FFA502] flex items-center justify-center animate-spin" style={{ animationDuration: '24s' }}>
              <span className="text-[10px] font-extrabold">₹42.8k</span>
            </div>
            <div className="space-y-1 text-[10px]">
              <div className="flex justify-between py-0.5">
                <span className="text-[#FF665C] font-bold">🍔 Food &amp; Dining</span>
                <span>33.2% (₹14,250)</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-[#FF78B9] font-bold">🛍️ Shopping</span>
                <span>20.8% (₹8,900)</span>
              </div>
              <div className="flex justify-between py-0.5">
                <span className="text-[#FFA502] font-bold">🧾 Bills &amp; Rent</span>
                <span>18.3% (₹7,850)</span>
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-[#2ED573] font-bold pt-2 border-t border-[#EEEEEE]">
            ✓ Arithmetic performed by Python, not guessed by LLM
          </div>
        </div>
      ),
    },
    {
      id: 3,
      title: 'Ask SpendWise',
      desc: 'Ask questions in natural language; grounded answers verified against data',
      icon: <MessageSquare className="w-7 h-7" />,
      animClass: 'animate-rb-icon-4',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1.5">Feature 4: Ask SpendWise</div>
            {/* User message */}
            <div className="bg-[#F7F8FA] p-2 rounded-xl border border-[#EEEEEE] mb-2 text-right">
              <span className="text-[9px] text-[#858585] block font-semibold mb-0.5">You asked:</span>
              <p className="font-bold text-[#171717] text-[11px]">"How much did I spend on food in October?"</p>
            </div>
            {/* Assistant message */}
            <div className="bg-white p-2.5 rounded-xl border border-[#FF665C]/30 shadow-xs mb-1">
              <div className="flex items-center gap-1 text-[9px] text-[#FF665C] font-bold mb-1">
                <Bot className="w-3 h-3" /> SpendWise Assistant
              </div>
              <p className="text-[11px] text-[#171717] leading-relaxed">
                You spent <b>₹14,250.00</b> on Food across 18 transactions in October 2026.
              </p>
              <div className="mt-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#2ED573]/10 text-[#2ED573] text-[9px] font-bold">
                ✓ Grounded · 1 figure verified against Python data
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            Query router parses intent • Zero hallucinations
          </div>
        </div>
      ),
    },
    {
      id: 4,
      title: 'Budget Suggestions',
      desc: 'Enter a monthly budget or savings goal and receive grounded suggestions',
      icon: <Target className="w-7 h-7" />,
      animClass: 'animate-rb-icon-5',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1.5">Feature 5: Budget Suggestions</div>
            <div className="p-2.5 rounded-xl bg-[#F7F8FA] border border-[#EEEEEE] mb-2">
              <div className="flex justify-between items-center text-[10px]">
                <span className="text-[#858585] font-bold">Monthly Budget Goal</span>
                <span className="font-extrabold text-[#171717]">₹38,000 / mo</span>
              </div>
              <div className="w-full h-1.5 bg-black/10 rounded-full mt-1.5 overflow-hidden">
                <div className="h-full bg-[#FF665C] rounded-full" style={{ width: '88%' }} />
              </div>
            </div>

            <div className="space-y-1.5 text-[10px]">
              <div className="p-1.5 rounded-lg bg-white border border-[#EEEEEE]">
                <span className="font-bold text-[#171717]">💡 Plan 2 Home-Cooked Days</span>
                <p className="text-[#666666] text-[9px] mt-0.5">Swap food delivery orders to save ~₹2,500/mo.</p>
              </div>
              <div className="p-1.5 rounded-lg bg-white border border-[#EEEEEE]">
                <span className="font-bold text-[#171717]">🚗 Metro over Short Cabs</span>
                <p className="text-[#666666] text-[9px] mt-0.5">Public transport covers office route for less (~₹1,200/mo).</p>
              </div>
            </div>
          </div>
          <div className="text-center text-[10px] text-[#858585] pt-2 border-t border-[#EEEEEE]">
            Constrained prompt generates practical, verified advice
          </div>
        </div>
      ),
    },
    {
      id: 5,
      title: 'Monthly Report',
      desc: 'Generate a structured JSON summary with category totals & next steps',
      icon: <FileText className="w-7 h-7" />,
      animClass: 'animate-rb-icon-6',
      preview: (
        <div className="p-3 text-xs flex flex-col justify-between h-full">
          <div>
            <div className="text-[10px] uppercase font-bold text-[#FF665C] mb-1.5">Feature 6: Monthly Report</div>
            <div className="p-2.5 rounded-xl bg-[#F7F8FA] border border-[#EEEEEE] mb-2">
              <span className="text-[9px] uppercase font-bold text-[#858585]">October 2026 Statement</span>
              <div className="text-xs font-extrabold text-[#171717] mt-0.5">₹42,860.00 spent, led by Food &amp; Dining</div>
            </div>

            <div className="space-y-1 text-[10px] bg-white p-2 rounded-xl border border-[#EEEEEE]">
              <div className="font-bold text-[#171717] mb-1">Key Observations:</div>
              <div className="text-[#666666] text-[9px] leading-tight">• 38 transactions across 6 categories</div>
              <div className="text-[#666666] text-[9px] leading-tight">• Largest single spend: ₹6,450 (Work Desk)</div>
              <div className="text-[#666666] text-[9px] leading-tight">• Savings rate achieved: 49.5%</div>
            </div>
          </div>
          <div className="pt-2 border-t border-[#EEEEEE] flex justify-between text-[9px] font-bold text-[#FF665C]">
            <span>⬇️ Markdown Export</span>
            <span>⬇️ Structured JSON</span>
          </div>
        </div>
      ),
    },
  ];

  const leftFeatures = features.slice(0, 3);
  const rightFeatures = features.slice(3, 6);

  return (
    <section 
      id="features" 
      className="py-24 bg-white overflow-hidden relative"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 sm:mb-20">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#FFF5F4] text-[11px] font-bold text-[#FF665C] mb-3">
            <Sparkles className="w-3.5 h-3.5" /> PROPOSED WORKFLOW &amp; CORE FEATURES
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight">
            Everything you need to manage your money.
          </h2>
          <p className="mt-3 text-base text-[#666666]">
            The 6 core prompt engineering features from the SpendWise Project Plan.
          </p>
        </div>

        {/* Centered Phone Layout with 3 Left and 3 Right Items */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-6 items-center max-w-6xl mx-auto">
          
          {/* Left Column (Features 1 to 3) */}
          <div className="lg:col-span-4 flex flex-col gap-10 lg:gap-14 text-center lg:text-right">
            {leftFeatures.map((f) => {
              const isActive = activeFeature === f.id;
              return (
                <div
                  key={f.id}
                  onClick={() => setActiveFeature(f.id)}
                  onMouseEnter={() => {
                    setActiveFeature(f.id);
                    setIsPaused(true);
                  }}
                  className="flex flex-col lg:flex-row-reverse items-center gap-4 cursor-pointer group transition-all"
                >
                  {/* Moving Animated Icon Circle */}
                  <div
                    className={`w-16 h-16 sm:w-20 sm:h-20 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                      isActive
                        ? 'bg-[#FF665C] text-white shadow-xl shadow-[#FF665C]/45 scale-110 animate-rb-pulse-ring'
                        : `border-2 border-[#E2E8F0] text-[#333333] bg-white group-hover:border-[#FF665C] group-hover:text-[#FF665C] group-hover:scale-105 shadow-sm ${f.animClass}`
                    }`}
                  >
                    <div className={isActive ? 'animate-rb-icon-active' : ''}>
                      {f.icon}
                    </div>
                  </div>
                  <div>
                    <h3 className={`text-lg font-bold mb-1 transition-colors ${
                      isActive ? 'text-[#FF665C]' : 'text-[#171717] group-hover:text-[#FF665C]'
                    }`}>
                      {f.title}
                    </h3>
                    <p className="text-xs sm:text-sm text-[#666666] max-w-xs mx-auto lg:mx-0 leading-relaxed">
                      {f.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Center Column: Phone Mockup that dynamically changes with active feature */}
          <div className="lg:col-span-4 flex justify-center py-4">
            <div className="w-64 sm:w-72 shadow-2xl relative">
              <div className="rb-phone">
                <div className="rb-phone-notch" />
                <div className="rb-phone-screen bg-white text-[#171717] h-[490px] flex flex-col justify-between overflow-hidden">
                  {/* Top Bar */}
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

                  {/* Dynamic Active Feature Screen Container */}
                  <div className="flex-1 overflow-hidden transition-all duration-300">
                    {features[activeFeature].preview}
                  </div>

                  {/* Phone Bottom Tabs */}
                  <div className="bg-[#FAFAFA] border-t border-[#EEEEEE] px-4 py-2 flex justify-between text-[10px] text-[#858585] font-bold">
                    <span className="text-[#FF665C]">SpendWise</span>
                    <span>Analytics</span>
                    <span>Assistant</span>
                    <span>Report</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column (Features 4 to 6) */}
          <div className="lg:col-span-4 flex flex-col gap-10 lg:gap-14 text-center lg:text-left">
            {rightFeatures.map((f) => {
              const isActive = activeFeature === f.id;
              return (
                <div
                  key={f.id}
                  onClick={() => setActiveFeature(f.id)}
                  onMouseEnter={() => {
                    setActiveFeature(f.id);
                    setIsPaused(true);
                  }}
                  className="flex flex-col lg:flex-row items-center gap-4 cursor-pointer group transition-all"
                >
                  {/* Moving Animated Icon Circle */}
                  <div
                    className={`w-16 h-16 sm:w-20 sm:h-20 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 ${
                      isActive
                        ? 'bg-[#FF665C] text-white shadow-xl shadow-[#FF665C]/45 scale-110 animate-rb-pulse-ring'
                        : `border-2 border-[#E2E8F0] text-[#333333] bg-white group-hover:border-[#FF665C] group-hover:text-[#FF665C] group-hover:scale-105 shadow-sm ${f.animClass}`
                    }`}
                  >
                    <div className={isActive ? 'animate-rb-icon-active' : ''}>
                      {f.icon}
                    </div>
                  </div>
                  <div>
                    <h3 className={`text-lg font-bold mb-1 transition-colors ${
                      isActive ? 'text-[#FF665C]' : 'text-[#171717] group-hover:text-[#FF665C]'
                    }`}>
                      {f.title}
                    </h3>
                    <p className="text-xs sm:text-sm text-[#666666] max-w-xs mx-auto lg:mx-0 leading-relaxed">
                      {f.desc}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>

        </div>
      </div>
    </section>
  );
};
