/** UserPanel — User Control Plane UI — v0.8.8 / v0.9.1 */
import { useControlPlane } from '../hooks/useControlPlane'
import PageShell from '../components/PageShell'
import PositionTable from '../components/PositionTable'
import PnlPanel from '../components/PnlPanel'
import BalancePanel from '../components/BalancePanel'
import ClaimSummaryCard from '../components/ClaimSummaryCard'
import LiveGateStatus from '../components/LiveGateStatus'

export default function UserPanel() {
  const { state, status, refresh } = useControlPlane()

  return (
    <PageShell
      title="Kullanıcı Paneli"
      subtitle="Pozisyonlar, bakiye, K/Z ve canlı mod durumu."
      status={status}
      onRefresh={refresh}
    >
      {state && (
        <div className="space-y-4">
          {state.live_mode_ui_blocked && (
            <div className="rounded border border-amber-500/30 bg-amber-500/8 px-4 py-2.5 text-sm text-amber-300">
              Canlı mod kilitli — bu ekran simülasyon verileri göstermektedir.
            </div>
          )}
          <PositionTable
            title="Açık Pozisyonlar"
            positions={state.open_positions}
            emptyMessage="Açık pozisyon yok."
          />
          <PositionTable
            title="Kapalı Pozisyonlar"
            positions={state.closed_positions}
            emptyMessage="Kapalı pozisyon yok."
          />
          <PnlPanel
            sessionRealizedPnl={state.session_realized_pnl}
            sessionUnrealizedPnl={state.session_unrealized_pnl}
            sessionTotalPnl={state.session_total_pnl}
          />
          <BalancePanel
            totalBalance={state.total_balance}
            availableBalance={state.available_balance}
            currentBalance={state.current_balance}
            sessionStartBalance={state.session_start_balance}
          />
          <ClaimSummaryCard
            claimStatus={state.claim_status}
            claimAvailable={state.claim_available}
            claimedAmount={state.claimed_amount}
            settlementCompletedAt={state.settlement_completed_at}
          />
          <LiveGateStatus
            releaseReady={state.release_ready}
            liveAppliedTestingReady={state.live_applied_testing_ready}
            liveBlocked={state.live_mode_ui_blocked}
            blockedReasons={state.blocked_reason_messages}
          />
        </div>
      )}
    </PageShell>
  )
}
