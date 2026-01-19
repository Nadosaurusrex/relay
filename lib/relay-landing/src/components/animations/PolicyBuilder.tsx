import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

export function PolicyBuilder() {
  const [showRule, setShowRule] = useState(false);
  const [showOperator, setShowOperator] = useState(false);
  const [showValue, setShowValue] = useState(false);

  useEffect(() => {
    const timer1 = setTimeout(() => setShowRule(true), 300);
    const timer2 = setTimeout(() => setShowOperator(true), 800);
    const timer3 = setTimeout(() => setShowValue(true), 1300);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
    };
  }, []);

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-6 space-y-4 min-h-[240px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted/80">New Rule</span>
        <span className="text-xs text-muted/60">No code</span>
      </div>

      {/* Rule Builder */}
      <div className="space-y-3">
        <div className="text-xs text-muted/90">Allow if:</div>

        <div className="flex items-center gap-3">
          {/* Field selector */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={showRule ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.3 }}
            className="flex-1"
          >
            <select className="w-full bg-white/5 border border-white/20 rounded px-3 py-2 text-sm text-white">
              <option>amount</option>
            </select>
          </motion.div>

          {/* Operator selector */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={showOperator ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.3 }}
            className="w-20"
          >
            <select className="w-full bg-white/5 border border-white/20 rounded px-3 py-2 text-sm text-white">
              <option>&lt;</option>
            </select>
          </motion.div>

          {/* Value input */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={showValue ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.3 }}
            className="w-32"
          >
            <input
              type="text"
              value="5000"
              readOnly
              className="w-full bg-white/5 border border-white/20 rounded px-3 py-2 text-sm text-white"
            />
          </motion.div>
        </div>

        {/* Generated policy preview */}
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={showValue ? { opacity: 1, height: 'auto' } : {}}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="border-t border-white/10 pt-3 mt-3 overflow-hidden"
        >
          <div className="text-xs text-muted/60 mb-2">Generated Policy:</div>
          <div className="font-mono text-xs text-green-400/80 bg-green-500/5 border border-green-500/20 rounded p-2">
            allow if &#123; amount &lt; 5000 &#125;
          </div>
        </motion.div>
      </div>
    </div>
  );
}
