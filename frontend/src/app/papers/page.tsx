'use client'

import { useState } from 'react'

export default function PapersPage() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [papers, setPapers] = useState<any[]>([])

  const handleSearch = async () => {
    if (!query.trim()) {
      alert('Please enter a search query')
      return
    }

    setLoading(true)
    setPapers([])

    try {
      const response = await fetch(
        `http://localhost:8000/api/papers/search?query=${encodeURIComponent(query)}&max_results=10`
      )

      if (!response.ok) {
        throw new Error('Failed to search papers')
      }

      const data = await response.json()
      setPapers(data)
    } catch (error) {
      console.error('Error:', error)
      alert('Error searching papers. Check console for details.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">
          📚 Browse Papers
        </h1>

        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 mb-8">
          <label className="block text-white text-sm font-medium mb-2">
            Search arXiv
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="quantum computing, machine learning, etc."
              className="flex-1 px-4 py-2 rounded-lg bg-white/5 border border-white/20 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/80 transition disabled:opacity-50"
            >
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>
        </div>

        {papers.length > 0 && (
          <div className="space-y-4">
            <p className="text-white/80 mb-4">
              Found {papers.length} papers
            </p>

            {papers.map((paper) => (
              <div
                key={paper.arxiv_id}
                className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6 hover:bg-white/15 transition"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-xl font-semibold text-white flex-1">
                    {paper.title}
                  </h3>
                  <a
                    href={paper.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-4 px-3 py-1 bg-primary/20 text-primary rounded-full text-sm hover:bg-primary/30 transition"
                  >
                    PDF
                  </a>
                </div>

                <p className="text-white/60 text-sm mb-2">
                  arXiv: {paper.arxiv_id} | {new Date(paper.published_date).toLocaleDateString()}
                </p>

                <p className="text-white/70 text-sm mb-3">
                  {paper.authors.slice(0, 3).join(', ')}
                  {paper.authors.length > 3 && ` +${paper.authors.length - 3} more`}
                </p>

                <p className="text-white/80">{paper.abstract}</p>

                {paper.categories && paper.categories.length > 0 && (
                  <div className="mt-3 flex gap-2 flex-wrap">
                    {paper.categories.map((cat: string) => (
                      <span
                        key={cat}
                        className="px-2 py-1 bg-secondary/20 text-secondary rounded text-xs"
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
