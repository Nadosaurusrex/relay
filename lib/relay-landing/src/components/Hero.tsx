import { Button } from './ui/button';

export function Hero() {
  const scrollToWaitlist = () => {
    document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToPlayground = () => {
    document.getElementById('playground')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-24">
      <div className="max-w-4xl w-full space-y-10">
        {/* Main Content */}
        <div className="space-y-6">
          <h1 className="text-4xl md:text-6xl font-medium leading-tight tracking-tight text-white/95">
            Ship agents to enterprises
            <br />
            without building custom governance
          </h1>

          <p className="text-lg text-muted/70 max-w-2xl leading-relaxed">
            Policy enforcement and audit trails for AI agents that handle real transactions
          </p>

          <p className="text-sm text-muted/60 max-w-2xl leading-relaxed">
            Works with LangChain, CrewAI, AutoGPT, or any custom framework—protect actions in 3 lines of code
          </p>
        </div>

        {/* CTA */}
        <div className="flex gap-3 pt-2">
          <Button onClick={scrollToWaitlist}>
            Start Free
          </Button>
          <Button
            variant="ghost"
            onClick={scrollToPlayground}
          >
            View Demo
          </Button>
        </div>
      </div>
    </section>
  );
}
