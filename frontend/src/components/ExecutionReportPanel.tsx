/** ExecutionReportPanel — fill events, claim events, operational alerts — v0.8.9 */
import type { AdminControlPlaneState } from '../types/adminControlPlane'

interface Props {
  state: AdminControlPlaneState
}

function EventList({ title, items, emptyLabel, alertStyle }: {
  title: string
  items: string[]
  emptyLabel: string
  alertStyle?: boolean
}) {
  return (
    <div className="mb-3 last:mb-0">
      <p className="text-slate-400 text-xs font-medium mb-1">{title}</p>
      {items.length === 0 ? (
        <p className="text-slate-500 text-xs italic">{emptyLabel}</p>
      ) : (
        <ul className="space-y-1">
          {items.map((item, i) => (
            <li key={i} className={`text-xs ${alertStyle ? 'text-yellow-300' : 'text-slate-300'}`}>
              • {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export default function ExecutionReportPanel({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Gerçekleşme ve Uyarı Raporu
      </h2>
      <EventList
        title="Gerçekleşme Olayları"
        items={state.execution_fill_events}
        emptyLabel="Gerçekleşme olayı yok"
      />
      <EventList
        title="Talep Olayları"
        items={state.claim_events}
        emptyLabel="Talep olayı yok"
      />
      <EventList
        title="Operasyonel Uyarılar"
        items={state.operational_alerts}
        emptyLabel="Uyarı yok"
        alertStyle
      />
    </div>
  )
}
