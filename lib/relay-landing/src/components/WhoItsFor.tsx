export function WhoItsFor() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-24 border-t border-white/10">
      <div className="max-w-3xl w-full space-y-16">
        <h2 className="text-3xl md:text-4xl font-medium text-white/90">
          Who uses this
        </h2>

        <div className="space-y-12 text-base text-muted/60 leading-relaxed">
          <div className="space-y-3">
            <p>You demo well. Enterprise likes it. Procurement asks how to audit it.</p>
            <p>6 months building governance infrastructure, or integrate Relay this afternoon.</p>
          </div>

          <div className="space-y-3">
            <p>CFO wants agents handling spend. Legal wants audit trails. Security wants policies that can't be prompt-injected.</p>
            <p>Relay is all three.</p>
          </div>

          <div className="pt-8 border-t border-white/10 space-y-3">
            <p>Agents are moving from demos to signing purchase orders.</p>
            <p>Governance is the difference between a contract and "maybe next quarter."</p>
          </div>
        </div>
      </div>
    </section>
  );
}
