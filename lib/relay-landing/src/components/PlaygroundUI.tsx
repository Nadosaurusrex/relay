import { useState } from 'react';
import { Button } from './ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { LazyCodeEditor } from './LazyCodeEditor';

interface Example {
  name: string;
  description: string;
  code: string;
  policy: string;
  expectedDecision: 'APPROVED' | 'DENIED';
  reason?: string;
}

// Helper to extract parameters from code
function extractParameters(code: string): Record<string, any> {
  const params: Record<string, any> = {};

  // Extract function name from @protect decorator
  const protectMatch = code.match(/@protect\(provider="([^"]+)",\s*method="([^"]+)"\)/);
  if (protectMatch) {
    params.action = protectMatch[2];
  }

  // Extract function call parameters (looking for the test call)
  const patterns = [
    /amount[=:]\s*(\d+)/i,
    /contract_value[=:]\s*(\d+)/i,
    /vendor_id[=:]\s*"([^"]+)"/i,
  ];

  patterns.forEach(pattern => {
    const match = code.match(pattern);
    if (match) {
      const value = match[1];
      if (pattern.source.includes('amount')) {
        params.amount = parseInt(value, 10);
      } else if (pattern.source.includes('contract_value')) {
        params.contract_value = parseInt(value, 10);
      } else if (pattern.source.includes('vendor_id')) {
        params.vendor_id = value;
      }
    }
  });

  // Add default user role for all requests
  params.user = { role: 'agent' };

  return params;
}

// Helper to evaluate policy against parameters
function evaluatePolicy(params: Record<string, any>): { decision: 'APPROVED' | 'DENIED', reason?: string } {
  const input = params;

  // Purchase Order policy
  if (input.action === 'create_purchase_order') {
    if (input.amount < 10000 && input.user.role === 'agent') {
      return { decision: 'APPROVED' };
    } else if (input.amount >= 10000) {
      return { decision: 'DENIED', reason: 'PO exceeds $10K agent limit' };
    }
  }

  // Vendor Onboarding policy
  if (input.action === 'onboard_vendor') {
    const approvedVendors = ['VENDOR-12345', 'VENDOR-67890', 'VENDOR-11111'];
    if (input.vendor_id && approvedVendors.includes(input.vendor_id) && input.user.role === 'agent') {
      return { decision: 'APPROVED' };
    } else if (input.vendor_id && !approvedVendors.includes(input.vendor_id)) {
      return { decision: 'DENIED', reason: 'Vendor not in approved list' };
    }
  }

  // Contract Approval policy
  if (input.action === 'approve_contract') {
    if (input.contract_value < 50000 && input.user.role === 'agent') {
      return { decision: 'APPROVED' };
    } else if (input.contract_value >= 50000) {
      return { decision: 'DENIED', reason: 'Contract value exceeds agent authority' };
    }
  }

  // Default deny
  return { decision: 'DENIED', reason: 'No matching policy rule' };
}

export const EXAMPLES: Example[] = [
  {
    name: 'Purchase Order',
    description: 'Create purchase order under $10K (APPROVED)',
    code: `from relay_sdk import protect

@protect(provider="erp", method="create_purchase_order")
def create_po(vendor: str, amount: int, department: str):
    """Create a purchase order for vendor"""
    return erp.create_purchase_order(
        vendor=vendor,
        amount=amount,
        department=department,
        status="pending_approval"
    )

# Test: Create $8,500 PO for office supplies
result = create_po(
    vendor="Office Depot",
    amount=8500,
    department="Operations"
)`,
    policy: `package relay.policies.main

allow if {
  input.action == "create_purchase_order"
  input.amount < 10000
  input.user.role == "agent"
}

deny["PO exceeds $10K agent limit"] if {
  input.action == "create_purchase_order"
  input.amount >= 10000
}`,
    expectedDecision: 'APPROVED',
  },
  {
    name: 'Vendor Onboarding',
    description: 'Onboard pre-approved vendor (APPROVED)',
    code: `from relay_sdk import protect

@protect(provider="crm", method="onboard_vendor")
def onboard_vendor(vendor_name: str, vendor_id: str):
    """Onboard a new vendor to the system"""
    return crm.create_vendor_profile(
        name=vendor_name,
        vendor_id=vendor_id,
        status="active",
        payment_terms="net30"
    )

# Test: Onboard vendor from approved list
result = onboard_vendor(
    vendor_name="Acme Corp",
    vendor_id="VENDOR-12345"
)`,
    policy: `package relay.policies.main

# List of pre-approved vendors
approved_vendors := [
  "VENDOR-12345",
  "VENDOR-67890",
  "VENDOR-11111"
]

allow if {
  input.action == "onboard_vendor"
  input.vendor_id in approved_vendors
  input.user.role == "agent"
}

deny["Vendor not in approved list"] if {
  input.action == "onboard_vendor"
  not input.vendor_id in approved_vendors
}`,
    expectedDecision: 'APPROVED',
  },
  {
    name: 'Contract Approval',
    description: 'Approve contract exceeding authority (DENIED)',
    code: `from relay_sdk import protect

@protect(provider="legal", method="approve_contract")
def approve_contract(contract_value: int, duration_months: int):
    """Approve a vendor contract"""
    return legal.approve_contract(
        value=contract_value,
        duration=duration_months,
        approved_by="agent",
        status="approved"
    )

# Test: Attempt to approve $150K contract
result = approve_contract(
    contract_value=150000,
    duration_months=24
)`,
    policy: `package relay.policies.main

allow if {
  input.action == "approve_contract"
  input.contract_value < 50000
  input.user.role == "agent"
}

deny["Contract value exceeds agent authority"] if {
  input.action == "approve_contract"
  input.contract_value >= 50000
}`,
    expectedDecision: 'DENIED',
    reason: 'Contract value exceeds agent authority',
  },
];

export interface SimulationResult {
  decision: 'APPROVED' | 'DENIED';
  reason?: string;
  seal: {
    manifest_id: string;
    signature: string;
    issued_at: string;
    expires_at: string;
  };
  auditEntry: {
    agent_id: string;
    action: string;
    decision: string;
    timestamp: string;
  };
}

interface PlaygroundUIProps {
  variant?: 'full-page' | 'section';
  className?: string;
}

export function PlaygroundUI({ variant: _variant = 'section', className = '' }: PlaygroundUIProps) {
  const [selectedExample, setSelectedExample] = useState(0);
  const [code, setCode] = useState(EXAMPLES[0].code);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const currentExample = EXAMPLES[selectedExample];

  const handleExampleChange = (index: number) => {
    setSelectedExample(index);
    setCode(EXAMPLES[index].code);
    setResult(null);
  };

  const handleRun = async () => {
    setIsRunning(true);

    // Simulate API call with delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Extract parameters from the current code
    const params = extractParameters(code);

    // Evaluate policy against extracted parameters
    const evaluation = evaluatePolicy(params);

    // Generate result based on actual policy evaluation
    const mockResult: SimulationResult = {
      decision: evaluation.decision,
      reason: evaluation.reason,
      seal: {
        manifest_id: `550e8400-e29b-41d4-a716-${Math.random().toString(36).substring(7)}`,
        signature: Array.from({ length: 128 }, () =>
          Math.floor(Math.random() * 16).toString(16)
        ).join(''),
        issued_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
      },
      auditEntry: {
        agent_id: 'agent-demo-001',
        action: params.action || currentExample.name.toLowerCase().replace(/\s+/g, '_'),
        decision: evaluation.decision,
        timestamp: new Date().toISOString(),
      },
    };

    setResult(mockResult);
    setIsRunning(false);
  };

  return (
    <div className={className}>
      {/* Example Selector */}
      <div className="mb-12">
        <div className="flex flex-wrap gap-3 justify-center">
          {EXAMPLES.map((example, index) => (
            <button
              key={index}
              onClick={() => handleExampleChange(index)}
              className={`px-4 py-2.5 border font-mono text-sm transition-all ${
                selectedExample === index
                  ? 'border-white/30 bg-white/5 text-white shadow-sm'
                  : 'border-white/10 text-muted hover:border-white/20 hover:bg-white/5'
              }`}
            >
              {example.name}
            </button>
          ))}
        </div>
        <p className="text-muted/60 mt-4 text-center text-sm">{currentExample.description}</p>
      </div>

      {/* Three Column Layout: Code | Policy | Results */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Column 1: Agent Code */}
        <div>
          <h3 className="text-sm font-medium text-muted/80 mb-3 uppercase tracking-wide">Agent Code</h3>
          <div className="border border-white/10 overflow-hidden bg-black/20">
            <LazyCodeEditor
              height="450px"
              defaultLanguage="python"
              value={code}
              onChange={(value) => setCode(value || '')}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                readOnly: false,
              }}
            />
          </div>
        </div>

        {/* Column 2: Policy */}
        <div>
          <h3 className="text-sm font-medium text-muted/80 mb-3 uppercase tracking-wide">Policy (Rego)</h3>
          <div className="border border-white/10 p-4 bg-black/20 font-mono text-xs overflow-auto h-[450px]">
            <pre className="text-muted/70 whitespace-pre-wrap">{currentExample.policy}</pre>
          </div>
        </div>

        {/* Column 3: Results */}
        <div>
          <h3 className="text-sm font-medium text-muted/80 mb-3 uppercase tracking-wide">Results</h3>
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.3 }}
                className="space-y-3 h-[450px] overflow-auto"
              >
                {/* Decision */}
                <div className="border border-white/10 bg-white/5">
                  <div className="px-4 py-2.5 border-b border-white/10">
                    <h4 className="text-xs font-medium text-white/90 uppercase tracking-wide">Decision</h4>
                  </div>
                  <div className="px-4 py-3">
                    <div className="flex items-start gap-2 flex-col">
                      <span
                        className={`px-2.5 py-1 text-xs font-medium border ${
                          result.decision === 'APPROVED'
                            ? 'border-green-500/20 bg-green-500/10 text-green-400/90'
                            : 'border-amber-500/20 bg-amber-500/10 text-amber-400/90'
                        }`}
                      >
                        {result.decision}
                      </span>
                      {result.reason && (
                        <span className="text-muted/70 text-xs leading-relaxed">
                          {result.reason}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Seal */}
                <div className="border border-white/10 bg-white/5">
                  <div className="px-4 py-2.5 border-b border-white/10">
                    <h4 className="text-xs font-medium text-white/90 uppercase tracking-wide">Cryptographic Seal</h4>
                  </div>
                  <div className="px-4 py-3">
                    <dl className="space-y-2 font-mono text-xs">
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Manifest ID</dt>
                        <dd className="text-white/70">{result.seal.manifest_id}</dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Signature</dt>
                        <dd className="text-white/70 break-all">
                          {result.seal.signature.substring(0, 48)}...
                        </dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Issued</dt>
                        <dd className="text-white/70">
                          {new Date(result.seal.issued_at).toLocaleString()}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Expires</dt>
                        <dd className="text-white/70">
                          {new Date(result.seal.expires_at).toLocaleString()}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>

                {/* Audit Entry */}
                <div className="border border-white/10 bg-white/5">
                  <div className="px-4 py-2.5 border-b border-white/10">
                    <h4 className="text-xs font-medium text-white/90 uppercase tracking-wide">Audit Log Entry</h4>
                  </div>
                  <div className="px-4 py-3">
                    <dl className="space-y-2 font-mono text-xs">
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Agent ID</dt>
                        <dd className="text-white/70">{result.auditEntry.agent_id}</dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Action</dt>
                        <dd className="text-white/70">{result.auditEntry.action}</dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Decision</dt>
                        <dd className={`${
                          result.auditEntry.decision === 'APPROVED'
                            ? 'text-green-400/90'
                            : 'text-amber-400/90'
                        }`}>
                          {result.auditEntry.decision}
                        </dd>
                      </div>
                      <div>
                        <dt className="text-muted/60 text-[10px] uppercase tracking-wider mb-0.5">Timestamp</dt>
                        <dd className="text-white/70">
                          {new Date(result.auditEntry.timestamp).toLocaleString()}
                        </dd>
                      </div>
                    </dl>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="border border-white/10 p-8 bg-white/5 text-center text-muted/60 h-[450px] flex items-center justify-center"
              >
                <div className="text-sm">Click "Run Protection Check" to see results</div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Run Button - Centered below the columns */}
      <div className="flex justify-center mb-16">
        <Button
          onClick={handleRun}
          disabled={isRunning}
          className="px-8 py-3 text-base"
        >
          {isRunning ? 'Running Protection Check...' : '▶ Run Protection Check'}
        </Button>
      </div>

      {/* Info Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.4 }}
        className="mt-16 border-t border-white/10 pt-12"
      >
        <h3 className="text-xl font-medium mb-8 text-center text-white/90">How it works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="text-center"
          >
            <div className="text-muted/60 text-xs font-medium mb-2 uppercase tracking-wide">Step 1</div>
            <h4 className="text-white/90 font-medium mb-2">Agent Action</h4>
            <p className="text-sm text-muted/60 leading-relaxed">
              Agent attempts to perform a critical action like creating a purchase order or approving a contract
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.2 }}
            className="text-center"
          >
            <div className="text-muted/60 text-xs font-medium mb-2 uppercase tracking-wide">Step 2</div>
            <h4 className="text-white/90 font-medium mb-2">Policy Check</h4>
            <p className="text-sm text-muted/60 leading-relaxed">
              Relay evaluates the action against deterministic policies defined in Rego (not prompts)
            </p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="text-center"
          >
            <div className="text-muted/60 text-xs font-medium mb-2 uppercase tracking-wide">Step 3</div>
            <h4 className="text-white/90 font-medium mb-2">Sealed + Logged</h4>
            <p className="text-sm text-muted/60 leading-relaxed">
              Decision is cryptographically signed and recorded in an immutable audit trail
            </p>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
}
