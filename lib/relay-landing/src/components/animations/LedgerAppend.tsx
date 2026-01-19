import { motion } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const LEDGER_ROWS = [
  { id: '550e8400', action: 'create_payment', decision: 'approved', timestamp: '2026-01-18T10:30:01Z' },
  { id: '6d7f9511', action: 'terminate_instance', decision: 'denied', timestamp: '2026-01-18T10:31:15Z' },
  { id: '7e8fa622', action: 'update_lead_score', decision: 'approved', timestamp: '2026-01-18T10:32:42Z' },
];

export function LedgerAppend() {
  const prefersReducedMotion = useReducedMotion();

  return (
    <div className="border border-white/10 overflow-hidden">
      <table className="w-full font-mono text-xs">
        <thead>
          <tr className="border-b border-white/10 bg-black/20">
            <th className="text-left p-3 font-normal text-white/60">ID</th>
            <th className="text-left p-3 font-normal text-white/60">Action</th>
            <th className="text-left p-3 font-normal text-white/60">Decision</th>
            <th className="text-left p-3 font-normal text-white/60">Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {LEDGER_ROWS.map((row, i) => (
            <motion.tr
              key={row.id}
              initial={prefersReducedMotion ? {} : { y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.3, duration: 0.4 }}
              className="border-b border-white/10 last:border-0"
            >
              <td className="p-3 text-white/80">{row.id}</td>
              <td className="p-3 text-muted">{row.action}</td>
              <td className="p-3">
                <span className={row.decision === 'approved' ? 'text-green-400/60' : 'text-red-400/60'}>
                  {row.decision}
                </span>
              </td>
              <td className="p-3 text-muted">{row.timestamp}</td>
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
