import { useEffect, useRef, useState } from 'react';
import { useInView } from 'framer-motion';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface NetworkNode {
  id: string;
  x: number;
  y: number;
  vx: number;
  vy: number;
  phase: number; // 1, 2, or 3
  connections: string[];
}

const COMPANIES = [
  'Nike', 'Salesforce', 'AWS', 'Stripe', 'Adobe', 'Oracle',
  'SAP', 'IBM', 'Microsoft', 'Google', 'Meta', 'Apple',
  'Tesla', 'Ford', 'GM', 'Walmart', 'Target', 'Costco'
];

export function NetworkEffects() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(containerRef, { once: true, amount: 0.3 });
  const prefersReducedMotion = useReducedMotion();
  const [currentPhase, setCurrentPhase] = useState(0);

  useEffect(() => {
    if (!isInView || prefersReducedMotion) {
      setCurrentPhase(3); // Show final state
      return;
    }

    // Phase timing
    const timers = [
      setTimeout(() => setCurrentPhase(1), 500),
      setTimeout(() => setCurrentPhase(2), 2500),
      setTimeout(() => setCurrentPhase(3), 5000),
    ];

    return () => timers.forEach(clearTimeout);
  }, [isInView, prefersReducedMotion]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const updateCanvasSize = () => {
      const container = canvas.parentElement;
      if (container) {
        canvas.width = container.clientWidth;
        canvas.height = 400;
      }
    };
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);

    // Initialize nodes based on phase
    const initNodes = (phase: number): NetworkNode[] => {
      const nodeCount = phase === 1 ? 2 : phase === 2 ? 6 : 15;
      const nodes: NetworkNode[] = [];
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;

      for (let i = 0; i < nodeCount; i++) {
        const angle = (i / nodeCount) * Math.PI * 2;
        const radius = phase === 1 ? 150 : phase === 2 ? 120 : 100;

        nodes.push({
          id: COMPANIES[i] || `Node-${i}`,
          x: centerX + Math.cos(angle) * radius + (Math.random() - 0.5) * 20,
          y: centerY + Math.sin(angle) * radius + (Math.random() - 0.5) * 20,
          vx: (Math.random() - 0.5) * 0.2,
          vy: (Math.random() - 0.5) * 0.2,
          phase,
          connections: [],
        });
      }

      // Add connections based on phase
      if (phase === 1) {
        nodes[0].connections = [nodes[1].id];
      } else if (phase === 2) {
        // Mesh connections
        nodes.forEach((node, i) => {
          const neighbors = [(i + 1) % nodeCount, (i + 2) % nodeCount];
          node.connections = neighbors.map(n => nodes[n].id);
        });
      } else {
        // Dense mesh
        nodes.forEach((node, i) => {
          const connectionCount = Math.floor(Math.random() * 3) + 2;
          for (let j = 0; j < connectionCount; j++) {
            const targetIdx = (i + j + 1) % nodeCount;
            if (!node.connections.includes(nodes[targetIdx].id)) {
              node.connections.push(nodes[targetIdx].id);
            }
          }
        });
      }

      return nodes;
    };

    let nodes = initNodes(currentPhase);
    let animationId: number;
    let frame = 0;

    const getPhaseColor = (phase: number) => {
      if (phase === 1) return 'rgba(59, 130, 246, 0.6)'; // Blue
      if (phase === 2) return 'rgba(34, 197, 94, 0.6)'; // Green
      return 'rgba(234, 179, 8, 0.6)'; // Gold
    };

    const draw = () => {
      // Clear canvas
      ctx.fillStyle = 'rgba(8, 8, 8, 0.9)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      if (nodes.length === 0) {
        animationId = requestAnimationFrame(draw);
        return;
      }

      const phaseColor = getPhaseColor(currentPhase);

      // Update positions with gentle physics
      if (frame % 2 === 0) { // Throttle updates
        nodes.forEach((node) => {
          // Gentle random movement
          node.x += node.vx;
          node.y += node.vy;

          // Soft boundary
          if (node.x < 50 || node.x > canvas.width - 50) node.vx *= -0.8;
          if (node.y < 50 || node.y > canvas.height - 50) node.vy *= -0.8;

          // Clamp position
          node.x = Math.max(30, Math.min(canvas.width - 30, node.x));
          node.y = Math.max(30, Math.min(canvas.height - 30, node.y));
        });
      }

      // Draw connections
      ctx.strokeStyle = phaseColor;
      ctx.lineWidth = 2;
      nodes.forEach((node) => {
        node.connections.forEach((targetId) => {
          const target = nodes.find(n => n.id === targetId);
          if (target) {
            ctx.beginPath();
            ctx.moveTo(node.x, node.y);
            ctx.lineTo(target.x, target.y);
            ctx.stroke();
          }
        });
      });

      // Draw nodes
      nodes.forEach((node) => {
        // Outer circle
        ctx.beginPath();
        ctx.arc(node.x, node.y, 20, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(8, 8, 8, 0.8)';
        ctx.fill();
        ctx.strokeStyle = phaseColor;
        ctx.lineWidth = 2;
        ctx.stroke();

        // Inner dot
        ctx.beginPath();
        ctx.arc(node.x, node.y, 8, 0, Math.PI * 2);
        ctx.fillStyle = phaseColor;
        ctx.fill();

        // Label
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(node.id, node.x, node.y + 35);
      });

      // Phase label
      ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
      ctx.font = '14px "JetBrains Mono", monospace';
      ctx.textAlign = 'left';
      const phaseLabel = currentPhase === 1 ? 'Phase 1: Internal' :
                         currentPhase === 2 ? 'Phase 2: Bilateral' :
                         'Phase 3: Standard';
      ctx.fillText(phaseLabel, 20, 30);

      frame++;
      animationId = requestAnimationFrame(draw);
    };

    // Re-init nodes when phase changes
    if (currentPhase > 0) {
      nodes = initNodes(currentPhase);
      frame = 0;
    }

    draw();

    return () => {
      window.removeEventListener('resize', updateCanvasSize);
      cancelAnimationFrame(animationId);
    };
  }, [currentPhase, prefersReducedMotion]);

  return (
    <div ref={containerRef} className="w-full my-8">
      <canvas
        ref={canvasRef}
        className="w-full border border-white/10 bg-black/20"
        style={{ height: '400px' }}
      />
    </div>
  );
}
