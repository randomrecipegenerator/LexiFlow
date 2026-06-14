import { useState } from 'react'
import { mockContradictions, mockWitnesses } from '../../data/mockData'

export default function ContradictionView() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  const filtered = filter === 'all'
    ? mockContradictions
    : mockContradictions.filter(c => c.severity === filter)

  const selected = mockContradictions.find(c => c.id === selectedId)

  return (
    <div className="flex gap-4 h-full">
      {/* List */}
      <div className="w-80 flex-shrink-0 space-y-2 overflow-y-auto">
        <div className="flex gap-1 mb-3">
          {['all', 'high', 'medium', 'low'].map(f => (
            <button key={f} onClick={() => setFilter(f)}
              className={`px-2.5 py-1 text-[10px] font-medium rounded-full capitalize transition-colors ${
                filter === f ? 'bg-gold/10 text-gold border border-gold/30' : 'bg-navy-700 text-text-muted border border-transparent hover:border-surface-border'
              }`}>
              {f}
            </button>
          ))}
        </div>

        {filtered.map(c => {
          const w = mockWitnesses.find(w => w.id === c.witnessId)
          const isSelected = selectedId === c.id
          return (
            <div key={c.id} onClick={() => setSelectedId(isSelected ? null : c.id)}
              className={`p-3 rounded-lg border cursor-pointer transition-all ${
                isSelected ? 'border-gold/40 bg-gold/5' : 'border-surface-border bg-surface-card hover:border-gold/20'
              }`}>
              <div className="flex items-center gap-2 mb-1">
                <SeverityBadge severity={c.severity} />
                <span className="text-xs font-medium text-text-primary truncate">{w?.name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-navy-700 text-text-muted uppercase">{c.type}</span>
              </div>
              <p className="text-[11px] text-text-secondary leading-relaxed line-clamp-2">{c.description}</p>
              <div className="mt-1.5 text-[10px] text-text-muted">{c.sourceTranscript}</div>
            </div>
          )
        })}
      </div>

      {/* Detail panel */}
      <div className="flex-1">
        {selected ? (
          <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <SeverityBadge severity={selected.severity} />
                <span className="text-sm font-semibold text-text-primary capitalize">{selected.severity} Severity</span>
                <span className="text-xs text-text-muted">· {selected.type} contradiction</span>
              </div>
            </div>

            {/* Side-by-side comparison */}
            <div className="grid grid-cols-2 gap-4">
              {/* Testimony 1 */}
              <div className="bg-surface-card rounded-lg border border-surface-border overflow-hidden">
                <div className="px-3 py-2 bg-navy-800/50 border-b border-surface-border flex items-center justify-between">
                  <span className="text-xs font-medium text-text-primary">Deposition Testimony</span>
                  <span className="text-[10px] text-text-muted">{selected.sourceTranscript}</span>
                </div>
                <div className="p-3">
                  <p className="text-sm text-text-primary leading-relaxed italic">"{selected.description}"</p>
                  <div className="mt-2 flex items-center gap-2 text-[11px] text-text-muted">
                    <span>Line {selected.sourceLine}</span>
                    {(() => {
                      const w = mockWitnesses.find(w => w.id === selected.witnessId)
                      return w ? <><span>·</span><span>{w.name}</span></> : null
                    })()}
                  </div>
                </div>
              </div>

              {/* Supporting evidence */}
              <div className="bg-surface-card rounded-lg border border-surface-border overflow-hidden">
                <div className="px-3 py-2 bg-navy-800/50 border-b border-surface-border flex items-center justify-between">
                  <span className="text-xs font-medium text-text-primary">Supporting Evidence</span>
                  <span className="text-[10px] text-gold">📎 Exhibit</span>
                </div>
                <div className="p-3">
                  {selected.supportingDoc ? (
                    <>
                      <div className="flex items-center gap-2 p-2 rounded-lg bg-navy-700/50 border border-surface-border mb-2">
                        <span className="text-gold text-lg">📄</span>
                        <div>
                          <div className="text-sm text-text-primary">{selected.supportingDoc}</div>
                          <div className="text-[11px] text-text-muted">Exhibit reference · Page 4 of 12</div>
                        </div>
                      </div>
                      <p className="text-xs text-text-secondary leading-relaxed">
                        This document directly contradicts the witness testimony regarding the sequence of events. 
                        The timeline recorded in the official record differs from the deposition account.
                      </p>
                    </>
                  ) : (
                    <p className="text-sm text-text-muted text-center py-8">No supporting document linked</p>
                  )}
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            <div className="bg-gold/5 border border-gold/20 rounded-lg p-3">
              <div className="text-xs font-medium text-gold mb-1">◇ AI Analysis</div>
              <p className="text-xs text-text-secondary leading-relaxed">
                This contradiction has been flagged as <strong className="text-text-primary">{selected.severity} priority</strong>. 
                The witness statement conflicts with documented evidence. Recommended for cross-examination focus.
                {selected.type === 'medical' && ' Medical record discrepancy suggests potential documentation error.'}
                {selected.type === 'timeline' && ' Timeline inconsistency may indicate memory reliability issues.'}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-text-muted">
            <div className="text-center">
              <div className="text-3xl mb-2">⚡</div>
              <p className="text-sm">Select a contradiction to view details</p>
              <p className="text-xs mt-1">Compare conflicting testimony side-by-side with supporting evidence</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors: Record<string, string> = {
    high: 'bg-red-500/10 text-red-400 border-red-500/20',
    medium: 'bg-gold/10 text-gold border-gold/20',
    low: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  }
  return (
    <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full border capitalize ${colors[severity] || ''}`}>
      {severity}
    </span>
  )
}