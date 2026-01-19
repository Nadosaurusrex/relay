import { motion } from 'framer-motion';
import { useState, useEffect } from 'react';

const policyCode = `allow if {
  input.action == "charge_card"
  input.amount < 5000
  input.user.role == "agent"
}`;

export function PolicySnippet() {
  const [displayedCode, setDisplayedCode] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < policyCode.length) {
      const timeout = setTimeout(() => {
        setDisplayedCode(prev => prev + policyCode[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 30);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex]);

  // Syntax highlighting helper
  const renderCodeWithHighlighting = (code: string) => {
    const lines = code.split('\n');
    return lines.map((line, lineIndex) => {
      // Highlight keywords
      let highlightedLine = line
        .replace(/(allow|if)/g, '<span class="text-blue-400">$1</span>')
        .replace(/(input\.\w+|==|<)/g, '<span class="text-purple-400">$1</span>')
        .replace(/("[\w_]+")/g, '<span class="text-green-400">$1</span>')
        .replace(/(\d+)/g, '<span class="text-green-400">$1</span>');

      return (
        <div key={lineIndex} className="flex">
          <span className="text-muted/40 select-none mr-2 text-right w-4 text-xs">
            {lineIndex + 1}
          </span>
          <span dangerouslySetInnerHTML={{ __html: highlightedLine }} />
        </div>
      );
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      className="backdrop-blur-lg bg-black/40 border border-white/10 rounded-lg p-3 font-mono text-xs overflow-x-auto"
    >
      <div className="space-y-0.5">
        {renderCodeWithHighlighting(displayedCode)}
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
          className="inline-block w-1.5 h-3 bg-blue-400 ml-1"
        />
      </div>
    </motion.div>
  );
}
