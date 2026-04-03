/** UserPanel — User Control Plane UI — v0.8.8 */
import { useControlPlane } from '../hooks/useControlPlane'
import PositionTable from '../components/PositionTable'
import PnlPanel from '../components/PnlPanel'
import BalancePanel from '../components/BalancePanel'
import ClaimSummaryCard from '../components/ClaimSummaryCard'
import LiveGateStatus from '../components/LiveGateStatus'

export default function UserPanel() {
  const { state, status, refresh } = useControlPlane()

  const isLoading = status === 'loading'
  const isError = status === 'error'

  return (
    <div className="max-w-2xl mx-auto space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-white">Kullanıcı Paneli</h1>
        <p className="text-slate-400 text-sm mt-1">
          Pozisyonlar, bakiye, K/Z ve canlı mod durumu.
        </p>
      </div>

      {/* Backend unreachable */}
      {isError && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 flex items-center justify-between">
          <span className="text-sm text-red-300">Backend'e ulaşılamıyor.</span>
          <button
            onClick={refresh}
            className="text-xs text-red-400 hover:text-red-200 underline"
          >
            Yenile
          </button>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-16 rounded-lg bg-white/5 animate-pulse" />
          ))}
        </div>
      )}

      {/* Control plane data */}
      {state && (
        <>
          {/* Live gate blocked banner */}
          {state.live_mode_ui_blocked && (
            <div className="rounded-lg border border-amber-500/30 bg-amber-500/8 px-4 py-2.5 text-sm text-amber-300">
              Canlı mod kilitli — bu ekran simülasyon verileri göstermektedir.
            </div>
          )}

          {/* Open positions */}
          <PositionTable
            title="Açık Pozisyonlar"
            positions={state.open_positions}
            emptyMessage="Açık pozisyon yok."
          />

          {/* Closed positions */}
          <PositionTable
            title="Kapalı Pozisyonlar"
            positions={state.closed_positions}
            emptyMessage="Kapalı pozisyon yok."
          />

          {/* PnL */}
          <PnlPanel
            sessionRealizedPnl={state.session_realized_pnl}
            sessionUnrealizedPnl={state.session_unrealized_pnl}
            sessionTotalPnl={state.session_total_pnl}
          />

          {/* Balance */}
          <BalancePanel
            totalBalance={state.total_balance}
            availableBalance={state.available_balance}
            currentBalance={state.current_balance}
            sessionStartBalance={state.session_start_balance}
          />

          {/* Claim summary */}
          <ClaimSummaryCard
            claimStatus={state.claim_status}
            claimAvailable={state.claim_available}
            claimedAmount={state.claimed_amount}
            settlementCompletedAt={state.settlement_completed_at}
          />

          {/* Live gate */}
          <LiveGateStatus
            releaseReady={state.release_ready}
            liveAppliedTestingReady={state.live_applied_testing_ready}
            liveBlocked={state.live_mode_ui_blocked}
            blockedReasons={state.blocked_reason_messages}
          />
        </>
      )}
    </div>
  )
}
