import React from 'react';
import { ExternalLink, HelpCircle, BookOpen, MessageCircle } from 'lucide-react';

interface HelpCenterProps {
  onOpenDashboard: () => void;
}

export const HelpCenter: React.FC<HelpCenterProps> = ({ onOpenDashboard }) => {
  return (
    <section id="help-center" className="py-24 bg-white border-t border-[#EEEEEE]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-[#171717] tracking-tight">
            Help Center
          </h2>
          <p className="mt-3 text-base text-[#666666]">
            Need to ask us how to use? Simply get in touch with us.
          </p>
        </div>

        {/* Desktop Monitor & Text Two-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center max-w-6xl mx-auto">
          {/* Left: Desktop Monitor Mockup */}
          <div className="lg:col-span-7">
            <div className="rb-monitor">
              <div className="rb-monitor-screen bg-[#F7F8FA] p-4 text-[#171717]">
                <div className="flex items-center justify-between pb-3 border-b border-[#EEEEEE] mb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F56]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#27C93F]" />
                    <span className="text-xs font-bold text-[#858585] ml-2">
                      SpendWise PC Web Manager
                    </span>
                  </div>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-[#3498F3]/10 text-[#3498F3]">
                    Connected via Localhost
                  </span>
                </div>

                <div className="bg-white rounded-xl p-4 border border-[#EEEEEE] shadow-xs">
                  <div className="flex justify-between items-center mb-3">
                    <div className="text-sm font-bold">Knowledge Base &amp; Tutorials</div>
                    <span className="text-xs text-[#FF665C] font-semibold">Project docs</span>
                  </div>
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    <div className="p-3 rounded-lg border border-[#EEEEEE] bg-[#FAFAFA]">
                      <div className="font-bold text-[#171717] mb-1">CSV Import Guide</div>
                      <div className="text-[11px] text-[#858585]">Columns, date formats and validation</div>
                    </div>
                    <div className="p-3 rounded-lg border border-[#EEEEEE] bg-[#FAFAFA]">
                      <div className="font-bold text-[#171717] mb-1">Prompt Lab Guide</div>
                      <div className="text-[11px] text-[#858585]">Reading the evaluation results</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="rb-monitor-stand" />
            <div className="rb-monitor-base" />
          </div>

          {/* Right: Text & Action Button */}
          <div className="lg:col-span-5 text-center lg:text-left">
            <h3 className="text-2xl sm:text-3xl font-extrabold text-[#171717] tracking-tight mb-3">
              SpendWise Help Center
            </h3>
            <p className="text-base text-[#666666] leading-relaxed mb-8">
              You can find out regular updates, user manuals, and prompt engineering architecture breakdowns.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
              <a
                href="#dashboard-preview"
                onClick={onOpenDashboard}
                className="inline-flex items-center gap-2.5 px-6 py-3 rounded-xl border border-[#DDDDDD] bg-white hover:bg-[#F7F8FA] text-[#171717] text-sm font-bold shadow-xs hover:border-[#FF665C] hover:shadow-md transition-all group"
              >
                <div className="w-6 h-6 rounded-lg bg-[#FF665C] text-white flex items-center justify-center text-xs group-hover:scale-110 group-hover:rotate-12 transition-transform">
                  🐷
                </div>
                <span>Help Center</span>
              </a>

              <a
                href="https://github.com/nidhi832/PROMPT-ENGINEERING"
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#666666] hover:text-[#FF665C] transition-colors"
              >
                <span>GitHub Readme</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
