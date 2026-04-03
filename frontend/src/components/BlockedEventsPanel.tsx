/** BlockedEventsPanel — blocked trades / rules / risk events — v0.8.9 */
import type { AdminControlPlaneState } from '../types/adminControlPlane'

interface Props {
  state: AdminControlPlaneState
}

function EventList({ title, items, emptyLabel }: { title: string; items: string[]; emptyLabel: string }) {
  return (
    <div className="mb-3 last:mb-0">
      <p className="text-slate-400 text-xs font-medium mb-1">{title}</p>
      {items.length === 0 ? (
        <p className="text-slate-500 text-xs italic">{emptyLabel}</p>
      ) : (
        <ul className="space-y-1">
          {items.map((item, i) => (
            <li key={i} className="text-red-300 text-xs">• {item}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function BlockedEventsPanel({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Bloke Olaylar
      </h2>
      <EventList
        title="Bloke Edilen İşlemler"
        items={state.blocked_trades}
        emptyLabel="Bloke işlem yok"
      />
      <EventList
        title="Bloke Edilen Kurallar"
        items={state.blocked_rules}
        emptyLabel="Bloke kural yok"
      />
      <EventList
        title="Bloke Edilen Risk Olayları"
        items={state.blocked_risk_events}
        emptyLabel="Bloke risk olayı yok"
      />
    </div>
  )
}
