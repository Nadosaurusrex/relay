import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

const objections = [
  {
    icon: '👔',
    role: 'Compliance Officer',
    quote: 'How do we audit every decision this agent makes?',
  },
  {
    icon: '🔒',
    role: 'Security Team',
    quote: 'What stops it from approving a $500K charge by mistake?',
  },
  {
    icon: '📋',
    role: 'Procurement',
    quote: 'We need SOC 2 evidence that policies are enforced',
  },
];

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2,
    },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
};

const itemStatic = {
  hidden: { opacity: 1, y: 0 },
  show: { opacity: 1, y: 0 },
};

export function EnterpriseObjections() {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mediaQuery.matches);

    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  return (
    <motion.div
      className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto"
      variants={container}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, margin: '-100px' }}
    >
      {objections.map((objection, index) => (
        <motion.div
          key={index}
          variants={prefersReducedMotion ? itemStatic : item}
          className="backdrop-blur-lg bg-black/40 border border-white/10 border-l-4 border-l-red-400/40 rounded-lg p-6 space-y-4 hover:bg-white/8 hover:border-white/20 transition-colors"
        >
          <div className="text-3xl">{objection.icon}</div>
          <div className="text-xs font-medium text-red-400/60 uppercase tracking-wide">
            Objection
          </div>
          <blockquote className="text-base font-medium text-red-300/90 leading-relaxed">
            "{objection.quote}"
          </blockquote>
          <div className="inline-block px-2 py-1 rounded bg-white/5 text-xs text-muted/80">
            {objection.role}
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
