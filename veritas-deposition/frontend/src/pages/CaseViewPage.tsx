import { useParams, useNavigate } from 'react-router-dom'
import { mockMatters, mockWitnesses, mockContradictions } from '../data/mockData'
import WitnessProfileCard from '../components/witness/WitnessProfileCard'
import EvidenceLink from '../components/evidence/EvidenceLink'
import FileUpload from '../components/uploads/FileUpload'
import { useState } from 'react'

type ViewTab = 'witnesses' | 'transcripts' | 'evidence' | 'upload'

export default function CaseViewPage() {
  const { matterId } = useParams()
  const navigate = useNavigate()
  const matter = mockMatters.find(m => m.id === matterId)
  const [view, setView] = useState<ViewTab>('witnesses')

  if (!matter) return <div className="p-6 text-text-muted">Matter not found</div>

  const witnessList = mockWitnesses
  const contradictions = mockContradictions

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      {/* Header */}
      <div className="h-14 flex items-center gap-3 px-5 border-b border-surface-border flex-shrink-0">
        <button onClick={() => navigate('/dashboard')} className="text-text-muted hover:text-text-primary text-xs">← Dashboard</button>
        <span className="text-text-muted">/</span>
        <span className="text-sm font-semibold text-text-primary">{matter.name}</span>
        <StatusBadge status={matter.status} />
        <span className="text-xs text-text-muted ml-auto">{matter.caseNumber} · {matter.court}</span>
        <button onClick={() => navigate(`/trial-prep/${matter.id}`)} className="px-3 py-1.5 text-xs bg-gold/10 text-gold rounded-lg border border-gold/20 hover:bg-gold/20 transition-colors">
          Trial Prep →
        </button>
      </div>

      {/* View tabs */}
      <div className="flex gap-1 px-5 pt-3 border-b border-surface-border">
        {(['witnesses', 'transcripts', 'evidence', 'upload'] as ViewTab[]).map(t => (
          <button key={t} onClick={() => setView(t)}
            className={`px-4 py-2 text-xs font-medium rounded-t-lg transition-colors capitalize ${
              view === t ? 'bg-surface-card text-gold border border-surface-border border-b-transparent' : 'text-text-muted hover:text-text-secondary'
            }`}>
            {t === 'upload' ? '📤 Upload' : t}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-5">
        {view === 'witnesses' && (
          <div className="space-y-4">
            <h2 className="text-sm font-semibold text-text-primary">Witness Profiles <span className="text-text-muted font-normal">({witnessList.length})</span></h2>
            <div className="grid grid-cols-2 gap-3">
              {witnessList.map(w => <WitnessProfileCard key={w.id} witness={w} />)}
            </div>

            <h2 className="text-sm font-semibold text-text-primary mt-8">AI-Detected Contradictions <span className="text-text-muted font-normal">({contradictions.length})</span></h2>
            <div className="space-y-3">
              {contradictions.map(c => {
                const w = witnessList.find(w => w.id === c.witnessId)
                return (
                  <EvidenceLink
                    key={c.id}
                    testimony={c.description}
                    witnessName={w?.name || 'Unknown'}
                    lineNumber={c.sourceLine}
                    supportingDoc={c.supportingDoc || `${w?.name} Deposition`}
                  />
                )
              })}
            </div>
          </div>
        )}

        {view === 'transcripts' && (
          <div className="flex items-center justify-center h-full text-text-muted">
            <div className="text-center">
              <div className="text-4xl mb-3">📜</div>
              <p className="text-sm">Transcript Viewer</p>
              <p className="text-xs mt-1">Select a witness deposition to view the full transcript with AI annotations.</p>
            </div>
          </div>
        )}

        {view === 'evidence' && (
          <div className="flex items-center justify-center h-full text-text-muted">
            <div className="text-center">
              <div className="text-4xl mb-3">📦</div>
              <p className="text-sm">Evidence Repository</p>
              <p className="text-xs mt-1">Browse and link documentary evidence to witness testimony.</p>
            </div>
          </div>
        )}

        {view === 'upload' && (
          <div className="max-w-2xl">
            <h2 className="text-sm font-semibold text-text-primary mb-4">Upload Documents</h2>
            <FileUpload />
          </div>
        )}
      </div>
    </div>
  )
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = { active: 'bg-blue-500/10 text-blue-400', trial: 'bg-gold/10 text-gold', discovery: 'bg-purple-500/10 text-purple-400', closed: 'bg-text-muted/10 text-text-muted' }
  return <span className={`text-[10px] font-medium px-2 py-0.5 rounded-full capitalize ${map[status] || ''}`}>{status}</span>
}