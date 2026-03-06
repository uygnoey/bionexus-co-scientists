export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-white mb-4">
          🧬 BioNexus Co-scientists
        </h1>
        <p className="text-xl text-white/80 mb-8">
          AI-powered scientific hypothesis generation using multi-agent systems
        </p>
        <div className="flex gap-4 justify-center">
          <a
            href="/hypotheses"
            className="px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg text-white hover:bg-white/20 transition"
          >
            Generate Hypotheses
          </a>
          <a
            href="/papers"
            className="px-6 py-3 bg-white/10 backdrop-blur-md border border-white/20 rounded-lg text-white hover:bg-white/20 transition"
          >
            Browse Papers
          </a>
        </div>
      </div>
    </main>
  )
}
