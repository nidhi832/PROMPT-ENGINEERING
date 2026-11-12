import React, { useState } from 'react';
import { X, Wallet, ArrowRight, ShieldCheck } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  mode: 'signin' | 'signup';
  onClose: () => void;
  onSuccess: (email: string) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, mode, onClose, onSuccess }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [currentMode, setCurrentMode] = useState<'signin' | 'signup'>(mode);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;
    onSuccess(email);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-200">
      <div className="bg-white rounded-3xl p-7 max-w-md w-full border border-[#EEEEEE] shadow-2xl relative">
        <button
          onClick={onClose}
          className="absolute right-5 top-5 p-1 rounded-full text-[#858585] hover:text-[#171717] hover:bg-[#F7F8FA]"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#FF665C] to-[#FF857D] flex items-center justify-center text-white shadow-md shadow-[#FF665C]/25">
            <Wallet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-[#171717]">
              {currentMode === 'signin' ? 'Welcome Back to SpendWise' : 'Create Your Free Account'}
            </h3>
            <p className="text-xs text-[#858585]">
              {currentMode === 'signin'
                ? 'Sign in to access your synchronized ledger.'
                : 'Start tracking expenses with RealByte-inspired simplicity.'}
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs font-bold text-[#555555] block mb-1">Email Address</label>
            <input
              type="email"
              placeholder="e.g. nidhi@example.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#EEEEEE] text-sm focus:outline-none focus:border-[#FF665C]"
            />
          </div>

          <div>
            <label className="text-xs font-bold text-[#555555] block mb-1">Password</label>
            <input
              type="password"
              placeholder="••••••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-[#EEEEEE] text-sm focus:outline-none focus:border-[#FF665C]"
            />
          </div>

          <button
            type="submit"
            className="w-full py-3 rounded-xl bg-[#FF665C] hover:bg-[#EE554B] text-white text-sm font-bold shadow-md shadow-[#FF665C]/25 transition-all flex items-center justify-center gap-2 mt-2"
          >
            <span>{currentMode === 'signin' ? 'Sign In' : 'Create Account'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-5 text-center text-xs text-[#858585]">
          {currentMode === 'signin' ? (
            <>
              Don't have an account?{' '}
              <button
                onClick={() => setCurrentMode('signup')}
                className="font-bold text-[#FF665C] hover:underline"
              >
                Sign Up free
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button
                onClick={() => setCurrentMode('signin')}
                className="font-bold text-[#FF665C] hover:underline"
              >
                Sign In
              </button>
            </>
          )}
        </div>

        <div className="mt-4 pt-4 border-t border-[#F2F2F2] flex items-center justify-center gap-1.5 text-[11px] text-[#858585]">
          <ShieldCheck className="w-3.5 h-3.5 text-[#2ED573]" />
          <span>Demo authentication: enter any email to explore.</span>
        </div>
      </div>
    </div>
  );
};
