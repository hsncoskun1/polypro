/** PnlPanel — session PnL cards (realized / unrealized / total) — v0.8.8 */

interface Props {
  sessionRealizedPnl: number
  sessionUnrealizedPnl: number
  sessionTotalPnl: number
}

function PnlCard({ label, value }: { label: string; value: number }) {
  const valueClass =
    value > 0 ? 'text-emerald-400' : value < 0 ? 'text-red-400' : 'text-slate-400'
  return (
    <div className="flex flex-col gap-0.5 rounded border border-white/8 bg-white/3 px-3 py-2">
      <span className="text-xs text-slate-500">{label}</span>
      <span className={`text-sm font-semibold font-mono ${valueClass}`}>
        {value >= 0 ? '+' : ''}{value.toFixed(4)}
      </span>
    </div>
  )
}

export default function PnlPanel({
  sessionRealizedPnl,
  sessionUnrealizedPnl,
  sessionTotalPnl,
}: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
        Seans K/Z
      </p>
      <div className="grid grid-cols-3 gap-2">
        <PnlCard label="Gerçekleşen K/Z" value={sessionRealizedPnl} />
        <PnlCard label="Açık K/Z" value={sessionUnrealizedPnl} />
        <PnlCard label="Toplam K/Z" value={sessionTotalPnl} />
      </div>
    </div>
  )
}
