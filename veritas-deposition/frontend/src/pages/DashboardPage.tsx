import { useNavigate } from 'react-router-dom'
import { mockMatters, mockWitnesses } from '../data/mockData'
import WitnessProfileCard from '../components/witness/WitnessProfileCard'
import EvidenceGraph from '../components/graph/EvidenceGraph'

export default function DashboardPage() {
  const navigate = useNavigate()
  const topRisk = [...mockWitnesses].sort((a, b) => b.riskScore - a.riskScore).slice(0, 3)

  return (
    <div className="flex-1 overflow-y-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-serif font-bold text-text-primary">Veritas Deposition™</h1>
        <p className="text-sm text-text-muted mt-1">Evidence Intelligence System — Litigation Dashboard</p>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Active Matters', value: mockMatters.filter(m => m.status !== 'closed').length, icon: '⚖️' },
          { label: 'Witnesses Tracked', value: mockWitnesses.length, icon: '👤' },
          { label: 'Contradictions Found', value: 12, icon: '⚡' },
          { label: 'Documents Indexed', value: '1,847', icon: '📚' },
        ].map(s => (
          <div key={s.label} className="bg-surface-card rounded-xl p-4 border border-surface-border">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">{s.icon}</span>
              <span className="text-xs text-text-muted uppercase tracking-wider">{s.label}</span>
            </div>
            <div className="text-2xl font-bold text-text-primary">{s.value}</div>
          </div>
        ))}
      </div>

      {/* Evidence Graph */}
      <EvidenceGraph />

      {/* Matters */}
      <div>
        <h2 className="text-sm font-semibold text-text-primary mb-3 uppercase tracking-wider">Active Matters</h2>
        <div className="grid grid-cols-2 gap-3">
          {mockMatters.filter(m => m.status !== 'closed').map(m => (
            <div key={m.id} onClick={() => navigate(`/case/${m.id}`)}
              className="bg-surface-card rounded-xl p-4 border border-surface-border cursor-pointer hover:border-gold/30 transition-all">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <div className="text-sm font-semibold text-text-primary">{m.name}</div>
                  <div className="text-xs text-text-muted mt-0.5">{m.caseNumber}</div>
                </div>
                <StatusBadge status={m.status} />
              </div>
              <div className="flex gap-4 text-xs text-text-muted mt-3">
                <span>{m.witnessCount} witnesses</span>
                <span>{m.transcriptCount} transcripts</span>
                <span>{m.court}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* High Risk Witnesses */}
      <div>
        <h2 className="text-sm font-semibold text-text-primary mb-3 uppercase tracking-wider">High Risk Witnesses</h2>
        <div className="grid grid-cols-3 gap-3">
          {topRisk.map(w => (
            <WitnessProfileCard key={w.id} witness={w} />
          ))}
        </div>
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = { active: 'bg-blue-500/10 text-blue-400', trial: 'bg-gold/10 text-gold', discovery: 'bg-purple-500/10 text-purple-400', closed: 'bg-text-muted/10 text-text-muted' }
  return <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${map[status] || ''}`}>{status}</span>
}