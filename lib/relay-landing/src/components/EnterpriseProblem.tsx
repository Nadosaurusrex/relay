import { EnterpriseObjections } from './animations/EnterpriseObjections';

export function EnterpriseProblem() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-24 border-t border-white/10">
      <div className="max-w-6xl w-full space-y-16">
        <div className="space-y-4">
          <div className="text-xs font-medium text-muted/60 uppercase tracking-wider text-center">
            The Reality
          </div>
          <h2 className="text-3xl md:text-4xl font-medium text-center leading-tight text-white/90">
            Your agent works in dev. Enterprise won't buy it in prod.
          </h2>
          <p className="text-base text-muted/60 text-center max-w-2xl mx-auto leading-relaxed">
            Every AI agent builder hits these objections.
          </p>
        </div>

        <EnterpriseObjections />
      </div>
    </section>
  );
}
