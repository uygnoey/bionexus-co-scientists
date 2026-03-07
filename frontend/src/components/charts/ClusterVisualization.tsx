'use client'

import { useRef, useEffect, useState } from 'react'
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from 'recharts'

interface ClusterVisualizationProps {
  hypotheses: any[]
  clusters: any[]
}

const COLORS = [
  '#6366f1', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b',
  '#ef4444', '#ec4899', '#14b8a6', '#84cc16', '#f97316',
]

export default function ClusterVisualization({
  hypotheses,
  clusters,
}: ClusterVisualizationProps) {
  const [zoom, setZoom] = useState(1)

  // Prepare scatter data
  const scatterData = hypotheses.map((hyp, idx) => {
    const clusterId = hyp.cluster_id ?? 0
    
    return {
      x: hyp.score?.novelty || 0,
      y: hyp.score?.feasibility || 0,
      z: hyp.score?.impact || 50,
      name: `H${idx + 1}`,
      cluster: clusterId,
      id: hyp.id,
      text: hyp.text,
    }
  })

  // Group by cluster
  const clusterGroups = clusters.map((cluster) => {
    const clusterHypotheses = scatterData.filter(
      (d) => d.cluster === cluster.cluster_id
    )
    return {
      clusterId: cluster.cluster_id,
      data: clusterHypotheses,
      color: COLORS[cluster.cluster_id % COLORS.length],
      name: `Cluster ${cluster.cluster_id + 1} (${cluster.size})`,
    }
  })

  const handleZoomIn = () => setZoom((prev) => Math.min(prev * 1.2, 3))
  const handleZoomOut = () => setZoom((prev) => Math.max(prev / 1.2, 0.5))
  const handleResetZoom = () => setZoom(1)

  return (
    <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-white">
          🎯 Cluster Visualization
        </h3>
        
        <div className="flex gap-2">
          <button
            onClick={handleZoomIn}
            className="px-3 py-1 bg-primary/20 text-primary rounded text-sm hover:bg-primary/30 transition"
            title="Zoom In"
          >
            🔍+
          </button>
          <button
            onClick={handleZoomOut}
            className="px-3 py-1 bg-primary/20 text-primary rounded text-sm hover:bg-primary/30 transition"
            title="Zoom Out"
          >
            🔍−
          </button>
          <button
            onClick={handleResetZoom}
            className="px-3 py-1 bg-primary/20 text-primary rounded text-sm hover:bg-primary/30 transition"
          >
            Reset
          </button>
        </div>
      </div>

      <div style={{ transform: `scale(${zoom})`, transformOrigin: 'center' }}>
        <ResponsiveContainer width="100%" height={500}>
          <ScatterChart margin={{ top: 20, right: 30, bottom: 40, left: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis
              type="number"
              dataKey="x"
              name="Novelty"
              stroke="rgba(255,255,255,0.6)"
              label={{
                value: 'Novelty Score →',
                position: 'insideBottom',
                offset: -10,
                style: { fill: 'rgba(255,255,255,0.8)' },
              }}
              domain={[0, 100]}
            />
            <YAxis
              type="number"
              dataKey="y"
              name="Feasibility"
              stroke="rgba(255,255,255,0.6)"
              label={{
                value: '← Feasibility Score',
                angle: -90,
                position: 'insideLeft',
                style: { fill: 'rgba(255,255,255,0.8)' },
              }}
              domain={[0, 100]}
            />
            <ZAxis type="number" dataKey="z" range={[50, 400]} name="Impact" />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              contentStyle={{
                backgroundColor: 'rgba(0, 0, 0, 0.9)',
                border: '1px solid rgba(255, 255, 255, 0.2)',
                borderRadius: '8px',
                color: 'white',
              }}
              content={({ payload }) => {
                if (!payload || payload.length === 0) return null
                const data = payload[0].payload
                return (
                  <div className="p-3">
                    <p className="font-semibold mb-1">{data.name}</p>
                    <p className="text-sm">Novelty: {data.x?.toFixed(1)}</p>
                    <p className="text-sm">Feasibility: {data.y?.toFixed(1)}</p>
                    <p className="text-sm">Impact: {data.z?.toFixed(1)}</p>
                    <p className="text-xs text-white/60 mt-2">{data.text?.slice(0, 80)}...</p>
                  </div>
                )
              }}
            />
            <Legend
              wrapperStyle={{ color: 'white' }}
              verticalAlign="top"
              height={36}
            />

            {clusterGroups.map((group) => (
              <Scatter
                key={group.clusterId}
                name={group.name}
                data={group.data}
                fill={group.color}
                shape="circle"
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-4 text-sm text-white/70">
        <div>
          <p className="font-semibold text-white mb-1">Legend:</p>
          <p>• X-axis: Novelty (참신성)</p>
          <p>• Y-axis: Feasibility (실현가능성)</p>
          <p>• Circle size: Impact (영향력)</p>
        </div>
        <div>
          <p className="font-semibold text-white mb-1">Clusters:</p>
          {clusters.map((cluster) => (
            <p key={cluster.cluster_id}>
              • Cluster {cluster.cluster_id + 1}: {cluster.size} hypotheses
            </p>
          ))}
        </div>
      </div>
    </div>
  )
}
