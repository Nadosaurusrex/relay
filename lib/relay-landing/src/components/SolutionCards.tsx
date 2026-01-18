export function SolutionCards() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20 border-t border-white/10">
      <div className="max-w-4xl w-full space-y-16">
        <h2 className="text-4xl md:text-5xl font-normal">
          How it works
        </h2>

        <div className="space-y-12">
          {/* 1. Policy Gateway */}
          <div className="space-y-3">
            <h3 className="text-xl">01 — Policy Gateway</h3>
            <p className="text-muted max-w-2xl">
              OPA-based policies enforce rules outside the LLM context.
              No prompt injection can override code-based constraints.
            </p>
          </div>

          {/* 2. Cryptographic Seals */}
          <div className="space-y-3">
            <h3 className="text-xl">02 — Cryptographic Seals</h3>
            <p className="text-muted max-w-2xl">
              Ed25519 signatures on every approved action.
              Downstream services can independently verify authorization.
            </p>
          </div>

          {/* 3. Audit Trail */}
          <div className="space-y-3">
            <h3 className="text-xl">03 — Immutable Audit Trail</h3>
            <p className="text-muted max-w-2xl">
              PostgreSQL ledger with database-level immutability.
              Every request, approval, and denial permanently logged.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
