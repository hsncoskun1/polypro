/** UserPanel — User Control Plane UI — v1.0.9 (entitlement enforcement) */
import { useControlPlane } from '../hooks/useControlPlane'
import { useEntitlement } from '../hooks/useEntitlement'
import PageShell from '../components/PageShell'
import PositionTable from '../components/PositionTable'
import PnlPanel from '../components/PnlPanel'
import BalancePanel from '../components/BalancePanel'
import ClaimSummaryCard from '../components/ClaimSummaryCard'
import LiveGateStatus from '../components/LiveGateStatus'

const SESSION_TOKEN_KEY = 'polypro_session_token'

/**
 * Panel visibility helper.
 * If visible_panels is empty, all panels are shown (default/unrestricted).
 * If visible_panels is non-empty, only listed panels are shown.
 */
function isPanelVisible(panelKey: string, visiblePanels: string[]): boolean {
  if (visiblePanels.length === 0) return true;
  return visiblePanels.includes(panelKey);
}

export default function UserPanel() {
  const { state, status, refresh } = useControlPlane()
  const sessionToken = sessionStorage.getItem(SESSION_TOKEN_KEY)
  const { entitlement } = useEntitlement(sessionToken)

  const visiblePanels = entitlement?.visible_panels ?? []
  const tradingEnabled = entitlement?.trading_enabled ?? true
  const blockedReasons = entitlement?.blocked_reason_messages ?? []

  return (
    <PageShell
      title="Kullanıcı Paneli"
      subtitle="Pozisyonlar, bakiye, K/Z ve canlı mod durumu."
      status={status}
      onRefresh={refresh}
    >
      {/* Trading lock — shown when trading_enabled is false */}
      {!tradingEnabled && (
        <div className="rounded border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300 mb-4" data-testid="trading-lock">
          <div className="font-semibold mb-1">İşlem Kilidi Aktif</div>
          {blockedReasons.length > 0 ? (
            <ul className="list-disc list-inside space-y-0.5">
              {blockedReasons.map((msg, i) => (
                <li key={i}>{msg}</li>
              ))}
            </ul>
          ) : (
            <p>Hesabınız için işlem devre dışı bırakıldı.</p>
          )}
        </div>
      )}

      {/* Blocked reasons visible even when trading is enabled (info/warning) */}
      {tradingEnabled && blockedReasons.length > 0 && (
        <div className="rounded border border-amber-500/30 bg-amber-500/8 px-4 py-2.5 text-sm text-amber-300 mb-4" data-testid="blocked-reasons">
          {blockedReasons.map((msg, i) => <p key={i}>• {msg}</p>)}
        </div>
      )}

      {state && (
        <div className="space-y-4">
          {state.live_mode_ui_blocked && (
            <div className="rounded border border-amber-500/30 bg-amber-500/8 px-4 py-2.5 text-sm text-amber-300">
              Canlı mod kilitli — bu ekran simülasyon verileri göstermektedir.
            </div>
          )}

          {isPanelVisible('positions', visiblePanels) && (
            <>
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
            </>
          )}

          {isPanelVisible('pnl', visiblePanels) && (
            <PnlPanel
              sessionRealizedPnl={state.session_realized_pnl}
              sessionUnrealizedPnl={state.session_unrealized_pnl}
              sessionTotalPnl={state.session_total_pnl}
            />
          )}

          {isPanelVisible('balance', visiblePanels) && (
            <BalancePanel
              totalBalance={state.total_balance}
              availableBalance={state.available_balance}
              currentBalance={state.current_balance}
              sessionStartBalance={state.session_start_balance}
            />
          )}

          {isPanelVisible('claims', visiblePanels) && (
            <ClaimSummaryCard
              claimStatus={state.claim_status}
              claimAvailable={state.claim_available}
              claimedAmount={state.claimed_amount}
              settlementCompletedAt={state.settlement_completed_at}
            />
          )}

          {isPanelVisible('live_gate', visiblePanels) && (
            <LiveGateStatus
              releaseReady={state.release_ready}
              liveAppliedTestingReady={state.live_applied_testing_ready}
              liveBlocked={state.live_mode_ui_blocked}
              blockedReasons={state.blocked_reason_messages}
            />
          )}
        </div>
      )}
    </PageShell>
  )
}
