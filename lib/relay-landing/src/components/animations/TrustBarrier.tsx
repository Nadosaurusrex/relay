import { motion } from 'framer-motion';

interface TrustBarrierProps {
  x: number;
  y: number;
  height: number;
}

export function TrustBarrier({ x, y, height }: TrustBarrierProps) {
  return (
    <g>
      <motion.rect
        x={x - 2}
        y={y}
        width="4"
        height={height}
        fill="rgba(239,68,68,0.6)"
        initial={{ scaleY: 0, opacity: 0 }}
        animate={{ scaleY: 1, opacity: 1 }}
        exit={{ scaleY: 0, opacity: 0 }}
        transition={{ duration: 0.5 }}
        style={{ originY: 'center' }}
      />
      <motion.path
        d={`M ${x - 15} ${y + height / 2 - 8} L ${x} ${y + height / 2} L ${x - 15} ${y + height / 2 + 8} Z`}
        fill="rgba(239,68,68,0.6)"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ delay: 0.3 }}
      />
      <motion.path
        d={`M ${x + 15} ${y + height / 2 - 8} L ${x} ${y + height / 2} L ${x + 15} ${y + height / 2 + 8} Z`}
        fill="rgba(239,68,68,0.6)"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ delay: 0.3 }}
      />
      <motion.text
        x={x}
        y={y - 10}
        textAnchor="middle"
        fill="rgba(239,68,68,0.8)"
        fontSize="10"
        fontFamily="JetBrains Mono, monospace"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ delay: 0.5 }}
      >
        TRUST BARRIER
      </motion.text>
    </g>
  );
}
