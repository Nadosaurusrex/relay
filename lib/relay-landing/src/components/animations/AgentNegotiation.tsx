import { motion, AnimatePresence } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef, useState, useEffect } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';
import { AgentIcon } from './AgentIcon';
import { TrustBarrier } from './TrustBarrier';
import { RelaySeal } from './RelaySeal';

export function AgentNegotiation() {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, amount: 0.5 });
  const prefersReducedMotion = useReducedMotion();
  const [phase, setPhase] = useState(0);

  useEffect(() => {
    if (!isInView || prefersReducedMotion) {
      setPhase(3); // Show final state
      return;
    }

    // Phase 0: Agents appear (0s)
    // Phase 1: Barrier appears (0.8s)
    // Phase 2: Relay gateway appears (2s)
    // Phase 3: Barrier dissolves, seals flow (3s)
    const timers = [
      setTimeout(() => setPhase(1), 800),
      setTimeout(() => setPhase(2), 2000),
      setTimeout(() => setPhase(3), 3000),
    ];

    return () => timers.forEach(clearTimeout);
  }, [isInView, prefersReducedMotion]);

  const viewBoxWidth = 600;
  const viewBoxHeight = 300;
  const leftAgentX = 100;
  const rightAgentX = 500;
  const agentY = 150;
  const barrierX = viewBoxWidth / 2;
  const gatewayY = 240;

  return (
    <div ref={ref} className="w-full max-w-3xl mx-auto my-8">
      <svg
        viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
        className="w-full h-auto"
        style={{ minHeight: '300px' }}
      >
        {/* Left Agent (Nike) */}
        {(phase >= 0 || prefersReducedMotion) && (
          <AgentIcon x={leftAgentX} y={agentY} label="Nike Agent" delay={0} />
        )}

        {/* Right Agent (Salesforce) */}
        {(phase >= 0 || prefersReducedMotion) && (
          <AgentIcon x={rightAgentX} y={agentY} label="Salesforce Agent" delay={0.2} />
        )}

        {/* Trust Barrier */}
        <AnimatePresence>
          {phase >= 1 && phase < 3 && !prefersReducedMotion && (
            <TrustBarrier x={barrierX} y={50} height={200} />
          )}
        </AnimatePresence>

        {/* Relay Gateway */}
        {(phase >= 2 || prefersReducedMotion) && (
          <motion.g
            initial={prefersReducedMotion ? {} : { y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: prefersReducedMotion ? 0 : 2, duration: 0.5 }}
          >
            <rect
              x={barrierX - 60}
              y={gatewayY - 25}
              width="120"
              height="50"
              fill="rgba(255,255,255,0.05)"
              stroke="rgba(255,255,255,0.2)"
              strokeWidth="1"
              rx="4"
            />
            <text
              x={barrierX}
              y={gatewayY + 5}
              textAnchor="middle"
              fill="rgba(255,255,255,0.8)"
              fontSize="14"
              fontFamily="JetBrains Mono, monospace"
              fontWeight="bold"
            >
              RELAY
            </text>
          </motion.g>
        )}

        {/* Seals flowing between agents */}
        {(phase >= 3 || prefersReducedMotion) && (
          <>
            <RelaySeal
              x1={leftAgentX}
              y1={agentY}
              x2={rightAgentX}
              y2={agentY}
              delay={prefersReducedMotion ? 0 : 3}
            />
          </>
        )}
      </svg>
    </div>
  );
}
