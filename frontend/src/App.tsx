import React from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { Features } from './components/Features';
import { ProductShowcase } from './components/ProductShowcase';
import { HelpCenter } from './components/HelpCenter';
import { InteractiveDashboard } from './components/InteractiveDashboard';
import { Footer } from './components/Footer';

export function App() {
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
      <Navbar onOpenAuth={handleScrollToDashboard} />

      {/* Main Layout */}
      <main className="flex-1">
        {/* 2. Hero Section with 3-Phones Moving Fan Mockup */}
        <Hero
          onGetStarted={handleScrollToDashboard}
          onExplore={handleExplore}
        />

        {/* 4. Features Section with Moving Animated Icons & Interactive Phone */}
        <Features />

        {/* 5. Screenshots Carousel (Light / Dark Switcher + 4 Phones) */}
        <ProductShowcase />

        {/* 6. Help Center & Web Manager Monitor */}
        <HelpCenter onOpenDashboard={handleScrollToDashboard} />

        {/* 7. Live Interactive Dashboard (Financial Application Workspace) */}
        <InteractiveDashboard />
      </main>

      {/* 8. Clean Footer */}
      <Footer />
    </div>
  );
}

export default App;
