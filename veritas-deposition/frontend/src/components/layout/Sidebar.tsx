import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { mockMatters } from '../../data/mockData'

export default function Sidebar() {
  const [active, setActive] = useState('dashboard')
  const navigate = useNavigate()

  return (
    <aside className="w-64 bg-navy-800 border-r border-surface-border flex flex-col flex-shrink-0">
      {/* Brand */}
      <div className="h-14 flex items-center gap-3 px-5 border-b border-surface-border">
        <div className="w-7 h-7 rounded-md bg-navy-700 flex items-center justify-center text-gold text-xs font-bold">V</div>
        <div>
          <div className="text-sm font-semibold text-text-primary">Veritas</div>
          <div className="text-[10px] text-gold font-medium tracking-wider uppercase">Deposition™</div>
        </div>
      </div>

      {/* Quick Nav */}
      <nav className="p-3 border-b border-surface-border">
        <NavItem icon="◻" label="Dashboard" active={active === 'dashboard'} onClick={() => { setActive('dashboard'); navigate('/dashboard') }} />
        <NavItem icon="⊕" label="New Analysis" active={false} onClick={() => {}} />
        <NavItem icon="↥" label="Upload" active={false} onClick={() => {}} />
      </nav>

      {/* Matters */}
      <div className="flex-1 overflow-y-auto p-3">
        <div className="text-[11px] font-semibold text-text-muted uppercase tracking-wider mb-2 px-2">Active Matters</div>
        {mockMatters.map(m => (
          <div
            key={m.id}
            onClick={() => { setActive(m.id); navigate(`/case/${m.id}`) }}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors text-sm mb-0.5 ${
              active === m.id ? 'bg-surface-light text-gold' : 'text-text-secondary hover:bg-surface-light hover:text-text-primary'
            }`}
          >
            <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
              m.status === 'active' ? 'bg-green-500' : m.status === 'trial' ? 'bg-gold' : m.status === 'discovery' ? 'bg-blue-500' : 'bg-text-muted'
            }`} />
            <div className="flex-1 min-w-0">
              <div className="truncate font-medium">{m.name}</div>
              <div className="text-[11px] text-text-muted truncate">{m.caseNumber}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-surface-border text-[11px] text-text-muted">
        <div className="flex items-center gap-2 px-2 py-1">
          <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
          Veritas Core™ v1.0
        </div>
      </div>
    </aside>
  )
}

function NavItem({ icon, label, active, onClick }: { icon: string; label: string; active: boolean; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-3 px-3 py-2.5 rounded-lg cursor-pointer transition-colors text-sm mb-0.5 ${
        active ? 'bg-surface-light text-gold font-medium' : 'text-text-secondary hover:bg-surface-light hover:text-text-primary'
      }`}
    >
      <span className="w-5 text-center text-base">{icon}</span>
      <span>{label}</span>
    </div>
  )
}