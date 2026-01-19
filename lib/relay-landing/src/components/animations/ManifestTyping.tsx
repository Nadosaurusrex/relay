import { useState, useEffect } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

const MANIFESTS = [
  {
    label: 'Payment',
    code: `{
  "agent_id": "procurement-001",
  "action": "create_payment",
  "amount": 4999,
  "recipient": "vendor-xyz"
}`
  },
  {
    label: 'Termination',
    code: `{
  "agent_id": "infra-002",
  "action": "terminate_instance",
  "instance_id": "i-abc123",
  "reason": "cost_optimization"
}`
  },
  {
    label: 'API Key',
    code: `{
  "agent_id": "devops-003",
  "action": "create_api_key",
  "service": "github",
  "scope": ["read", "write"]
}`
  },
  {
    label: 'Contract',
    code: `{
  "agent_id": "legal-004",
  "action": "sign_contract",
  "contract_id": "NDA-2024-Q1",
  "amount": 250000
}`
  }
];

export function ManifestTyping() {
  const [selected, setSelected] = useState(0);
  const [charCount, setCharCount] = useState(0);
  const prefersReducedMotion = useReducedMotion();

  const currentCode = MANIFESTS[selected].code;

  useEffect(() => {
    if (prefersReducedMotion) {
      setCharCount(currentCode.length);
      return;
    }

    // Reset and type out when selection changes
    setCharCount(0);
    const interval = setInterval(() => {
      setCharCount((prev) => {
        if (prev >= currentCode.length) {
          clearInterval(interval);
          return prev;
        }
        return prev + 1;
      });
    }, 30);

    return () => clearInterval(interval);
  }, [selected, currentCode.length, prefersReducedMotion]);

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {MANIFESTS.map((manifest, i) => (
          <button
            key={i}
            onClick={() => setSelected(i)}
            className={`px-4 py-2 border font-mono text-sm transition-colors ${
              selected === i
                ? 'border-white/30 bg-white/5 text-white'
                : 'border-white/10 text-muted hover:border-white/20'
            }`}
          >
            {manifest.label}
          </button>
        ))}
      </div>
      <div className="border border-white/10 p-6 bg-black/20 font-mono text-xs">
        <pre className="text-white/80">
          {currentCode.slice(0, charCount)}
          {!prefersReducedMotion && charCount < currentCode.length && (
            <span className="animate-pulse">|</span>
          )}
        </pre>
      </div>
    </div>
  );
}
