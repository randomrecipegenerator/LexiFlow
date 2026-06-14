import { useState } from 'react'

interface EvidenceLinkProps {
  testimony: string
  witnessName: string
  lineNumber: number
  supportingDoc: string
  citations?: string[]
}

export default function EvidenceLink({ testimony, witnessName, lineNumber, supportingDoc, citations }: EvidenceLinkProps) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="bg-surface-card rounded-lg border border-surface-border overflow-hidden">
      {/* Testimony Quote */}
      <div
        onClick={() => setExpanded(!expanded)}
        className="p-3 cursor-pointer hover:bg-surface-light transition-colors"
      >
        <div className="flex items-start gap-2">
          <span className="text-gold mt-0.5 text-lg leading-none">❝</span>
          <div className="flex-1">
            <p className="text-sm text-text-primary leading-relaxed italic">{testimony}</p>
            <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
              <span className="font-medium text-gold/70">{witnessName}</span>
              <span>Line {lineNumber}</span>
              {supportingDoc && <span className="flex items-center gap-1">📎 {supportingDoc}</span>}
            </div>
          </div>
          <span className={`text-text-muted transition-transform ${expanded ? 'rotate-180' : ''}`}>▾</span>
        </div>
      </div>

      {/* Supporting evidence */}
      {expanded && (
        <div className="border-t border-surface-border p-3 bg-navy-900/50">
          <div className="text-xs font-medium text-text-muted mb-2 uppercase tracking-wider">Supporting Evidence</div>
          <div className="flex items-center gap-2 p-2 rounded-lg bg-navy-700/50 border border-surface-border cursor-pointer hover:bg-surface-light transition-colors">
            <span className="text-gold">📄</span>
            <span className="text-sm text-text-primary flex-1">{supportingDoc}</span>
            <span className="text-[11px] text-gold px-2 py-0.5 rounded-full bg-gold/10">View</span>
          </div>
          {citations && citations.length > 0 && (
            <div className="mt-2">
              <div className="text-xs font-medium text-text-muted mb-1">Legal Citations</div>
              <div className="flex flex-wrap gap-1.5">
                {citations.map((c, i) => (
                  <span key={i} className="text-[11px] px-2 py-0.5 rounded bg-navy-700 text-text-muted">{c}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}