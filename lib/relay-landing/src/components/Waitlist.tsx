import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';

export function Waitlist() {
  const [email, setEmail] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [framework, setFramework] = useState('');
  const [useCase, setUseCase] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const params = new URLSearchParams(window.location.search);
      const sheetsUrl = import.meta.env.VITE_SHEETS_URL;

      if (sheetsUrl) {
        await fetch(sheetsUrl, {
          method: 'POST',
          mode: 'no-cors',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'waitlist',
            email,
            company_name: companyName,
            framework,
            use_case: useCase,
            utm_source: params.get('utm_source') || '',
            utm_medium: params.get('utm_medium') || '',
            utm_campaign: params.get('utm_campaign') || '',
            timestamp: new Date().toISOString(),
          }),
        });
      }

      await new Promise(resolve => setTimeout(resolve, 1000));
      setIsSuccess(true);
      setEmail('');
      setCompanyName('');
      setFramework('');
      setUseCase('');
    } catch (err) {
      console.error('Waitlist submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="waitlist" className="min-h-screen flex items-center justify-center px-6 py-24 border-t border-white/10">
      <div className="max-w-md w-full space-y-10">
        {isSuccess ? (
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-medium text-white/90">You're on the list</h2>
            <p className="text-muted/60">We'll email you when Relay is ready.</p>
          </div>
        ) : (
          <>
            <div className="space-y-4 text-center">
              <h2 className="text-3xl md:text-4xl font-medium text-white/90">
                Start shipping agents to enterprise
              </h2>
              <p className="text-base text-muted/60 leading-relaxed">
                Free for development. Pay when you deploy to production.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3">
              <Input
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isSubmitting}
              />
              <Input
                type="text"
                placeholder="Company Name"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                required
                disabled={isSubmitting}
              />
              <Select
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                required
                disabled={isSubmitting}
              >
                <option value="">Framework</option>
                <option value="langchain">LangChain</option>
                <option value="crewai">CrewAI</option>
                <option value="autogpt">AutoGPT</option>
                <option value="custom">Custom</option>
                <option value="other">Other</option>
              </Select>
              <Select
                value={useCase}
                onChange={(e) => setUseCase(e.target.value)}
                required
                disabled={isSubmitting}
              >
                <option value="">Use Case</option>
                <option value="procurement">Procurement / Purchase Orders</option>
                <option value="contracts">Contract Approval</option>
                <option value="vendor">Vendor Management</option>
                <option value="financial">Financial Transactions</option>
                <option value="other">Other</option>
              </Select>
              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? 'Submitting...' : 'Get Early Access'}
              </Button>
            </form>
          </>
        )}
      </div>
    </section>
  );
}
