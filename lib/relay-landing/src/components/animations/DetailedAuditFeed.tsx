import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export function DetailedAuditFeed() {
  const [showManifest, setShowManifest] = useState(false);
  const [showPolicy, setShowPolicy] = useState(false);
  const [showSeal, setShowSeal] = useState(false);
  const [cycleKey, setCycleKey] = useState(0);

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  useEffect(() => {
    if (prefersReducedMotion) {
      setShowManifest(true);
      setShowPolicy(true);
      setShowSeal(true);
      return;
    }

    // Reset states
    setShowManifest(false);
    setShowPolicy(false);
    setShowSeal(false);

    // Cascade reveal
    setShowManifest(true);
    const timer1 = setTimeout(() => setShowPolicy(true), 400);
    const timer2 = setTimeout(() => setShowSeal(true), 800);

    // After seal appears + 2s pause, reset and restart
    const resetTimer = setTimeout(() => {
      setShowManifest(false);
      setShowPolicy(false);
      setShowSeal(false);

      setTimeout(() => setCycleKey(prev => prev + 1), 500);
    }, 800 + 2000); // Last appear time + pause duration

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(resetTimer);
    };
  }, [cycleKey, prefersReducedMotion]);

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-6 font-mono text-xs min-h-[400px] space-y-4">
      {/* Manifest Section */}
      {showManifest && (
        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-2"
        >
          <div className="text-blue-400/80 font-semibold">MANIFEST</div>
          <div className="pl-3 border-l-2 border-blue-400/30 space-y-1 text-muted/70">
            <div>Agent: infra-agent-02</div>
            <div>Action: aws.terminate_vm</div>
            <div>Instance: i-0abc123</div>
            <div>Cost: $850/month</div>
          </div>
        </motion.div>
      )}

      {/* Policy Evaluation Section */}
      {showPolicy && (
        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-2"
        >
          <div className="text-amber-400/80 font-semibold">POLICY CHECK</div>
          <div className="pl-3 border-l-2 border-amber-400/30 space-y-1">
            <div className="flex justify-between items-center">
              <span className="text-muted/70">cost &lt; $1000</span>
              <span className="text-green-400">✓ PASS</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted/70">has_approval</span>
              <span className="text-green-400">✓ PASS</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Seal Section */}
      {showSeal && (
        <motion.div
          initial={prefersReducedMotion ? false : { opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-2"
        >
          <div className="text-green-400/80 font-semibold">SEAL</div>
          <div className="pl-3 border-l-2 border-green-400/30 space-y-1 text-muted/70">
            <div>Sig: ed25519:a8f3d2...</div>
            <div>Expires: 5min</div>
            <div className="text-green-400 font-semibold">APPROVED</div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
