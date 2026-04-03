/** AdminFinancialSummary — full balance/PnL admin reporting panel — v0.8.9 */
import type { AdminControlPlaneState } from '../types/adminControlPlane'

interface Props {
  state: AdminControlPlaneState
}

function ValueCard({ label, value, signed }: { label: string; value: number; signed?: boolean }) {
  const formatted = value.toFixed(4)
  const prefix = signed ? (value >= 0 ? '+' : '') : ''
  const color = signed ? (value > 0 ? 'text-emerald-400' : value < 0 ? 'text-red-400' : 'text-slate-300') : 'text-slate-300'
  return (
    <div className="bg-slate-700 rounded p-3">
      <p className="text-slate-400 text-xs mb-1">{label}</p>
      <p className={`text-sm font-mono font-medium ${color}`}>{prefix}{formatted}</p>
    </div>
  )
}

export default function AdminFinancialSummary({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Finansal Özet
      </h2>
      <div className="grid grid-cols-2 gap-2 mb-3">
        <ValueCard label="Toplam Bakiye" value={state.total_balance} />
        <ValueCard label="Kullanılabilir Bakiye" value={state.available_balance} />
        <ValueCard label="Güncel Bakiye" value={state.current_balance} />
        <ValueCard label="Seans Başlangıç Bakiyesi" value={state.session_start_balance} />
      </div>
      <div className="grid grid-cols-3 gap-2 mb-2">
        <ValueCard label="Gerçekleşen K/Z" value={state.realized_pnl} signed />
        <ValueCard label="Gerçekleşmemiş K/Z" value={state.unrealized_pnl} signed />
        <ValueCard label="Seans Toplam K/Z" value={state.session_total_pnl} signed />
      </div>
      <div className="grid grid-cols-1 gap-2">
        <ValueCard label="Talep Düzeltilmiş Bakiye Etkisi" value={state.claim_adjusted_balance_effect} signed />
      </div>
    </div>
  )
}
