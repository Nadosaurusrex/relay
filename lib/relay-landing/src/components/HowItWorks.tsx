export function HowItWorks() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20 border-t border-white/10">
      <div className="max-w-4xl w-full space-y-16">
        <div className="space-y-6">
          <h2 className="text-4xl md:text-5xl font-normal">
            Three lines of code
          </h2>
          <p className="text-xl text-muted">
            Add the decorator. That's it.
          </p>
        </div>

        {/* Code Example */}
        <div className="border border-white/10 p-8 bg-black/20 font-mono text-sm overflow-x-auto">
          <pre className="text-white/80">
{`from relay_sdk import protect

@protect(provider="stripe", method="create_payment")
def process_payment(amount: int, recipient: str):
    stripe.Payment.create(
        amount=amount,
        recipient=recipient
    )`}
          </pre>
        </div>

        <p className="text-muted">
          If your agent is compromised, your policies still hold.
        </p>
      </div>
    </section>
  );
}
