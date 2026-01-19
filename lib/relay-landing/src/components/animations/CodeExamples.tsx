import { useReducedMotion } from '../../hooks/useReducedMotion';

const EXAMPLES = [
  {
    label: 'AWS',
    provider: 'aws' as const,
    code: `@protect(provider="aws", method="terminate_instance")
def cleanup_instance(instance_id: str):
    ec2.terminate_instances([instance_id])`
  },
  {
    label: 'Salesforce',
    provider: 'salesforce' as const,
    code: `@protect(provider="salesforce", method="update_deal")
def close_deal(deal_id: str, amount: int):
    sf.Deal.update(deal_id, status="closed")`
  },
  {
    label: 'GitHub',
    provider: 'github' as const,
    code: `@protect(provider="github", method="merge_pr")
def merge_pull_request(repo: str, pr_number: int):
    github.pull_request(repo, pr_number).merge()`
  }
];

interface CodeExamplesProps {
  selected: number;
  onSelect: (index: number) => void;
  charCount: number;
}

export function CodeExamples({ selected, onSelect, charCount }: CodeExamplesProps) {
  const prefersReducedMotion = useReducedMotion();

  const currentCode = EXAMPLES[selected].code;

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {EXAMPLES.map((example, i) => (
          <button
            key={i}
            onClick={() => onSelect(i)}
            className={`px-4 py-2 border font-mono text-sm transition-colors ${
              selected === i
                ? 'border-white/30 bg-white/5 text-white'
                : 'border-white/10 text-muted hover:border-white/20'
            }`}
          >
            {example.label}
          </button>
        ))}
      </div>
      <div className="border border-white/10 p-8 bg-black/20 font-mono text-sm overflow-x-auto">
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

export { EXAMPLES };
