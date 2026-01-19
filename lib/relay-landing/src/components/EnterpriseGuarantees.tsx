import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { StepHeader } from './StepHeader';
import { AirGapVisualization } from './animations/AirGapVisualization';
import { ProtectedCodeFlow } from './animations/ProtectedCodeFlow';
import { DetailedAuditFeed } from './animations/DetailedAuditFeed';

const steps = [
  {
    number: 1,
    title: 'The air gap',
    subtitle: 'Physical separation between reasoning and execution',
    component: AirGapVisualization,
  },
  {
    number: 2,
    title: '3 lines of code',
    subtitle: 'Protect any function',
    component: ProtectedCodeFlow,
  },
  {
    number: 3,
    title: 'Immutable log',
    subtitle: 'Every decision recorded',
    component: DetailedAuditFeed,
  },
];

export function EnterpriseGuarantees() {
  const [currentStep, setCurrentStep] = useState(0);

  const handlePrevious = () => {
    setCurrentStep((prev) => (prev === 0 ? steps.length - 1 : prev - 1));
  };

  const handleNext = () => {
    setCurrentStep((prev) => (prev === steps.length - 1 ? 0 : prev + 1));
  };

  const step = steps[currentStep];
  const StepComponent = step.component;

  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-24 border-t border-white/10">
      <div className="max-w-5xl w-full space-y-12">
        <h2 className="text-3xl md:text-4xl font-medium text-white/90">
          How it works
        </h2>

        {/* Carousel Container */}
        <div className="relative">
          {/* Step Header */}
          <div className="mb-8">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.3 }}
              >
                <StepHeader
                  number={step.number}
                  title={step.title}
                  subtitle={step.subtitle}
                />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Animation Carousel */}
          <div className="relative overflow-hidden">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                className="w-full"
              >
                <StepComponent />
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Navigation Arrows */}
          <div className="absolute top-1/2 -translate-y-1/2 left-0 right-0 flex justify-between items-center pointer-events-none">
            <button
              onClick={handlePrevious}
              className="pointer-events-auto -ml-4 md:-ml-12 flex items-center justify-center w-10 h-10 rounded-full bg-black/60 border border-white/20 hover:border-white/40 hover:bg-black/80 transition-all text-white/70 hover:text-white"
              aria-label="Previous step"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
            </button>
            <button
              onClick={handleNext}
              className="pointer-events-auto -mr-4 md:-mr-12 flex items-center justify-center w-10 h-10 rounded-full bg-black/60 border border-white/20 hover:border-white/40 hover:bg-black/80 transition-all text-white/70 hover:text-white"
              aria-label="Next step"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Dot Indicators */}
        <div className="flex justify-center gap-2 pt-6">
          {steps.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentStep(index)}
              className={`w-2 h-2 rounded-full transition-all ${
                index === currentStep
                  ? 'bg-white/90 w-8'
                  : 'bg-white/20 hover:bg-white/40'
              }`}
              aria-label={`Go to step ${index + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
}
