import { ManifestTyping } from './animations/ManifestTyping';

export function StandardComponents() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20 border-t border-white/10">
      <div className="max-w-4xl w-full space-y-16">
        <h2 className="text-4xl md:text-5xl font-normal">
          How it works
        </h2>

        <div className="space-y-12">
          <div className="space-y-4">
            <h3 className="text-xl">Decision Intent</h3>
            <p className="text-muted max-w-2xl">
              Every agent action becomes a signed manifest
            </p>
            <ManifestTyping />
          </div>

          <div className="space-y-3">
            <h3 className="text-xl">Cryptographic Seals</h3>
            <p className="text-muted max-w-2xl">
              Ed25519 signatures from both parties
            </p>
          </div>

          <div className="space-y-3">
            <h3 className="text-xl">Audit Trail</h3>
            <p className="text-muted max-w-2xl">
              Immutable ledger for every transaction
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
