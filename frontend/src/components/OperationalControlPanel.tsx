/** OperationalControlPanel — admin operational control state — v0.8.9 */
import type { AdminControlPlaneState } from '../types/adminControlPlane'

interface Props {
  state: AdminControlPlaneState
}

function StatusRow({ label, active, activeLabel, inactiveLabel }: {
  label: string
  active: boolean
  activeLabel: string
  inactiveLabel: string
}) {
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`text-sm font-medium ${active ? 'text-red-400' : 'text-emerald-400'}`}>
        {active ? activeLabel : inactiveLabel}
      </span>
    </div>
  )
}

export default function OperationalControlPanel({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Operasyonel Kontrol
      </h2>
      <StatusRow
        label="Güvenli Durdurma"
        active={state.safe_stop_active}
        activeLabel="Aktif"
        inactiveLabel="Pasif"
      />
      {state.safe_stop_active && state.safe_stop_reason && (
        <p className="text-red-300 text-xs mt-1 mb-2">• {state.safe_stop_reason}</p>
      )}
      <StatusRow
        label="Zamanlayıcı"
        active={!state.scheduler_enabled}
        activeLabel="Devre Dışı"
        inactiveLabel="Etkin"
      />
      <StatusRow
        label="Genel Devre Dışı"
        active={state.global_disable_active}
        activeLabel="Aktif"
        inactiveLabel="Pasif"
      />
      <div className="flex justify-between items-center py-2 border-b border-slate-700">
        <span className="text-slate-300 text-sm">Yapılandırma Yeniden Yükleme</span>
        <span className={`text-sm font-medium ${state.config_reload_available ? 'text-slate-300' : 'text-slate-500'}`}>
          {state.config_reload_available ? 'Mevcut' : 'Mevcut Değil'}
        </span>
      </div>
      <div className="flex justify-between items-center py-2">
        <span className="text-slate-300 text-sm">Yapılandırma Sıfırlama</span>
        <span className={`text-sm font-medium ${state.config_reset_available ? 'text-slate-300' : 'text-slate-500'}`}>
          {state.config_reset_available ? 'Mevcut' : 'Mevcut Değil'}
        </span>
      </div>
    </div>
  )
}
