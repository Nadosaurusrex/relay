export function ProblemViz() {
  return (
    <section className="min-h-screen flex items-center justify-center px-6 py-20">
      <div className="max-w-4xl w-full space-y-16">
        {/* Problem Statement */}
        <div className="space-y-6">
          <h2 className="text-4xl md:text-5xl font-normal">
            The €100K question
          </h2>
          <p className="text-xl text-muted max-w-2xl">
            Your procurement agent negotiates a €100K Salesforce deal.
            <br />
            When the CFO asks why, what's your answer?
          </p>
        </div>

        {/* Simple Visual */}
        <div className="border-l border-white/10 pl-8 space-y-4 text-muted">
          <p>→ No audit trail of the decision process</p>
          <p>→ Can't explain which policies were checked</p>
          <p>→ Unable to defend in compliance review</p>
        </div>

        {/* Solution Hint */}
        <p className="text-lg">
          Agents can communicate.
          <br />
          But without accountability infrastructure, they can't transact.
        </p>
      </div>
    </section>
  );
}
