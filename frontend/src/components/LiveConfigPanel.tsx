/** LiveConfigPanel — live configuration state: explicit enable, test gate — v0.9.0 */
import type { SettingsState } from '../types/settings'

interface Props {
  state: SettingsState
}

function ConfigRow({ label, value, activeLabel, inactiveLabel, isWarning }: {
  label: string
  value: boolean
  activeLabel: string
  inactiveLabel: string
  isWarning?: boolean
}) {
  const color = value
    ? isWarning ? 'text-yellow-400' : 'text-emerald-400'
    : 'text-slate-500'
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`text-sm font-medium ${color}`}>
        <span className={`inline-block w-2 h-2 rounded-full mr-1 ${value ? (isWarning ? 'bg-yellow-400' : 'bg-emerald-400') : 'bg-slate-500'}`} />
        {value ? activeLabel : inactiveLabel}
      </span>
    </div>
  )
}

export default function LiveConfigPanel({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Canlı Yapılandırma
      </h2>
      <ConfigRow
        label="Açık Canlı Etkinleştirme"
        value={state.explicit_live_enable}
        activeLabel="Etkin"
        inactiveLabel="Kapalı"
        isWarning
      />
      <ConfigRow
        label="Canlı Test Kapısı Etkin"
        value={state.live_test_gate_enabled}
        activeLabel="Etkin"
        inactiveLabel="Kapalı"
      />
      <ConfigRow
        label="Canlı Test Kapısı Geçildi"
        value={state.live_test_gate_passed}
        activeLabel="Geçildi"
        inactiveLabel="Geçilmedi"
      />
    </div>
  )
}
