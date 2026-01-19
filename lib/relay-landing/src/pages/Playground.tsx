import { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Button } from '../components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { EXAMPLES, type SimulationResult } from '../components/PlaygroundUI';

export function Playground() {
  const [selectedExample, setSelectedExample] = useState(0);
  const [code, setCode] = useState(EXAMPLES[0].code);
  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const currentExample = EXAMPLES[selectedExample];

  const handleExampleChange = (index: number) => {
    setSelectedExample(index);
    setCode(EXAMPLES[index].code);
    setResult(null);
  };

  const handleRun = async () => {
    setIsRunning(true);

    // Simulate API call with delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Generate mock result based on example
    const mockResult: SimulationResult = {
      decision: currentExample.expectedDecision,
      reason: currentExample.reason,
      seal: {
        manifest_id: `550e8400-e29b-41d4-a716-${Math.random().toString(36).substring(7)}`,
        signature: Array.from({ length: 128 }, () =>
          Math.floor(Math.random() * 16).toString(16)
        ).join(''),
        issued_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 5 * 60 * 1000).toISOString(),
      },
      auditEntry: {
        agent_id: 'agent-demo-001',
        action: currentExample.name.toLowerCase().replace(/\s+/g, '_'),
        decision: currentExample.expectedDecision,
        timestamp: new Date().toISOString(),
      },
    };

    setResult(mockResult);
    setIsRunning(false);
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Navigation */}
      <nav className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <a href="/" className="text-lg font-bold hover:text-primary transition-colors">
              ← RELAY
            </a>
            <span className="text-muted">Interactive Playground</span>
          </div>
          <div className="flex gap-6">
            <a
              href="https://github.com/your-org/relay"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted hover:text-white transition-colors"
            >
              GitHub
            </a>
            <a
              href="/docs"
              className="text-muted hover:text-white transition-colors"
            >
              Docs
            </a>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Example Selector */}
        <div className="mb-8">
          <h1 className="text-3xl font-normal mb-4">Try Relay Protection</h1>
          <div className="flex gap-2">
            {EXAMPLES.map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleChange(index)}
                className={`px-4 py-2 border font-mono text-sm transition-colors ${
                  selectedExample === index
                    ? 'border-white/30 bg-white/5 text-white'
                    : 'border-white/10 text-muted hover:border-white/20'
                }`}
              >
                {example.name}
              </button>
            ))}
          </div>
          <p className="text-muted mt-4">{currentExample.description}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: Code Editor + Policy */}
          <div className="space-y-6">
            {/* Code Editor */}
            <div>
              <h2 className="text-xl mb-3">Agent Code</h2>
              <div className="border border-white/10 rounded-lg overflow-hidden">
                <Editor
                  height="400px"
                  defaultLanguage="python"
                  value={code}
                  onChange={(value) => setCode(value || '')}
                  theme="vs-dark"
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: 'on',
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                  }}
                />
              </div>
            </div>

            {/* Policy Viewer */}
            <div>
              <h2 className="text-xl mb-3">Policy (Rego)</h2>
              <div className="border border-white/10 rounded-lg p-4 bg-black/40 font-mono text-sm overflow-x-auto">
                <pre className="text-muted/90">{currentExample.policy}</pre>
              </div>
            </div>

            {/* Run Button */}
            <Button
              onClick={handleRun}
              disabled={isRunning}
              className="w-full"
            >
              {isRunning ? 'Running...' : 'Run Protection Check'}
            </Button>
          </div>

          {/* Right Column: Results */}
          <div>
            <h2 className="text-xl mb-3">Results</h2>
            <AnimatePresence mode="wait">
              {result ? (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="space-y-4"
                >
                  {/* Decision */}
                  <div className="border border-white/10 rounded-lg p-6 bg-black/20">
                    <h3 className="text-lg font-semibold mb-3">Decision</h3>
                    <div className="flex items-center gap-3">
                      <span
                        className={`px-3 py-1 rounded text-sm font-semibold ${
                          result.decision === 'APPROVED'
                            ? 'bg-green-500/20 text-green-400'
                            : 'bg-red-500/20 text-red-400'
                        }`}
                      >
                        {result.decision}
                      </span>
                      {result.reason && (
                        <span className="text-muted text-sm">
                          {result.reason}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Seal */}
                  <div className="border border-white/10 rounded-lg p-6 bg-black/20">
                    <h3 className="text-lg font-semibold mb-3">Cryptographic Seal</h3>
                    <div className="space-y-2 font-mono text-xs text-muted/80">
                      <div>
                        <span className="text-muted">Manifest ID:</span>{' '}
                        {result.seal.manifest_id}
                      </div>
                      <div>
                        <span className="text-muted">Signature:</span>{' '}
                        <span className="break-all">
                          {result.seal.signature.substring(0, 64)}...
                        </span>
                      </div>
                      <div>
                        <span className="text-muted">Issued:</span>{' '}
                        {new Date(result.seal.issued_at).toLocaleString()}
                      </div>
                      <div>
                        <span className="text-muted">Expires:</span>{' '}
                        {new Date(result.seal.expires_at).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {/* Audit Entry */}
                  <div className="border border-white/10 rounded-lg p-6 bg-black/20">
                    <h3 className="text-lg font-semibold mb-3">Audit Log Entry</h3>
                    <div className="space-y-2 font-mono text-xs text-muted/80">
                      <div>
                        <span className="text-muted">Agent ID:</span>{' '}
                        {result.auditEntry.agent_id}
                      </div>
                      <div>
                        <span className="text-muted">Action:</span>{' '}
                        {result.auditEntry.action}
                      </div>
                      <div>
                        <span className="text-muted">Decision:</span>{' '}
                        <span
                          className={
                            result.auditEntry.decision === 'APPROVED'
                              ? 'text-green-400'
                              : 'text-red-400'
                          }
                        >
                          {result.auditEntry.decision}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted">Timestamp:</span>{' '}
                        {new Date(result.auditEntry.timestamp).toLocaleString()}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="placeholder"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="border border-white/10 rounded-lg p-12 bg-black/20 text-center text-muted"
                >
                  Click "Run Protection Check" to see results
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-12 border-t border-white/10 pt-8">
          <h2 className="text-2xl font-normal mb-4">How it works</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-muted">
            <div>
              <h3 className="text-white font-semibold mb-2">1. Agent Action</h3>
              <p className="text-sm">
                Agent attempts to perform a critical action like charging a card or terminating infrastructure
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">2. Policy Check</h3>
              <p className="text-sm">
                Relay evaluates the action against deterministic policies defined in Rego (not prompts)
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-2">3. Sealed + Logged</h3>
              <p className="text-sm">
                Decision is cryptographically signed and recorded in an immutable audit trail
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
