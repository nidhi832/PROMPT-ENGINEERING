import React from 'react';
import { Star, Quote, CheckCircle2 } from 'lucide-react';
import { TESTIMONIALS } from '../data/mockData';

export const Testimonials: React.FC = () => {
  return (
    <section className="py-20 bg-white border-t border-[#EEEEEE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FFF5F4] text-[12px] font-bold text-[#FF665C] mb-3">
            USER STORIES
          </div>
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight">
            Loved by Students &amp; Working Professionals
          </h2>
          <p className="mt-3 text-base sm:text-lg text-[#666666]">
            See how everyday users turn complex personal finances into effortless clarity.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {TESTIMONIALS.map((t, idx) => (
            <div
              key={idx}
              className="bg-white rounded-3xl p-7 border border-[#EEEEEE] shadow-xs hover:border-[#DDDDDD] hover:shadow-realbyte-hover hover:-translate-y-1 transition-all duration-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-5">
                  {/* Star Rating */}
                  <div className="flex items-center gap-1">
                    {Array.from({ length: t.rating }).map((_, sIdx) => (
                      <Star key={sIdx} className="w-4 h-4 fill-[#FFA502] text-[#FFA502]" />
                    ))}
                  </div>
                  <Quote className="w-5 h-5 text-[#CCCCCC]" />
                </div>

                <p className="text-sm text-[#444444] leading-relaxed mb-6 font-medium italic">
                  "{t.quote}"
                </p>
              </div>

              <div className="pt-5 border-t border-[#F2F2F2] flex items-center gap-3.5">
                <img
                  src={t.avatar}
                  alt={t.name}
                  className="w-11 h-11 rounded-full object-cover border border-[#EEEEEE]"
                />
                <div>
                  <div className="text-sm font-bold text-[#171717] flex items-center gap-1.5">
                    <span>{t.name}</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#2ED573]" />
                  </div>
                  <div className="text-xs text-[#858585]">{t.role}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Demo Disclaimer */}
        <div className="text-center mt-10 text-[11px] text-[#999999]">
          * Illustrative demo testimonials presented for product preview purposes.
        </div>
      </div>
    </section>
  );
};
