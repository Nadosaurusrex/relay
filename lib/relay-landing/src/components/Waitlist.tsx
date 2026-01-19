import { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';

export function Waitlist() {
  const [email, setEmail] = useState('');
  const [companyName, setCompanyName] = useState('');
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
      setUseCase('');
    } catch (err) {
      console.error('Waitlist submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section id="waitlist" className="min-h-screen flex items-center justify-center px-6 py-20 border-t border-white/10">
      <div className="max-w-4xl w-full space-y-12">
        {isSuccess ? (
          <div className="text-center space-y-6">
            <h2 className="text-4xl font-normal">You're on the list</h2>
            <p className="text-muted">We'll email you when Relay is ready.</p>
          </div>
        ) : (
          <>
            <div className="space-y-6">
              <h2 className="text-4xl md:text-5xl font-normal">
                Get early access
              </h2>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 max-w-md">
              <Input
                type="email"
                placeholder="Company Email"
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
                value={useCase}
                onChange={(e) => setUseCase(e.target.value)}
                required
                disabled={isSubmitting}
              >
                <option value="">Use Case</option>
                <option value="procurement">Procurement</option>
                <option value="sales">Sales</option>
                <option value="legal">Legal</option>
                <option value="infrastructure">Infrastructure</option>
                <option value="other">Other</option>
              </Select>
              <Button type="submit" disabled={isSubmitting} className="w-full">
                {isSubmitting ? 'Joining...' : 'Join'}
              </Button>
            </form>
          </>
        )}
      </div>
    </section>
  );
}
