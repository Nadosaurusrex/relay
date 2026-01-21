import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Scenario {
  request: string;
  amount?: string;
  rule: string;
  approved: boolean;
  executionTarget: string;
}

const scenarios: Scenario[] = [
  {
    request: 'Pay Salesforce $95k',
    amount: '$95,000',
    rule: 'amount > $50k',
    approved: false,
    executionTarget: 'stripe.com',
  },
  {
    request: 'Terminate AWS VM',
    amount: '$850/mo',
    rule: 'cost < $1000/mo',
    approved: true,
    executionTarget: 'aws.amazon.com',
  },
  {
    request: 'Delete GitHub repo',
    rule: 'has_backup',
    approved: true,
    executionTarget: 'github.com',
  },
];

export function AirGapVisualization() {
  const [currentScenario, setCurrentScenario] = useState(0);
  const [showManifest, setShowManifest] = useState(false);
  const [showEvaluation, setShowEvaluation] = useState(false);
  const [showSeal, setShowSeal] = useState(false);
  const [showExecution, setShowExecution] = useState(false);

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const scenario = scenarios[currentScenario];

  useEffect(() => {
    if (prefersReducedMotion) {
      setShowManifest(true);
      setShowEvaluation(true);
      setShowSeal(true);
      setShowExecution(scenario.approved);
      return;
    }

    // Reset states
    setShowManifest(false);
    setShowEvaluation(false);
    setShowSeal(false);
    setShowExecution(false);

    // Animation sequence
    const timers: number[] = [];

    // 1. Agent sends request (manifest appears)
    timers.push(setTimeout(() => {
      setShowManifest(true);
    }, 300));

    // 2. Policy evaluates
    timers.push(setTimeout(() => {
      setShowEvaluation(true);
    }, 1000));

    // 3. Show result (seal or denial)
    timers.push(setTimeout(() => {
      setShowSeal(true);
    }, 1800));

    // 4. If approved, show execution
    if (scenario.approved) {
      timers.push(setTimeout(() => {
        setShowExecution(true);
      }, 2500));
    }

    // 5. Pause, then reset for next scenario
    timers.push(setTimeout(() => {
      setCurrentScenario((prev) => (prev + 1) % scenarios.length);
    }, scenario.approved ? 4500 : 4000));

    return () => timers.forEach(clearTimeout);
  }, [currentScenario, prefersReducedMotion, scenario.approved]);

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-8 min-h-[460px] flex flex-col justify-between gap-6">
      {/* Agent Layer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-medium text-white/40 uppercase tracking-wide">
            Agent Layer
          </div>
          <div className="text-xs text-white/30 font-mono">
            LLM reasoning · Can be manipulated
          </div>
        </div>
        <div className="relative p-4 rounded-lg border border-purple-500/20 bg-purple-500/5">
          <AnimatePresence mode="wait">
            {showManifest && (
              <motion.div
                key={`agent-${currentScenario}`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="text-sm text-purple-300/90 font-medium"
              >
                {scenario.request}
                {scenario.amount && (
                  <span className="ml-2 text-purple-400/60">({scenario.amount})</span>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Flow Arrow Down */}
      <div className="flex justify-center">
        <motion.div
          animate={{
            opacity: showManifest ? [0.3, 1, 0.3] : 0,
            y: showManifest ? [0, 4, 0] : 0,
          }}
          transition={{
            duration: 1,
            repeat: showManifest && !showEvaluation ? Infinity : 0,
            ease: 'easeInOut',
          }}
          className="text-white/30 text-2xl"
        >
          ↓
        </motion.div>
      </div>

      {/* Policy Layer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-medium text-white/40 uppercase tracking-wide">
            Policy Layer
          </div>
          <div className="text-xs text-white/30 font-mono">
            Deterministic code · Immune to prompts
          </div>
        </div>
        <div className="relative p-4 rounded-lg border-2 border-amber-500/30 bg-amber-500/5">
          <AnimatePresence mode="wait">
            {showEvaluation && (
              <motion.div
                key={`policy-${currentScenario}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="space-y-2"
              >
                <div className="text-xs text-amber-400/60 font-mono mb-2">
                  Evaluating: {scenario.rule}
                </div>
                <div className="flex items-center gap-2">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.3, type: 'spring' }}
                    className={`flex items-center gap-2 text-sm font-semibold ${
                      scenario.approved ? 'text-green-400' : 'text-red-400'
                    }`}
                  >
                    {scenario.approved ? (
                      <>
                        <span className="text-lg">✓</span>
                        <span>APPROVED</span>
                      </>
                    ) : (
                      <>
                        <span className="text-lg">✗</span>
                        <span>DENIED</span>
                      </>
                    )}
                  </motion.div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Flow Arrow Down (conditional) */}
      <div className="flex justify-center">
        <motion.div
          animate={{
            opacity: showSeal && scenario.approved ? [0.3, 1, 0.3] : showSeal && !scenario.approved ? 0.2 : 0,
            y: showSeal && scenario.approved ? [0, 4, 0] : 0,
          }}
          transition={{
            duration: 1,
            repeat: showSeal && scenario.approved && !showExecution ? Infinity : 0,
            ease: 'easeInOut',
          }}
          className={`text-2xl ${
            showSeal && !scenario.approved ? 'text-red-500/30 line-through' : 'text-white/30'
          }`}
        >
          {showSeal && !scenario.approved ? '✗' : '↓'}
        </motion.div>
      </div>

      {/* Execution Layer */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-xs font-medium text-white/40 uppercase tracking-wide">
            Execution Layer
          </div>
          <div className="text-xs text-white/30 font-mono">
            External services · AWS, Stripe, etc.
          </div>
        </div>
        <div className="relative p-4 rounded-lg border border-blue-500/20 bg-blue-500/5 min-h-[48px] flex items-center">
          <AnimatePresence mode="wait">
            {showExecution ? (
              <motion.div
                key={`exec-${currentScenario}`}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="flex items-center gap-2 text-sm text-green-400/90"
              >
                <span className="text-lg">✓</span>
                <span>Executed on {scenario.executionTarget}</span>
              </motion.div>
            ) : (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: showSeal && !scenario.approved ? 1 : 0 }}
                className="text-sm text-red-400/60 italic"
              >
                Action blocked · Never reached execution
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
