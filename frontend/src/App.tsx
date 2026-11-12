import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { TrustStats } from './components/TrustStats';
import { Features } from './components/Features';
import { ProductShowcase } from './components/ProductShowcase';
import { HelpCenter } from './components/HelpCenter';
import { InteractiveDashboard } from './components/InteractiveDashboard';
import { Footer } from './components/Footer';
import { AuthModal } from './components/AuthModal';

export function App() {
  const [authModal, setAuthModal] = useState<{ isOpen: boolean; mode: 'signin' | 'signup' }>({
    isOpen: false,
    mode: 'signin',
  });

  const handleOpenAuth = (mode: 'signin' | 'signup') => {
    setAuthModal({ isOpen: true, mode });
  };

  const handleCloseAuth = () => {
    setAuthModal(prev => ({ ...prev, isOpen: false }));
  };

  const handleAuthSuccess = (email: string) => {
    const el = document.getElementById('dashboard-preview');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleExplore = () => {
    const el = document.getElementById('features');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const handleScrollToDashboard = () => {
    const el = document.getElementById('dashboard-preview');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="min-h-screen bg-white text-[#171717] flex flex-col font-sans selection:bg-[#FF665C]/20 selection:text-[#FF665C]">
      {/* 1. Transparent-to-Sticky Navbar */}
      <Navbar onOpenAuth={handleOpenAuth} />

      {/* Main RealByte Layout */}
      <main className="flex-1">
        {/* 2. Hero Section with 3-Phones Moving Fan Mockup */}
        <Hero
          onGetStarted={() => handleOpenAuth('signup')}
          onExplore={handleExplore}
        />

        {/* 3. RealByte Laurel Wreath Trust & Stats Bar */}
        <TrustStats />

        {/* 4. RealByte Features Section with Moving Animated Icons & Interactive Phone */}
        <Features />

        {/* 5. RealByte Screenshots Carousel (Light / Dark Switcher + 4 Phones) */}
        <ProductShowcase />

        {/* 6. RealByte Help Center & Web Manager Monitor */}
        <HelpCenter onOpenDashboard={handleScrollToDashboard} />

        {/* 7. Live Interactive Dashboard (Financial Application Workspace) */}
        <InteractiveDashboard />
      </main>

      {/* 8. Clean RealByte-style Footer */}
      <Footer />

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModal.isOpen}
        mode={authModal.mode}
        onClose={handleCloseAuth}
        onSuccess={handleAuthSuccess}
      />
    </div>
  );
}

export default App;
