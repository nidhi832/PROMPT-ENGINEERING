import React from 'react';
import { PenLine, BarChart3, TrendingUp, ArrowRight } from 'lucide-react';

export const HowItWorks: React.FC = () => {
  const steps = [
    {
      num: '01',
      title: 'Track',
      subtitle: 'Record your income and expenses.',
      description: 'Log daily spending across bank accounts, cards, and cash in seconds. Fast manual entry with smart category auto-mapping.',
      icon: <PenLine className="w-6 h-6 text-[#FF665C]" />,
      pill: 'Double-Entry',
    },
    {
      num: '02',
      title: 'Analyze',
      subtitle: 'Understand where your money goes.',
      description: 'Explore interactive monthly category breakdowns, donut distribution charts, and velocity graphs to pinpoint leaks.',
      icon: <BarChart3 className="w-6 h-6 text-[#3498F3]" />,
      pill: 'Visual Insights',
    },
    {
      num: '03',
      title: 'Improve',
      subtitle: 'Set budgets and achieve your financial goals.',
      description: 'Establish category spending ceilings, monitor utilization gauges, and build consistent long-term wealth habits.',
      icon: <TrendingUp className="w-6 h-6 text-[#2ED573]" />,
      pill: 'Budget Goals',
    },
  ];

  return (
    <section id="how-it-works" className="py-20 bg-[#F7F8FA] border-t border-[#EEEEEE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-[#EEEEEE] text-[12px] font-bold text-[#FF665C] mb-3">
            HOW IT WORKS
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight">
            Managing money doesn't have to be complicated.
          </h2>
          <p className="mt-3 text-base sm:text-lg text-[#666666]">
            Three straightforward steps to transform chaos into clear financial control.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="bg-white rounded-3xl p-8 border border-[#EEEEEE] shadow-xs hover:border-[#DDDDDD] hover:shadow-realbyte-hover hover:-translate-y-1 transition-all duration-200 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-6">
                  <span className="text-3xl font-black text-[#FF665C]/20 group-hover:text-[#FF665C] transition-colors">
                    {step.num}
                  </span>
                  <div className="w-12 h-12 rounded-2xl bg-[#F7F8FA] flex items-center justify-center group-hover:bg-[#FFF5F4] transition-colors">
                    {step.icon}
                  </div>
                </div>

                <div className="inline-block text-[11px] font-bold uppercase tracking-wider text-[#FF665C] mb-1">
                  Step {idx + 1} • {step.pill}
                </div>
                <h3 className="text-xl font-bold text-[#171717] mb-2">{step.title}</h3>
                <h4 className="text-sm font-semibold text-[#555555] mb-3">{step.subtitle}</h4>
                <p className="text-xs text-[#666666] leading-relaxed">
                  {step.description}
                </p>
              </div>

              {/* Step indicator footer */}
              <div className="mt-8 pt-4 border-t border-[#F2F2F2] flex items-center justify-between text-xs font-bold text-[#858585] group-hover:text-[#171717]">
                <span>Phase {step.num}</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
