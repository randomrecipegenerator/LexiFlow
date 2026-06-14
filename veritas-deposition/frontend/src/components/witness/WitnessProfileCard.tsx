import type { Witness } from '../../types'

interface Props {
  witness: Witness
  onClick?: () => void
}

export default function WitnessProfileCard({ witness, onClick }: Props) {
  const initials = witness.name.split(' ').map(n => n[0]).join('')
  const riskColor = witness.riskScore > 70 ? 'text-red-400' : witness.riskScore > 50 ? 'text-gold' : 'text-green-400'
  const roleColor = witness.role === 'expert' ? 'border-purple-500 text-purple-400' :
    witness.role === 'defendant' ? 'border-red-500 text-red-400' :
    witness.role === 'medical' ? 'border-blue-500 text-blue-400' :
    'border-green-500 text-green-400'

  return (
    <div onClick={onClick} className="bg-surface-card rounded-lg p-4 border border-surface-border hover:border-gold/30 cursor-pointer transition-all">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-10 h-10 rounded-full bg-navy-700 flex items-center justify-center text-sm font-semibold text-text-primary flex-shrink-0">
          {initials}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-text-primary truncate">{witness.name}</div>
          <div className="flex items-center gap-2 mt-0.5">
            <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${roleColor} capitalize`}>{witness.role}</span>
          </div>
        </div>
        <div className={`text-sm font-bold ${riskColor}`}>{witness.riskScore}</div>
      </div>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-navy-700/50 rounded-lg p-2">
          <div className="text-xs font-semibold text-text-primary">{witness.transcriptCount}</div>
          <div className="text-[10px] text-text-muted">Depos</div>
        </div>
        <div className="bg-navy-700/50 rounded-lg p-2">
          <div className="text-xs font-semibold text-text-primary">{witness.contradictions}</div>
          <div className="text-[10px] text-text-muted">Conflicts</div>
        </div>
        <div className="bg-navy-700/50 rounded-lg p-2">
          <div className="text-xs font-semibold text-text-primary">{witness.credibility}%</div>
          <div className="text-[10px] text-text-muted">Credibility</div>
        </div>
      </div>
    </div>
  )
}