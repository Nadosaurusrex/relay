import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { useReducedMotion } from '../../hooks/useReducedMotion';

interface ApiJourneyProps {
  provider: 'aws' | 'salesforce' | 'github' | 'stripe' | 'erp' | 'legal' | 'crm';
}

const JOURNEY_STEPS = {
  erp: [
    { label: 'Agent Request', detail: 'create_po("Office Depot", 8500)' },
    { label: 'Policy Check', detail: 'amount < 10000 ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'PO created' },
  ],
  legal: [
    { label: 'Agent Request', detail: 'approve_contract(150000, 24)' },
    { label: 'Policy Check', detail: 'value >= 50000 ✗' },
    { label: 'Seal Denied', detail: 'Exceeds authority' },
    { label: 'Action Blocked', detail: 'Contract rejected' },
  ],
  crm: [
    { label: 'Agent Request', detail: 'onboard_vendor("VENDOR-12345")' },
    { label: 'Policy Check', detail: 'vendor in approved_list ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'Vendor onboarded' },
  ],
  stripe: [
    { label: 'Agent Request', detail: 'charge_card(4999, "salesforce")' },
    { label: 'Policy Check', detail: 'amount < 5000 ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'Payment charged' },
  ],
  aws: [
    { label: 'Agent Request', detail: 'terminate_instance(i-abc123)' },
    { label: 'Policy Check', detail: 'instance in region us-east-1 ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'Instance terminated' },
  ],
  salesforce: [
    { label: 'Agent Request', detail: 'update_deal(deal_123, closed)' },
    { label: 'Policy Check', detail: 'user has deal_close permission ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'Deal updated' },
  ],
  github: [
    { label: 'Agent Request', detail: 'merge_pr(repo, pr_456)' },
    { label: 'Policy Check', detail: 'PR has 2 approvals ✓' },
    { label: 'Seal Issued', detail: 'Ed25519 signature' },
    { label: 'Action Executed', detail: 'PR merged' },
  ],
};

export function ApiJourney({ provider }: ApiJourneyProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: false, amount: 0.3 });
  const prefersReducedMotion = useReducedMotion();

  const steps = JOURNEY_STEPS[provider];

  return (
    <div ref={ref} className="w-full py-4">
      <div className="flex flex-col md:flex-row items-center justify-between gap-8 md:gap-4">
        {steps.map((step, i) => (
          <div key={`${provider}-${i}`} className="flex items-center w-full md:w-auto">
            <motion.div
              className="flex flex-col items-center md:items-start w-full"
              initial={prefersReducedMotion ? {} : { opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.2, duration: 0.5 }}
            >
              {/* Step number */}
              <div className="flex items-center gap-4 w-full">
                <div className="flex items-center justify-center w-8 h-8 border border-white/30 text-white/60 font-mono text-sm">
                  {i + 1}
                </div>
                <div className="flex-1">
                  <div className="text-white text-sm mb-1">{step.label}</div>
                  <div className="text-muted text-xs font-mono">{step.detail}</div>
                </div>
              </div>
            </motion.div>

            {/* Arrow */}
            {i < steps.length - 1 && (
              <motion.div
                className="hidden md:block mx-4 text-white/20"
                initial={prefersReducedMotion ? {} : { opacity: 0, x: -10 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ delay: i * 0.2 + 0.3, duration: 0.3 }}
              >
                →
              </motion.div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
