import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const ROWS = [
  { stripe: 'Payment Intent', relay: 'Decision Intent' },
  { stripe: 'Webhook Events', relay: 'Audit Events' },
  { stripe: 'Fraud Detection', relay: 'Policy Enforcement' },
];

export function ComparisonTable() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });
  const prefersReducedMotion = useReducedMotion();

  return (
    <div ref={ref} className="border border-white/10 overflow-hidden">
      <table className="w-full font-mono text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left p-4 font-normal text-white">Stripe</th>
            <th className="text-left p-4 font-normal text-muted">→</th>
            <th className="text-left p-4 font-normal text-white">Payments</th>
            <th className="text-left p-4 font-normal text-muted">|</th>
            <th className="text-left p-4 font-normal text-white">Relay</th>
            <th className="text-left p-4 font-normal text-muted">→</th>
            <th className="text-left p-4 font-normal text-white">Decisions</th>
          </tr>
        </thead>
        <tbody className="text-muted">
          {ROWS.map((row, i) => (
            <motion.tr
              key={i}
              className="border-b border-white/10 last:border-0"
              initial={prefersReducedMotion ? {} : { backgroundColor: 'transparent' }}
              animate={
                isInView && !prefersReducedMotion
                  ? {
                      backgroundColor: ['transparent', 'rgba(255,255,255,0.05)', 'transparent'],
                    }
                  : {}
              }
              transition={{ delay: i * 0.4, duration: 0.8 }}
            >
              <td className="p-4" colSpan={3}>{row.stripe}</td>
              <td className="p-4 text-white/30">|</td>
              <td className="p-4" colSpan={3}>{row.relay}</td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
