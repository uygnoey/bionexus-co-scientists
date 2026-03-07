'use client'

import { useState } from 'react'
import dynamic from 'next/dynamic'

// Dynamic import to avoid SSR issues with charts
const HypothesisScoreChart = dynamic(
  () => import('../../components/charts/HypothesisScoreChart'),
  { ssr: false }
)
const ClusterVisualization = dynamic(
  () => import('../../components/charts/ClusterVisualization'),
  { ssr: false }
)

export default function HypothesesPage() {
  const [paperIds, setPaperIds] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)

  const handleGenerate = async () => {
    if (!paperIds.trim()) {
      alert('Please enter paper IDs')
      return
    }

    setLoading(true)
    setResults(null)

    try {
      const ids = paperIds.split(',').map(id => id.trim())
      
      const response = await fetch('http://localhost:9000/api/hypotheses/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          paper_ids: ids,
          max_hypotheses: 5,
          debate_rounds: 3,
          clustering: true,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to generate hypotheses')
      }

      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error('Error:', error)
      alert('Error generating hypotheses. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">
          🧬 Generate Hypotheses
        </h1>

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 mb-8">
          <label className="block text-white text-sm font-medium mb-2">
            arXiv Paper IDs (comma-separated)
          </label>
          <input
            type="text"
            value={paperIds}
            onChange={(e) => setPaperIds(e.target.value)}
            placeholder="2301.12345, 2302.67890"
            className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary"
          />
          
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="mt-4 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/80 transition disabled:opacity-50"
          >
            {loading ? 'Generating...' : 'Generate Hypotheses'}
          </button>
        </div>

        {results && (
          <div className="space-y-4">
            <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6">
              <h2 className="text-2xl font-bold text-white mb-4">Results</h2>
              <p className="text-white/80">
                Generated {results.hypotheses?.length || 0} hypotheses in{' '}
                {results.generation_time_seconds?.toFixed(2)}s
              </p>
              <p className="text-white/80">
                Clusters: {results.clusters?.length || 0}
              </p>
            </div>

            {/* Score Chart */}
            {results.hypotheses && results.hypotheses.length > 0 && (
              <HypothesisScoreChart hypotheses={results.hypotheses} />
            )}

            {/* Cluster Visualization */}
            {results.clusters && results.clusters.length > 0 && (
              <ClusterVisualization
                hypotheses={results.hypotheses}
                clusters={results.clusters}
              />
            )}

            {results.hypotheses?.map((hyp: any, idx: number) => (
              <div
                key={hyp.id}
                className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 hover:bg-white/15 transition"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-xl font-semibold text-white">
                    Hypothesis #{idx + 1}
                  </h3>
                  <span className="px-3 py-1 bg-primary/20 text-primary rounded-full text-sm">
                    Score: {hyp.score?.overall?.toFixed(1)}
                  </span>
                </div>
                <p className="text-white/90 mb-4">{hyp.text}</p>
                <p className="text-white/70 text-sm">{hyp.description}</p>
                
                <div className="mt-4 flex gap-4 text-sm text-white/60">
                  <span>Novelty: {hyp.score?.novelty?.toFixed(1)}</span>
                  <span>Feasibility: {hyp.score?.feasibility?.toFixed(1)}</span>
                  <span>Impact: {hyp.score?.impact?.toFixed(1)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
