import { Button } from './ui/button';

export function Hero() {
  const scrollToWaitlist = () => {
    document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20">
      <div className="max-w-4xl w-full space-y-12">
        {/* Main Content */}
        <div className="space-y-8">
          <h1 className="text-5xl md:text-7xl font-normal leading-tight tracking-tight">
            DocuSign for
            <br />
            Machine-to-Machine
            <br />
            Reasoning
          </h1>

          <p className="text-xl text-muted max-w-2xl">
            When agents negotiate across companies, who signs?
          </p>
        </div>

        {/* CTA */}
        <div className="flex gap-4">
          <Button onClick={scrollToWaitlist}>
            Join the Standard
          </Button>
          <Button
            variant="ghost"
            onClick={() => window.open('https://github.com/your-org/relay', '_blank')}
          >
            Read Documentation
          </Button>
        </div>
      </div>
    </section>
  );
}
