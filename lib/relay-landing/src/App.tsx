import { AnimatedBackground } from './components/AnimatedBackground';
import { Hero } from './components/Hero';
import { BilateralProblem } from './components/BilateralProblem';
import { StandardComponents } from './components/StandardComponents';
import { AdoptionPath } from './components/AdoptionPath';
import { Waitlist } from './components/Waitlist';
import { Footer } from './components/Footer';

function App() {
  return (
    <div className="snap-y snap-mandatory h-screen overflow-y-scroll">
      <AnimatedBackground />

      <div className="relative z-10">
        <div className="snap-start">
          <Hero />
        </div>
        <div className="snap-start">
          <BilateralProblem />
        </div>
        <div className="snap-start">
          <StandardComponents />
        </div>
        <div className="snap-start">
          <AdoptionPath />
        </div>
        <div className="snap-start">
          <Waitlist />
          <Footer />
        </div>
      </div>
    </div>
  );
}

export default App;
