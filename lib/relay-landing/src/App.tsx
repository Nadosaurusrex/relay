import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnimatedBackground } from './components/AnimatedBackground';
import { Hero } from './components/Hero';
import { EnterpriseProblem } from './components/EnterpriseProblem';
import { EnterpriseGuarantees } from './components/EnterpriseGuarantees';
import { AdoptionPath } from './components/AdoptionPath';
import { WhoItsFor } from './components/WhoItsFor';
import { PlaygroundSection } from './components/PlaygroundSection';
import { Waitlist } from './components/Waitlist';
import { Footer } from './components/Footer';
import { Playground } from './pages/Playground';

function HomePage() {
  return (
    <div className="snap-y snap-mandatory h-screen overflow-y-scroll">
      <AnimatedBackground />

      <div className="relative z-10">
        <div className="snap-start">
          <Hero />
        </div>
        <div className="snap-start">
          <EnterpriseProblem />
        </div>
        <div className="snap-start">
          <EnterpriseGuarantees />
        </div>
        <div className="snap-start">
          <AdoptionPath />
        </div>
        <div className="snap-start">
          <WhoItsFor />
        </div>
        <div className="snap-start">
          <PlaygroundSection />
        </div>
        <div className="snap-start">
          <Waitlist />
          <Footer />
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/playground" element={<Playground />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
