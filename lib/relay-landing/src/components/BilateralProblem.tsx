import { TrustBarrierViz } from './animations/TrustBarrierViz';

export function BilateralProblem() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20">
      <div className="max-w-4xl w-full space-y-16">
        <h2 className="text-4xl md:text-5xl font-normal">
          The trust barrier
        </h2>

        <TrustBarrierViz />
      </div>
    </section>
  );
}
