import { motion } from 'framer-motion';

interface StepHeaderProps {
  number: number;
  title: string;
  subtitle: string;
}

export function StepHeader({ number, title, subtitle }: StepHeaderProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="space-y-2"
    >
      <div className="flex items-center gap-3">
        <span className="flex items-center justify-center w-8 h-8 border-2 border-white/20 text-muted/70 font-mono text-sm">
          {number}
        </span>
        <h3 className="text-2xl font-medium text-white/90">{title}</h3>
      </div>
      <p className="text-muted/60 text-base leading-relaxed pl-11">
        {subtitle}
      </p>
    </motion.div>
  );
}
