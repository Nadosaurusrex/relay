import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

export function DualSignature() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const prefersReducedMotion = useReducedMotion();

  const documentX = 300;
  const documentY = 100;
  const documentWidth = 200;
  const documentHeight = 120;

  return (
    <div ref={ref} className="w-full max-w-2xl mx-auto my-6">
      <svg viewBox="0 0 600 200" className="w-full h-auto">
        {/* Document */}
        <motion.rect
          x={documentX - documentWidth / 2}
          y={documentY - documentHeight / 2}
          width={documentWidth}
          height={documentHeight}
          fill="rgba(255,255,255,0.05)"
          stroke="rgba(255,255,255,0.2)"
          strokeWidth="2"
          rx="4"
          initial={prefersReducedMotion ? {} : { scale: 0.8, opacity: 0 }}
          animate={isInView ? { scale: 1, opacity: 1 } : {}}
          transition={{ duration: 0.5 }}
        />

        {/* Document lines */}
        {[0, 1, 2, 3].map((i) => (
          <motion.line
            key={i}
            x1={documentX - documentWidth / 2 + 20}
            y1={documentY - documentHeight / 2 + 25 + i * 15}
            x2={documentX + documentWidth / 2 - 20}
            y2={documentY - documentHeight / 2 + 25 + i * 15}
            stroke="rgba(255,255,255,0.2)"
            strokeWidth="1"
            initial={prefersReducedMotion ? {} : { pathLength: 0 }}
            animate={isInView ? { pathLength: 1 } : {}}
            transition={{ delay: 0.5 + i * 0.1, duration: 0.3 }}
          />
        ))}

        {/* Left Key (Buyer) */}
        <motion.g
          initial={prefersReducedMotion ? {} : { x: -100, opacity: 0 }}
          animate={isInView ? { x: 0, opacity: 1 } : {}}
          transition={{ delay: 1, duration: 0.6 }}
        >
          <rect
            x={50}
            y={80}
            width={80}
            height={40}
            fill="rgba(255,255,255,0.1)"
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="2"
            rx="4"
          />
          <text
            x={90}
            y={105}
            textAnchor="middle"
            fill="rgba(255,255,255,0.7)"
            fontSize="12"
            fontFamily="JetBrains Mono, monospace"
          >
            🔑 Buyer
          </text>
        </motion.g>

        {/* Right Key (Seller) */}
        <motion.g
          initial={prefersReducedMotion ? {} : { x: 100, opacity: 0 }}
          animate={isInView ? { x: 0, opacity: 1 } : {}}
          transition={{ delay: 1, duration: 0.6 }}
        >
          <rect
            x={470}
            y={80}
            width={80}
            height={40}
            fill="rgba(255,255,255,0.1)"
            stroke="rgba(255,255,255,0.3)"
            strokeWidth="2"
            rx="4"
          />
          <text
            x={510}
            y={105}
            textAnchor="middle"
            fill="rgba(255,255,255,0.7)"
            fontSize="12"
            fontFamily="JetBrains Mono, monospace"
          >
            🔑 Seller
          </text>
        </motion.g>

        {/* Signature stamps */}
        {isInView && !prefersReducedMotion && (
          <>
            {/* Left stamp */}
            <motion.circle
              cx={240}
              cy={150}
              r="15"
              fill="rgba(34,197,94,0.2)"
              stroke="rgba(34,197,94,0.6)"
              strokeWidth="2"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 1.8, duration: 0.3, type: 'spring', stiffness: 200 }}
            />
            <motion.text
              x={240}
              y={155}
              textAnchor="middle"
              fill="rgba(34,197,94,0.9)"
              fontSize="16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2 }}
            >
              ✓
            </motion.text>

            {/* Right stamp */}
            <motion.circle
              cx={360}
              cy={150}
              r="15"
              fill="rgba(34,197,94,0.2)"
              stroke="rgba(34,197,94,0.6)"
              strokeWidth="2"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 2.1, duration: 0.3, type: 'spring', stiffness: 200 }}
            />
            <motion.text
              x={360}
              y={155}
              textAnchor="middle"
              fill="rgba(34,197,94,0.9)"
              fontSize="16"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2.3 }}
            >
              ✓
            </motion.text>
          </>
        )}

        {/* Final state for reduced motion */}
        {prefersReducedMotion && (
          <>
            <circle
              cx={240}
              cy={150}
              r="15"
              fill="rgba(34,197,94,0.2)"
              stroke="rgba(34,197,94,0.6)"
              strokeWidth="2"
            />
            <text x={240} y={155} textAnchor="middle" fill="rgba(34,197,94,0.9)" fontSize="16">
              ✓
            </text>
            <circle
              cx={360}
              cy={150}
              r="15"
              fill="rgba(34,197,94,0.2)"
              stroke="rgba(34,197,94,0.6)"
              strokeWidth="2"
            />
            <text x={360} y={155} textAnchor="middle" fill="rgba(34,197,94,0.9)" fontSize="16">
              ✓
            </text>
          </>
        )}
      </svg>
    </div>
  );
}
