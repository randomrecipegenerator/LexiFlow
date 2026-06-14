import { useState, useMemo } from 'react'

interface GraphNode {
  id: string
  label: string
  type: 'witness' | 'exhibit' | 'transcript' | 'contradiction'
  riskScore?: number
}

interface GraphEdge {
  source: string
  target: string
  label: string
  weight: number
}

const sampleNodes: GraphNode[] = [
  { id: 'w1', label: 'Dr. Sarah Chen', type: 'witness', riskScore: 72 },
  { id: 'w2', label: 'James Morrison', type: 'witness', riskScore: 45 },
  { id: 'w4', label: 'Dr. Michael Park', type: 'witness', riskScore: 88 },
  { id: 'e1', label: 'Nursing Flow Sheet', type: 'exhibit' },
  { id: 'e2', label: 'Prelim Assessment', type: 'exhibit' },
  { id: 'e3', label: 'ACOG Bulletin No.183', type: 'exhibit' },
  { id: 't1', label: 'Chen Dep. Day 2', type: 'transcript' },
  { id: 't2', label: 'Park Dep. Day 1', type: 'transcript' },
  { id: 'c1', label: 'Intubation Timing', type: 'contradiction' },
  { id: 'c2', label: 'Medication Conflict', type: 'contradiction' },
]

const sampleEdges: GraphEdge[] = [
  { source: 'w1', target: 't1', label: 'deposed', weight: 1 },
  { source: 'w1', target: 'e1', label: 'contradicts', weight: 0.8 },
  { source: 'w1', target: 'c1', label: 'flagged', weight: 0.9 },
  { source: 'w4', target: 't2', label: 'deposed', weight: 1 },
  { source: 'w4', target: 'e2', label: 'contradicts', weight: 0.7 },
  { source: 'w4', target: 'e3', label: 'contradicts', weight: 0.9 },
  { source: 'w4', target: 'c2', label: 'flagged', weight: 0.9 },
  { source: 'c1', target: 'e1', label: 'evidence', weight: 0.8 },
  { source: 'c2', target: 'e2', label: 'evidence', weight: 0.7 },
  { source: 'w2', target: 't1', label: 'mentioned', weight: 0.4 },
]

const COLORS: Record<string, string> = {
  witness: '#3b82f6',
  exhibit: '#c9a84c',
  transcript: '#64748b',
  contradiction: '#ef4444',
}

const RADIUS: Record<string, number> = {
  witness: 28,
  exhibit: 22,
  transcript: 18,
  contradiction: 16,
}

export default function EvidenceGraph() {
  const [selected, setSelected] = useState<string | null>(null)
  const [hovered, setHovered] = useState<string | null>(null)

  const positions = useMemo(() => {
    const cx = 280, cy = 200
    const angles = sampleNodes.map((_, i) => (i / sampleNodes.length) * Math.PI * 2 - Math.PI / 2)
    const r = 150
    return sampleNodes.map((n, i) => ({
      ...n,
      x: cx + r * Math.cos(angles[i]),
      y: cy + r * Math.sin(angles[i]),
    }))
  }, [])

  const activeNode = selected || hovered
  const connectedIds = useMemo(() => {
    if (!activeNode) return new Set<string>()
    const ids = new Set<string>([activeNode])
    sampleEdges.forEach(e => {
      if (e.source === activeNode) ids.add(e.target)
      if (e.target === activeNode) ids.add(e.source)
    })
    return ids
  }, [activeNode])

  return (
    <div className="bg-surface-card rounded-xl border border-surface-border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-text-primary">🕸 Evidence Graph</h3>
        <div className="flex gap-3 text-[10px] text-text-muted">
          {Object.entries(COLORS).map(([key, color]) => (
            <span key={key} className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full" style={{ background: color }} />
              {key}
            </span>
          ))}
        </div>
      </div>

      <svg viewBox="0 0 560 400" className="w-full h-auto bg-navy-900/30 rounded-lg">
        {/* Edges */}
        {sampleEdges.map((e, i) => {
          const src = positions.find(n => n.id === e.source)
          const tgt = positions.find(n => n.id === e.target)
          if (!src || !tgt) return null
          const isActive = activeNode && (e.source === activeNode || e.target === activeNode)
          return (
            <g key={i}>
              <line
                x1={src.x} y1={src.y} x2={tgt.x} y2={tgt.y}
                stroke={isActive ? '#c9a84c' : '#334155'}
                strokeWidth={isActive ? 2 : 1}
                strokeOpacity={isActive ? 0.8 : 0.3}
                strokeDasharray={e.weight < 0.6 ? '4,4' : undefined}
              />
              <text
                x={(src.x + tgt.x) / 2} y={(src.y + tgt.y) / 2 - 6}
                fill={isActive ? '#94a3b8' : '#475569'}
                fontSize={8}
                textAnchor="middle"
                className="select-none"
              >
                {e.label}
              </text>
            </g>
          )
        })}

        {/* Nodes */}
        {positions.map(n => {
          const isActive = connectedIds.has(n.id)
          const isHovered = hovered === n.id || selected === n.id
          return (
            <g
              key={n.id}
              onMouseEnter={() => setHovered(n.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => setSelected(selected === n.id ? null : n.id)}
              className="cursor-pointer"
            >
              <circle
                cx={n.x} cy={n.y}
                r={isHovered ? RADIUS[n.type] + 4 : RADIUS[n.type]}
                fill={isActive ? COLORS[n.type] : '#1e293b'}
                stroke={isHovered ? '#c9a84c' : isActive ? COLORS[n.type] : '#334155'}
                strokeWidth={isHovered ? 3 : 2}
                opacity={activeNode && !isActive ? 0.25 : 1}
                transition="all 0.2s"
              />
              <text
                x={n.x} y={n.y + 4}
                fill={isActive ? '#f1f5f9' : '#64748b'}
                fontSize={n.type === 'witness' ? 11 : 9}
                textAnchor="middle"
                className="select-none pointer-events-none"
                fontWeight={n.type === 'witness' ? 600 : 400}
              >
                {n.type === 'witness' ? n.label.split(' ').map(s => s[0]).join('') : '◈'}
              </text>
              {isHovered && (
                <text
                  x={n.x} y={n.y - RADIUS[n.type] - 10}
                  fill="#e2e8f0"
                  fontSize={9}
                  textAnchor="middle"
                  className="select-none"
                >
                  {n.label}
                </text>
              )}
            </g>
          )
        })}
      </svg>

      {/* Legend detail */}
      {selected && (
        <div className="mt-3 p-3 rounded-lg bg-navy-800/50 border border-surface-border">
          <div className="text-xs font-medium text-text-primary mb-1">
            {positions.find(n => n.id === selected)?.label}
          </div>
          <div className="text-[11px] text-text-muted">
            Connected to {connectedIds.size - 1} nodes
            {sampleEdges.filter(e => e.source === selected || e.target === selected).map((e, i) => (
              <span key={i} className="ml-2 text-gold">· {e.label}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}