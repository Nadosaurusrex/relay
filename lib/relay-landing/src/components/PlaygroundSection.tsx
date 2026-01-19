import { motion } from 'framer-motion';
import { PlaygroundUI } from './PlaygroundUI';

export function PlaygroundSection() {
  return (
    <section
      id="playground"
      className="min-h-screen flex items-center justify-center px-6 py-12 border-t border-white/10"
    >
      <div className="max-w-7xl w-full space-y-8">
        {/* Heading */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="space-y-2 text-center"
        >
          <div className="text-xs font-medium text-muted/60 uppercase tracking-wider">
            Interactive Demo
          </div>
          <h2 className="text-2xl md:text-3xl font-medium text-white/90">
            Try It Yourself
          </h2>
          <p className="text-sm text-muted/60 max-w-2xl mx-auto leading-relaxed">
            See how Relay validates agent actions against deterministic policies in real-time.
          </p>
        </motion.div>

        {/* Playground UI */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <PlaygroundUI variant="section" />
        </motion.div>
      </div>
    </section>
  );
}
