/** BalancePanel — balance cards (total / available / current / session start) — v0.8.8 */

interface Props {
  totalBalance: number
  availableBalance: number
  currentBalance: number
  sessionStartBalance: number
}

function BalanceCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col gap-0.5 rounded border border-white/8 bg-white/3 px-3 py-2">
      <span className="text-xs text-slate-500">{label}</span>
      <span className="text-sm font-semibold font-mono text-slate-300">
        {value.toFixed(4)}
      </span>
    </div>
  )
}

export default function BalancePanel({
  totalBalance,
  availableBalance,
  currentBalance,
  sessionStartBalance,
}: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
        Bakiye
      </p>
      <div className="grid grid-cols-2 gap-2">
        <BalanceCard label="Toplam Bakiye" value={totalBalance} />
        <BalanceCard label="Kullanılabilir Bakiye" value={availableBalance} />
        <BalanceCard label="Güncel Bakiye" value={currentBalance} />
        <BalanceCard label="Seans Başlangıç Bakiyesi" value={sessionStartBalance} />
      </div>
    </div>
  )
}
