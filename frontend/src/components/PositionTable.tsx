/** PositionTable — renders open or closed position list — v0.8.8 */
import type { PositionViewData } from '../types/controlPlane'

interface Props {
  title: string
  positions: PositionViewData[]
  emptyMessage: string
}

function fmt(n: number) {
  return n.toFixed(4)
}

function pnlClass(n: number) {
  if (n > 0) return 'text-emerald-400'
  if (n < 0) return 'text-red-400'
  return 'text-slate-400'
}

export default function PositionTable({ title, positions, emptyMessage }: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
        {title}
        <span className="ml-2 text-slate-500 font-normal normal-case">
          ({positions.length})
        </span>
      </p>

      {positions.length === 0 ? (
        <p className="text-sm text-slate-500">{emptyMessage}</p>
      ) : (
        <div className="space-y-2">
          {positions.map((p) => (
            <div
              key={p.position_id}
              className="rounded border border-white/8 bg-white/3 px-3 py-2 space-y-1"
            >
              {/* Header row */}
              <div className="flex items-center justify-between">
                <span className="text-xs text-slate-500 font-mono">{p.position_id}</span>
                <span className="text-xs text-slate-400">{p.event_key}</span>
                <span
                  className={`text-xs font-semibold uppercase ${
                    p.side === 'YES' ? 'text-emerald-400' : 'text-red-400'
                  }`}
                >
                  {p.side}
                </span>
              </div>

              {/* Price row */}
              <div className="grid grid-cols-3 gap-1 text-xs text-slate-400">
                <span>Tetik: <span className="text-slate-300">{fmt(p.trigger_price)}</span></span>
                <span>Giriş: <span className="text-slate-300">{fmt(p.entry_fill_price)}</span></span>
                <span>Güncel: <span className="text-slate-300">{fmt(p.current_price)}</span></span>
              </div>

              {/* Move row */}
              <div className="grid grid-cols-3 gap-1 text-xs text-slate-400">
                <span>H.Tetik: <span className="text-slate-300">{fmt(p.trigger_move_value)}</span></span>
                <span>H.Giriş: <span className="text-slate-300">{fmt(p.fill_move_value)}</span></span>
                <span>H.Güncel: <span className="text-slate-300">{fmt(p.current_move_value)}</span></span>
              </div>

              {/* PnL row */}
              <div className="flex gap-4 text-xs">
                <span className="text-slate-400">
                  Gerçekleşen K/Z: <span className={pnlClass(p.realized_pnl)}>{fmt(p.realized_pnl)}</span>
                </span>
                <span className="text-slate-400">
                  Açık K/Z: <span className={pnlClass(p.unrealized_pnl)}>{fmt(p.unrealized_pnl)}</span>
                </span>
              </div>

              {/* Metadata */}
              <div className="text-xs text-slate-500">
                {p.opened_at}
                {p.closed_at && <span className="ml-2">→ {p.closed_at}</span>}
                {p.exit_reason && <span className="ml-2 text-slate-400">[{p.exit_reason}]</span>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
