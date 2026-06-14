import { useParams, useNavigate } from 'react-router-dom'
import { mockMatters, mockWitnesses, mockContradictions } from '../data/mockData'
import EvidenceLink from '../components/evidence/EvidenceLink'

export default function TrialPrepPage() {
  const { matterId } = useParams()
  const navigate = useNavigate()
  const matter = mockMatters.find(m => m.id === matterId)

  if (!matter) return <div className="p-6 text-text-muted">Matter not found</div>

  const highRisk = [...mockWitnesses].filter(w => w.riskScore > 60)
  const highSeverity = mockContradictions.filter(c => c.severity === 'high')

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-14 flex items-center gap-3 px-5 border-b border-surface-border flex-shrink-0">
        <button onClick={() => navigate(`/case/${matterId}`)} className="text-text-muted hover:text-text-primary text-xs">← Case View</button>
        <span className="text-text-muted">/</span>
        <span className="text-sm font-semibold text-text-primary">Trial Preparation</span>
        <span className="text-xs text-text-muted ml-auto">{matter.name}</span>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-surface-card rounded-xl p-4 border border-surface-border">
            <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Trial Readiness</div>
            <div className="text-2xl font-bold text-gold">72%</div>
            <div className="mt-2 h-1.5 rounded-full bg-surface-lighter overflow-hidden">
              <div className="h-full rounded-full bg-gold" style={{ width: '72%' }} />
            </div>
          </div>
          <div className="bg-surface-card rounded-xl p-4 border border-surface-border">
            <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Key Witnesses</div>
            <div className="text-2xl font-bold text-text-primary">{highRisk.length}</div>
            <div className="text-xs text-red-400 mt-1">High risk — requires preparation</div>
          </div>
          <div className="bg-surface-card rounded-xl p-4 border border-surface-border">
            <div className="text-xs text-text-muted uppercase tracking-wider mb-1">Cross-Examinations</div>
            <div className="text-2xl font-bold text-text-primary">{highSeverity.length}</div>
            <div className="text-xs text-gold mt-1">Priority contradictions to address</div>
          </div>
        </div>

        {/* Cross-Examination Builder */}
        <div>
          <h2 className="text-sm font-semibold text-text-primary mb-3">Cross-Examination Builder</h2>
          <div className="space-y-3">
            {highSeverity.slice(0, 4).map(c => {
              const w = mockWitnesses.find(w => w.id === c.witnessId)
              return (
                <div key={c.id} className="bg-surface-card rounded-xl border border-surface-border overflow-hidden">
                  <div className="p-3 border-b border-surface-border bg-navy-800/50 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-red-400">⚡ HIGH PRIORITY</span>
                      <span className="text-xs text-text-muted">|</span>
                      <span className="text-sm font-medium text-text-primary">{w?.name}</span>
                    </div>
                    <span className="text-[11px] text-gold/70">{c.type} contradiction</span>
                  </div>
                  <div className="p-3">
                    <EvidenceLink
                      testimony={c.description}
                      witnessName={w?.name || ''}
                      lineNumber={c.sourceLine}
                      supportingDoc={c.supportingDoc || 'Deposition Transcript'}
                      citations={[`${c.sourceTranscript}`, `Exhibit ${Math.floor(Math.random() * 20) + 1}`]}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Witness Preparation */}
        <div>
          <h2 className="text-sm font-semibold text-text-primary mb-3">Witness Preparation Checklist</h2>
          <div className="bg-surface-card rounded-xl border border-surface-border divide-y divide-surface-border">
            {highRisk.map(w => (
              <div key={w.id} className="flex items-center justify-between p-3">
                <div className="flex items-center gap-3">
                  <input type="checkbox" className="accent-gold w-4 h-4" />
                  <div>
                    <div className="text-sm text-text-primary">{w.name}</div>
                    <div className="text-xs text-text-muted capitalize">{w.role} · {w.credibility}% credibility</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <span className={`text-[11px] px-2 py-0.5 rounded-full ${
                    w.riskScore > 70 ? 'bg-red-500/10 text-red-400' : 'bg-gold/10 text-gold'
                  }`}>{w.riskScore} risk</span>
                  <button className="text-xs text-gold/70 hover:text-gold">Prepare →</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}