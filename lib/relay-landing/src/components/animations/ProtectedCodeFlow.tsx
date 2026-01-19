import { useEffect, useState } from 'react';

const CODE_TEXT = `@protect(provider="aws")
def terminate_vm(id: str):
    aws.ec2.terminate(id)`;

type Phase = 'typing' | 'paused' | 'resetting';

export function ProtectedCodeFlow() {
  const [typedCode, setTypedCode] = useState('');
  const [showCursor, setShowCursor] = useState(true);
  const [phase, setPhase] = useState<Phase>('typing');
  const [cycleKey, setCycleKey] = useState(0);

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Main animation loop
  useEffect(() => {
    if (prefersReducedMotion) {
      setTypedCode(CODE_TEXT);
      setShowCursor(false);
      return;
    }

    if (phase === 'typing') {
      let charIndex = 0;
      setShowCursor(true);

      const typeInterval = setInterval(() => {
        if (charIndex >= CODE_TEXT.length) {
          clearInterval(typeInterval);
          setShowCursor(false);
          setPhase('paused');
          return;
        }
        setTypedCode(CODE_TEXT.slice(0, charIndex + 1));
        charIndex++;
      }, 25);

      return () => clearInterval(typeInterval);
    } else if (phase === 'paused') {
      const timer = setTimeout(() => setPhase('resetting'), 2000);
      return () => clearTimeout(timer);
    } else if (phase === 'resetting') {
      setTypedCode('');
      const timer = setTimeout(() => {
        setCycleKey(prev => prev + 1);
        setPhase('typing');
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [phase, cycleKey, prefersReducedMotion]);

  // Cursor blink effect
  useEffect(() => {
    if (prefersReducedMotion || !showCursor || phase !== 'typing') return;

    const blinkInterval = setInterval(() => {
      setShowCursor((prev) => !prev);
    }, 500);

    return () => clearInterval(blinkInterval);
  }, [prefersReducedMotion, showCursor, phase]);

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-6 min-h-[320px] flex items-start justify-start overflow-x-auto">
      <div className="font-mono text-sm text-muted/90 whitespace-pre">
        {typedCode}
        {showCursor && !prefersReducedMotion && (
          <span className="inline-block w-2 h-4 bg-blue-400 ml-1" />
        )}
      </div>
    </div>
  );
}
