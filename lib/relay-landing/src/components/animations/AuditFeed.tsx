import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

interface AuditEntry {
  action: string;
  decision: 'APPROVED' | 'DENIED';
  detail: string;
}

const sampleEntries: AuditEntry[] = [
  {
    action: 'charge_card',
    decision: 'APPROVED',
    detail: '$4,999',
  },
  {
    action: 'charge_card',
    decision: 'DENIED',
    detail: '$6,000',
  },
  {
    action: 'terminate_vm',
    decision: 'APPROVED',
    detail: 'us-east-1',
  },
  {
    action: 'delete_data',
    decision: 'DENIED',
    detail: 'admin only',
  },
];

export function AuditFeed() {
  const [visibleEntries, setVisibleEntries] = useState<AuditEntry[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    // Add entries one by one
    if (currentIndex < sampleEntries.length) {
      const timeout = setTimeout(() => {
        setVisibleEntries(prev => [...prev, sampleEntries[currentIndex]]);
        setCurrentIndex(prev => prev + 1);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex]);

  return (
    <div className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-6 space-y-3 font-mono text-xs min-h-[240px]">
      {visibleEntries.map((entry, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-1"
        >
          <div className="flex items-center justify-between">
            <span className="text-muted/70 text-xs">{entry.action}</span>
            <span
              className={`px-2 py-0.5 rounded text-xs font-semibold ${
                entry.decision === 'APPROVED'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-red-500/20 text-red-400'
              }`}
            >
              {entry.decision}
            </span>
          </div>
          <div className="text-muted/50 text-xs pl-2 border-l-2 border-white/10">
            {entry.detail}
          </div>
        </motion.div>
      ))}
    </div>
  );
}
