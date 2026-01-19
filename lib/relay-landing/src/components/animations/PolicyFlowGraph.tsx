import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

interface Scenario {
  trigger: string;
  condition: string;
  outcome: 'APPROVE' | 'DENY';
}

const scenarios: Scenario[] = [
  {
    trigger: 'AWS Terminate VM',
    condition: 'cost < $1000/mo',
    outcome: 'APPROVE',
  },
  {
    trigger: 'GitHub Delete Repo',
    condition: 'has_backup',
    outcome: 'APPROVE',
  },
  {
    trigger: 'Salesforce Deal',
    condition: 'amount > $50k',
    outcome: 'DENY',
  },
];

const organicEasing = {
  enter: [0.34, 1.56, 0.64, 1] as [number, number, number, number],
};

export function PolicyFlowGraph() {
  const [currentScenario, setCurrentScenario] = useState(0);
  const [showNodes, setShowNodes] = useState(false);

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Initial reveal
  useEffect(() => {
    if (prefersReducedMotion) {
      setShowNodes(true);
    } else {
      const timer = setTimeout(() => setShowNodes(true), 100);
      return () => clearTimeout(timer);
    }
  }, [prefersReducedMotion]);

  // Auto-cycle scenarios
  useEffect(() => {
    if (!prefersReducedMotion) {
      const interval = setInterval(() => {
        setCurrentScenario((prev) => (prev + 1) % scenarios.length);
      }, 4000); // 4 seconds per scenario
      return () => clearInterval(interval);
    }
  }, [prefersReducedMotion]);

  const scenario = scenarios[currentScenario];

  const nodeVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: {
      opacity: 1,
      scale: 1,
      transition: {
        duration: 0.4,
        ease: organicEasing.enter,
      },
    },
  };

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-6 min-h-[460px] flex items-center justify-center">
      <div className="flex flex-col items-center justify-center gap-3 w-full">
        {showNodes && (
          <>
            {/* Trigger Node */}
            <motion.div
              key={`trigger-${currentScenario}`}
              variants={nodeVariants}
              initial="hidden"
              animate="visible"
              className="w-full"
            >
              <div className="px-4 py-3 rounded-lg border border-blue-400/30 bg-blue-500/5 backdrop-blur-sm">
                <div className="text-xs text-blue-400/60 font-medium mb-1">TRIGGER</div>
                <div className="text-sm font-semibold text-blue-300">{scenario.trigger}</div>
              </div>
            </motion.div>

            <div className="text-slate-400 text-lg">↓</div>

            {/* Condition Node */}
            <motion.div
              key={`condition-${currentScenario}`}
              variants={nodeVariants}
              initial="hidden"
              animate="visible"
              className="w-full"
            >
              <div className="px-4 py-3 rounded-lg border border-amber-400/30 bg-amber-500/5 backdrop-blur-sm">
                <div className="text-xs text-amber-400/60 font-medium mb-1">CONDITION</div>
                <div className="text-sm font-mono text-amber-300">{scenario.condition}</div>
              </div>
            </motion.div>

            <div className="text-slate-400 text-lg">↓</div>

            {/* Outcome Node */}
            <motion.div
              key={`outcome-${currentScenario}`}
              variants={nodeVariants}
              initial="hidden"
              animate="visible"
              className="w-full"
            >
              <div
                className={`px-4 py-3 rounded-lg border backdrop-blur-sm ${
                  scenario.outcome === 'APPROVE'
                    ? 'border-green-400/30 bg-green-500/5'
                    : 'border-red-400/30 bg-red-500/5'
                }`}
              >
                <div
                  className={`text-xs font-medium mb-1 ${
                    scenario.outcome === 'APPROVE' ? 'text-green-400/60' : 'text-red-400/60'
                  }`}
                >
                  OUTCOME
                </div>
                <div
                  className={`text-sm font-semibold flex items-center gap-1 ${
                    scenario.outcome === 'APPROVE' ? 'text-green-300' : 'text-red-300'
                  }`}
                >
                  {scenario.outcome === 'APPROVE' ? '✓' : '✗'} {scenario.outcome}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </div>
    </div>
  );
}
