/** AdminReleaseGate — release gate status with admin visibility — v0.8.9 */
import type { AdminControlPlaneState } from '../types/adminControlPlane'

interface Props {
  state: AdminControlPlaneState
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

export default function AdminReleaseGate({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Yayın Kapısı
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
    </div>
  )
}
