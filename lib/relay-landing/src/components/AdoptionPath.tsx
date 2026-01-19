import { useState, useEffect } from 'react';
import { ApiJourney } from './animations/ApiJourney';
import { CodeExamples, EXAMPLES } from './animations/CodeExamples';
import { useReducedMotion } from '../hooks/useReducedMotion';

export function AdoptionPath() {
  const [selected, setSelected] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const prefersReducedMotion = useReducedMotion();

  const currentCode = EXAMPLES[selected].code;
  const currentProvider = EXAMPLES[selected].provider;

  useEffect(() => {
    if (prefersReducedMotion) {
      setCharCount(currentCode.length);
      return;
    }

    // Reset and type out when selection changes
    setCharCount(0);
    const interval = setInterval(() => {
      setCharCount((prev) => {
        if (prev >= currentCode.length) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 30);

    return () => clearInterval(interval);
  }, [selected, currentCode.length, prefersReducedMotion]);

  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20 border-t border-white/10">
      <div className="max-w-4xl w-full space-y-16">
        <h2 className="text-4xl md:text-5xl font-normal">
          The journey
        </h2>

        <div className="space-y-6">
          <h3 className="text-xl">Three lines needed to start</h3>
          <CodeExamples
            selected={selected}
            onSelect={setSelected}
            charCount={charCount}
          />
        </div>

        <div className="pt-8 border-t border-white/10">
          <ApiJourney provider={currentProvider} />
        </div>
      </div>
    </section>
  );
}
