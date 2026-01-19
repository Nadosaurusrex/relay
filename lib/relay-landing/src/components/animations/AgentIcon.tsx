import { motion } from 'framer-motion';

interface AgentIconProps {
  x: number;
  y: number;
  label: string;
  delay?: number;
}

export function AgentIcon({ x, y, label, delay = 0 }: AgentIconProps) {
  return (
    <g>
      <motion.circle
        cx={x}
        cy={y}
        r="30"
        fill="none"
        stroke="rgba(255,255,255,0.2)"
        strokeWidth="2"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay, duration: 0.5 }}
      />
      <motion.circle
        cx={x}
        cy={y}
        r="12"
        fill="rgba(255,255,255,0.1)"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: delay + 0.2, duration: 0.3 }}
      />
      <motion.text
        x={x}
        y={y + 50}
        textAnchor="middle"
        fill="rgba(255,255,255,0.6)"
        fontSize="12"
        fontFamily="JetBrains Mono, monospace"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.4 }}
      >
        {label}
      </motion.text>
    </g>
  );
}
