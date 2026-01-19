import { motion } from 'framer-motion';

interface RelaySealProps {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  delay?: number;
}

export function RelaySeal({ x1, y1, x2, y2, delay = 0 }: RelaySealProps) {
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  return (
    <g>
      {/* Connection line */}
      <motion.line
        x1={x1}
        y1={y1}
        x2={x2}
        y2={y2}
        stroke="rgba(34,197,94,0.6)"
        strokeWidth="2"
        strokeDasharray="5,5"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ delay, duration: 0.8 }}
      />
      {/* Seal badge */}
      <motion.circle
        cx={midX}
        cy={midY}
        r="20"
        fill="rgba(34,197,94,0.2)"
        stroke="rgba(34,197,94,0.6)"
        strokeWidth="2"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: delay + 0.8, duration: 0.4 }}
      />
      <motion.text
        x={midX}
        y={midY + 4}
        textAnchor="middle"
        fill="rgba(34,197,94,0.9)"
        fontSize="20"
        fontFamily="monospace"
        fontWeight="bold"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 1.0 }}
      >
        ✓
      </motion.text>
    </g>
  );
}
