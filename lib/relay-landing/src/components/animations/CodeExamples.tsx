import { useReducedMotion } from '../../hooks/useReducedMotion';

const EXAMPLES = [
  {
    label: 'LangChain + ERP',
    framework: 'LangChain',
    provider: 'erp' as const,
    code: `# LangChain tool creating purchase orders
@protect(provider="erp", method="create_po")
def create_purchase_order(vendor: str, amount: int):
    erp.create_po(vendor, amount, dept="ops")`
  },
  {
    label: 'CrewAI + Legal',
    framework: 'CrewAI',
    provider: 'legal' as const,
    code: `# CrewAI agent approving contracts
@protect(provider="legal", method="approve_contract")
def approve_vendor_contract(value: int, duration: int):
    legal.approve(value, duration, status="approved")`
  },
  {
    label: 'Custom + CRM',
    framework: 'Custom',
    provider: 'crm' as const,
    code: `# Custom agent onboarding vendors
@protect(provider="crm", method="onboard_vendor")
def onboard_new_vendor(vendor_id: str, name: str):
    crm.create_vendor(vendor_id, name, terms="net30")`
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
