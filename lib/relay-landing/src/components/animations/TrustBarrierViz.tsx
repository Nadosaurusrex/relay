import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

export function TrustBarrierViz() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const prefersReducedMotion = useReducedMotion();

  return (
    <div ref={ref} className="w-full max-w-3xl mx-auto py-12">
      <div className="relative flex items-center justify-between">
        {/* Company A */}
        <motion.div
          className="flex flex-col items-center"
          initial={prefersReducedMotion ? {} : { opacity: 0, x: -20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <div className="w-24 h-24 border border-white/20 flex items-center justify-center mb-4">
            <div className="text-white/40 text-xs font-mono">Agent A</div>
          </div>
          <div className="text-muted text-sm">Nike</div>
        </motion.div>

        {/* Center - Transaction attempt */}
        <div className="flex-1 mx-8 relative">
          <motion.div
            className="border-t border-dashed border-white/20 relative"
            initial={prefersReducedMotion ? {} : { scaleX: 0 }}
            animate={isInView ? { scaleX: 1 } : {}}
            transition={{ delay: 0.5, duration: 0.8 }}
            style={{ originX: 0 }}
          >
            {/* Transaction proposal */}
            <motion.div
              className="absolute -top-12 left-1/2 -translate-x-1/2 bg-black/40 border border-white/10 px-4 py-2 text-xs font-mono text-white/60 whitespace-nowrap"
              initial={prefersReducedMotion ? {} : { opacity: 0, y: 10 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.8, duration: 0.4 }}
            >
              €100,000 deal
            </motion.div>

            {/* Question marks */}
            <motion.div
              className="absolute -bottom-12 left-1/2 -translate-x-1/2 text-red-400/60 text-2xl"
              initial={prefersReducedMotion ? {} : { opacity: 0, scale: 0 }}
              animate={isInView ? { opacity: 1, scale: 1 } : {}}
              transition={{ delay: 1.2, duration: 0.3, type: 'spring' }}
            >
              ?
            </motion.div>
          </motion.div>
        </div>

        {/* Company B */}
        <motion.div
          className="flex flex-col items-center"
          initial={prefersReducedMotion ? {} : { opacity: 0, x: 20 }}
          animate={isInView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.5 }}
        >
          <div className="w-24 h-24 border border-white/20 flex items-center justify-center mb-4">
            <div className="text-white/40 text-xs font-mono">Agent B</div>
          </div>
          <div className="text-muted text-sm">Salesforce</div>
        </motion.div>
      </div>

      {/* Questions */}
      <motion.div
        className="mt-16 space-y-3 text-center text-sm text-muted"
        initial={prefersReducedMotion ? {} : { opacity: 0 }}
        animate={isInView ? { opacity: 1 } : {}}
        transition={{ delay: 1.5, duration: 0.5 }}
      >
        <div>Is Agent A authorized to spend €100,000?</div>
        <div>Can Agent B prove it followed policy?</div>
        <div>Who verifies? Who audits?</div>
      </motion.div>
    </div>
  );
}
