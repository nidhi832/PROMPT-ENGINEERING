import React from 'react';
import { Wallet, Heart, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer id="about" className="bg-white border-t border-[#EEEEEE] pt-16 pb-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 pb-12 border-b border-[#EEEEEE]">
          {/* Col 1 & 2: Brand Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center gap-2.5 mb-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#FF665C] to-[#FF857D] flex items-center justify-center text-white shadow-md shadow-[#FF665C]/25">
                <Wallet className="w-5 h-5 stroke-[2.2]" />
              </div>
              <span className="font-extrabold text-xl tracking-tight text-[#171717]">
                SpendWise
              </span>
            </div>
            <p className="text-xs sm:text-sm text-[#666666] max-w-sm leading-relaxed mb-4">
              An intelligent personal-finance assistant built on prompt engineering, automated prompt optimization, and double-entry bookkeeping inspired by RealByte Money Manager.
            </p>
            <div className="flex items-center gap-2 text-xs text-[#858585]">
              <span>Course: Prompt Engineering &amp; Optimization for GenAI</span>
            </div>
          </div>

          {/* Col 3: Product */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#171717] mb-4">
              Product
            </h4>
            <ul className="space-y-2.5 text-xs text-[#666666]">
              <li><a href="#home" className="hover:text-[#FF665C] transition-colors">Overview</a></li>
              <li><a href="#dashboard-preview" className="hover:text-[#FF665C] transition-colors">Interactive Dashboard</a></li>
              <li><a href="#product-showcase" className="hover:text-[#FF665C] transition-colors">Daily Ledger View</a></li>
              <li><a href="#product-showcase" className="hover:text-[#FF665C] transition-colors">Budget Management</a></li>
              <li><a href="#product-showcase" className="hover:text-[#FF665C] transition-colors">Financial Reports</a></li>
            </ul>
          </div>

          {/* Col 4: Features */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#171717] mb-4">
              Features
            </h4>
            <ul className="space-y-2.5 text-xs text-[#666666]">
              <li><a href="#features" className="hover:text-[#FF665C] transition-colors">Expense Tracking</a></li>
              <li><a href="#features" className="hover:text-[#FF665C] transition-colors">Category Limits</a></li>
              <li><a href="#features" className="hover:text-[#FF665C] transition-colors">Income vs Expenses</a></li>
              <li><a href="#features" className="hover:text-[#FF665C] transition-colors">Grounded AI Explanations</a></li>
              <li><a href="#features" className="hover:text-[#FF665C] transition-colors">Prompt Optimizer Lab</a></li>
            </ul>
          </div>

          {/* Col 5: Help & Legal */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-[#171717] mb-4">
              Support &amp; Legal
            </h4>
            <ul className="space-y-2.5 text-xs text-[#666666]">
              <li><a href="https://www.realbyteapps.com" target="_blank" rel="noreferrer" className="hover:text-[#FF665C] transition-colors inline-flex items-center gap-1">RealByte Reference <ExternalLink className="w-3 h-3" /></a></li>
              <li><a href="https://github.com/nidhi832/PROMPT-ENGINEERING" target="_blank" rel="noreferrer" className="hover:text-[#FF665C] transition-colors inline-flex items-center gap-1">GitHub Repository <ExternalLink className="w-3 h-3" /></a></li>
              <li><span className="text-[#858585]">Privacy Policy (Client-Side)</span></li>
              <li><span className="text-[#858585]">Terms of Service</span></li>
              <li><span className="text-[#858585]">Educational Use Disclaimer</span></li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-[#858585]">
          <div>
            © {new Date().getFullYear()} SpendWise. All rights reserved. Educational personal-finance assistant, not financial advice.
          </div>
          <div className="flex items-center gap-1">
            <span>Crafted with</span>
            <Heart className="w-3.5 h-3.5 text-[#FF665C] fill-[#FF665C]" />
            <span>inspired by RealByte Money Manager design system.</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
