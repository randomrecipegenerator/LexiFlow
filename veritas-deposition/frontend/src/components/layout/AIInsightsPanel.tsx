import { useState } from 'react'
import EvidenceGraph from '../graph/EvidenceGraph'
import ContradictionView from '../contradictions/ContradictionView'
import { mockContradictions, mockWitnesses } from '../../data/mockData'

export default function AIInsightsPanel() {
  const [tab, setTab] = useState<'risk' | 'contradictions' | 'graph'>('risk')
  const contradictions = mockContradictions.filter(c => c.severity === 'high')
  const witnessRisk = [...mockWitnesses].sort((a, b) => b.riskScore - a.riskScore).slice(0, 4)

  return (
    <aside className="w-80 bg-navy-800 border-l border-surface-border flex flex-col flex-shrink-0">
      {/* Header */}
      <div className="h-14 flex items-center gap-2 px-4 border-b border-surface-border">
        <span className="text-gold text-lg">◇</span>
        <span className="text-sm font-semibold text-text-primary">AI Insights</span>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-surface-border">
        {(['risk', 'contradictions', 'graph'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)} className={`flex-1 py-2.5 text-xs font-medium transition-colors ${
            tab === t ? 'text-gold border-b-2 border-gold' : 'text-text-muted hover:text-text-secondary'
          }`}>
            {t === 'risk' ? 'Witness Risk' : t === 'contradictions' ? 'Contradictions' : 'Evidence Graph'}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">

        {/* Witness Risk Tab */}
        {tab === 'risk' && witnessRisk.map(w => (
          <div key={w.id} className="bg-surface-card rounded-lg p-3 border border-surface-border">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-text-primary">{w.name}</span>
              <RiskBadge score={w.riskScore} />
            </div>
            <div className="flex gap-3 text-xs text-text-muted">
              <span className="capitalize">{w.role}</span>
              <span>Cred: {w.credibility}%</span>
              <span>{w.contradictions} conflicts</span>
            </div>
            <div className="mt-2 h-1.5 rounded-full bg-surface-lighter overflow-hidden">
              <div className={`h-full rounded-full transition-all ${
                w.riskScore > 70 ? 'bg-red-500' : w.riskScore > 50 ? 'bg-gold' : 'bg-green-500'
              }`} style={{ width: `${w.riskScore}%` }} />
            </div>
          </div>
        ))}

        {/* Contradictions Tab - Full view */}
        {tab === 'contradictions' && (
          <div className="space-y-2">
            {mockContradictions.slice(0, 6).map(c => {
              const witness = mockWitnesses.find(w => w.id === c.witnessId)
              return (
                <div key={c.id} className="bg-surface-card rounded-lg p-3 border border-surface-border cursor-pointer hover:border-gold/30 transition-colors">
                  <div className="flex items-center gap-2 mb-1">
                    <SeverityDot severity={c.severity} />
                    <span className="text-xs font-medium text-text-primary">{witness?.name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-navy-700 text-text-muted uppercase">{c.type}</span>
                  </div>
                  <p className="text-xs text-text-secondary leading-relaxed">{c.description}</p>
                  <div className="mt-2 text-[11px] text-text-muted">{c.sourceTranscript}</div>
                  {c.supportingDoc && (
                    <div className="mt-1 text-[11px] text-gold/70 flex items-center gap-1">
                      <span>📎</span> {c.supportingDoc}
                    </div>
                  )}
                </div>
              )
            })}
            <div className="text-center pt-2">
              <button onClick={() => setTab('graph')} className="text-[11px] text-gold/70 hover:text-gold">
                View all in Evidence Graph →
              </button>
            </div>
          </div>
        )}

        {/* Evidence Graph Tab */}
        {tab === 'graph' && (
          <div className="overflow-hidden">
            <EvidenceGraph />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-surface-border text-[11px] text-text-muted text-center">
        Powered by Veritas Core™ Reasoning AI
      </div>
    </aside>
  )
}

function RiskBadge({ score }: { score: number }) {
  const color = score > 70 ? 'bg-red-500/10 text-red-400' : score > 50 ? 'bg-gold/10 text-gold' : 'bg-green-500/10 text-green-400'
  return <span className={`text-[11px] font-medium px-2 py-0.5 rounded-full ${color}`}>{score} Risk</span>
}

function SeverityDot({ severity }: { severity: string }) {
  const color = severity === 'high' ? 'bg-red-500' : severity === 'medium' ? 'bg-gold' : 'bg-blue-500'
  return <span className={`w-1.5 h-1.5 rounded-full ${color} flex-shrink-0`} />
}