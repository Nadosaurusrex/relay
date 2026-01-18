export function Footer() {
  return (
    <footer className="px-6 py-12 border-t border-white/10 mt-20">
      <div className="max-w-4xl mx-auto flex flex-col md:flex-row justify-between gap-8 text-sm text-muted">
        <div>
          <div className="font-bold text-white mb-2">RELAY</div>
          <div>Accountability infrastructure for AI agents</div>
        </div>

        <div className="flex gap-8">
          <a
            href="https://github.com/your-org/relay"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-white transition-colors"
          >
            GitHub
          </a>
          <a
            href="/docs"
            className="hover:text-white transition-colors"
          >
            Docs
          </a>
          <a
            href="https://twitter.com/relay"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-white transition-colors"
          >
            Twitter
          </a>
        </div>
      </div>
    </footer>
  );
}
