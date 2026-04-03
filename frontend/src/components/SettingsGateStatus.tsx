/** SettingsGateStatus — release gate and blocked reasons for settings view — v0.9.0 */
import type { SettingsState } from '../types/settings'

interface Props {
  state: SettingsState
}

function GateRow({ label, active, activeLabel, inactiveLabel }: {
  label: string
  active: boolean
  activeLabel: string
  inactiveLabel: string
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`text-sm font-medium ${active ? 'text-emerald-400' : 'text-slate-500'}`}>
        <span className={`inline-block w-2 h-2 rounded-full mr-1 ${active ? 'bg-emerald-400' : 'bg-slate-500'}`} />
        {active ? activeLabel : inactiveLabel}
      </span>
    </div>
  )
}

export default function SettingsGateStatus({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Yayın Durumu
      </h2>
      <GateRow
        label="Yayın Hazırlığı"
        active={state.release_ready}
        activeLabel="Hazır"
        inactiveLabel="Hazır Değil"
      />
      <GateRow
        label="Canlı Uygulamalı Test"
        active={state.live_applied_testing_ready}
        activeLabel="Etkin"
        inactiveLabel="Kapalı"
      />
      {state.blocked_reason_messages.length > 0 && (
        <div className="mt-3">
          <p className="text-slate-400 text-xs font-medium mb-1">Engel Nedenleri</p>
          <ul className="space-y-1">
            {state.blocked_reason_messages.map((msg, i) => (
              <li key={i} className="text-slate-400 text-xs">• {msg}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
