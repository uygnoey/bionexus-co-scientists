'use client'

import { useState } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from 'recharts'

interface HypothesisScoreChartProps {
  hypotheses: any[]
}

export default function HypothesisScoreChart({ hypotheses }: HypothesisScoreChartProps) {
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null)

  const chartData = hypotheses.map((hyp, idx) => ({
    name: `H${idx + 1}`,
    novelty: hyp.score?.novelty || 0,
    feasibility: hyp.score?.feasibility || 0,
    impact: hyp.score?.impact || 0,
    overall: hyp.score?.overall || 0,
    id: hyp.id,
  }))

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white">📊 Hypothesis Scores</h3>
        {zoomDomain && (
          <button
            onClick={() => setZoomDomain(null)}
            className="px-3 py-1 bg-primary/20 text-primary rounded text-sm hover:bg-primary/30 transition"
          >
            Reset Zoom
          </button>
        )}
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
          <XAxis
            dataKey="name"
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke="rgba(255,255,255,0.6)"
            style={{ fontSize: '12px' }}
            domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.2)',
              borderRadius: '8px',
              color: 'white',
            }}
          />
          <Legend
            wrapperStyle={{ color: 'white' }}
            iconType="square"
          />
          <Bar dataKey="novelty" fill="#6366f1" name="Novelty" />
          <Bar dataKey="feasibility" fill="#8b5cf6" name="Feasibility" />
          <Bar dataKey="impact" fill="#06b6d4" name="Impact" />
          <Bar dataKey="overall" fill="#10b981" name="Overall" />
          
          {/* Brush for zooming */}
          <Brush
            dataKey="name"
            height={30}
            stroke="rgba(255,255,255,0.5)"
            fill="rgba(255,255,255,0.1)"
          />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-4 text-sm text-white/60">
        <p>💡 Tip: Use the brush at the bottom to zoom into specific hypotheses</p>
      </div>
    </div>
  )
}
