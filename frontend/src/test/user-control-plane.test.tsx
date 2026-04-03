/** user-control-plane.test.tsx — v0.8.8 User Control Plane UI tests */

import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import PositionTable from '../components/PositionTable'
import PnlPanel from '../components/PnlPanel'
import BalancePanel from '../components/BalancePanel'
import ClaimSummaryCard from '../components/ClaimSummaryCard'
import LiveGateStatus from '../components/LiveGateStatus'
import UserPanel from '../routes/UserPanel'

// ── useControlPlane mock ─────────────────────────────────────────────────────

vi.mock('../hooks/useControlPlane', () => ({
  useControlPlane: vi.fn(),
}))

import { useControlPlane } from '../hooks/useControlPlane'
const mockUseControlPlane = vi.mocked(useControlPlane)

// ── Fixtures ─────────────────────────────────────────────────────────────────

const EMPTY_STATE = {
  open_positions: [],
  closed_positions: [],
  session_realized_pnl: 0.0,
  session_unrealized_pnl: 0.0,
  session_total_pnl: 0.0,
  total_balance: 0.0,
  available_balance: 0.0,
  current_balance: 0.0,
  session_start_balance: 0.0,
  claim_status: 'not_claimable_outcome_unknown',
  claim_available: false,
  claimed_amount: 0.0,
  settlement_completed_at: null,
  release_ready: true,
  live_applied_testing_ready: false,
  live_mode_ui_blocked: true,
  blocked_reason_messages: ['Canlı uygulamalı test henüz yetkilendirilmedi.'],
}

const OPEN_POS = {
  position_id: 'pos-001',
  event_key: 'btc-up',
  side: 'YES',
  status: 'open',
  trigger_price: 0.65,
  entry_fill_price: 0.66,
  current_price: 0.70,
  exit_fill_price: 0.0,
  trigger_move_value: 0.05,
  fill_move_value: 0.04,
  current_move_value: 0.08,
  realized_pnl: 0.0,
  unrealized_pnl: 0.04,
  entry_reason: 'rule_triggered',
  exit_reason: '',
  opened_at: '2026-04-03T08:00:00',
  closed_at: null,
}

function renderUserPanel() {
  return render(
    <MemoryRouter>
      <UserPanel />
    </MemoryRouter>
  )
}

// ── PositionTable ─────────────────────────────────────────────────────────────

describe('PositionTable', () => {
  test('shows title', () => {
    render(<PositionTable title="Açık Pozisyonlar" positions={[]} emptyMessage="Boş." />)
    expect(screen.getByText(/Açık Pozisyonlar/)).toBeInTheDocument()
  })

  test('shows empty message when no positions', () => {
    render(<PositionTable title="X" positions={[]} emptyMessage="Pozisyon yok." />)
    expect(screen.getByText('Pozisyon yok.')).toBeInTheDocument()
  })

  test('shows position id when positions present', () => {
    render(<PositionTable title="X" positions={[OPEN_POS]} emptyMessage="Boş." />)
    expect(screen.getByText('pos-001')).toBeInTheDocument()
  })

  test('shows event_key', () => {
    render(<PositionTable title="X" positions={[OPEN_POS]} emptyMessage="Boş." />)
    expect(screen.getByText('btc-up')).toBeInTheDocument()
  })

  test('shows side YES', () => {
    render(<PositionTable title="X" positions={[OPEN_POS]} emptyMessage="Boş." />)
    expect(screen.getByText('YES')).toBeInTheDocument()
  })

  test('shows position count', () => {
    render(<PositionTable title="X" positions={[OPEN_POS]} emptyMessage="Boş." />)
    expect(screen.getByText('(1)')).toBeInTheDocument()
  })
})

// ── PnlPanel ──────────────────────────────────────────────────────────────────

describe('PnlPanel', () => {
  test('shows Seans K/Z heading', () => {
    render(<PnlPanel sessionRealizedPnl={0} sessionUnrealizedPnl={0} sessionTotalPnl={0} />)
    expect(screen.getByText('Seans K/Z')).toBeInTheDocument()
  })

  test('shows all three pnl labels', () => {
    render(<PnlPanel sessionRealizedPnl={1.5} sessionUnrealizedPnl={-0.5} sessionTotalPnl={1.0} />)
    expect(screen.getByText('Gerçekleşen K/Z')).toBeInTheDocument()
    expect(screen.getByText('Açık K/Z')).toBeInTheDocument()
    expect(screen.getByText('Toplam K/Z')).toBeInTheDocument()
  })

  test('positive pnl shows + prefix', () => {
    render(<PnlPanel sessionRealizedPnl={1.5} sessionUnrealizedPnl={0} sessionTotalPnl={1.5} />)
    expect(screen.getAllByText(/^\+/).length).toBeGreaterThan(0)
  })
})

// ── BalancePanel ──────────────────────────────────────────────────────────────

describe('BalancePanel', () => {
  test('shows Bakiye heading', () => {
    render(<BalancePanel totalBalance={0} availableBalance={0} currentBalance={0} sessionStartBalance={0} />)
    expect(screen.getByText('Bakiye')).toBeInTheDocument()
  })

  test('shows all four balance labels', () => {
    render(<BalancePanel totalBalance={100} availableBalance={80} currentBalance={90} sessionStartBalance={100} />)
    expect(screen.getByText('Toplam Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Kullanılabilir Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Güncel Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Seans Başlangıç Bakiyesi')).toBeInTheDocument()
  })
})

// ── ClaimSummaryCard ──────────────────────────────────────────────────────────

describe('ClaimSummaryCard', () => {
  test('shows Talep / Uzlasma heading', () => {
    render(<ClaimSummaryCard claimStatus="not_claimable_outcome_unknown" claimAvailable={false} claimedAmount={0} settlementCompletedAt={null} />)
    expect(screen.getByText('Talep / Uzlaşma')).toBeInTheDocument()
  })

  test('maps not_claimable_outcome_unknown to Turkish', () => {
    render(<ClaimSummaryCard claimStatus="not_claimable_outcome_unknown" claimAvailable={false} claimedAmount={0} settlementCompletedAt={null} />)
    expect(screen.getByText('Sonuç Bilinmiyor')).toBeInTheDocument()
  })

  test('maps claim_available to Turkish', () => {
    render(<ClaimSummaryCard claimStatus="claim_available" claimAvailable={true} claimedAmount={5.0} settlementCompletedAt={null} />)
    expect(screen.getByText('Talep Kullanılabilir')).toBeInTheDocument()
  })

  test('shows claimed amount when claim_available=true', () => {
    render(<ClaimSummaryCard claimStatus="claim_available" claimAvailable={true} claimedAmount={5.1234} settlementCompletedAt={null} />)
    expect(screen.getByText('5.1234')).toBeInTheDocument()
  })

  test('shows settlement date when present', () => {
    render(<ClaimSummaryCard claimStatus="claim_completed" claimAvailable={false} claimedAmount={0} settlementCompletedAt="2026-04-03" />)
    expect(screen.getByText('2026-04-03')).toBeInTheDocument()
  })
})

// ── LiveGateStatus ────────────────────────────────────────────────────────────

describe('LiveGateStatus', () => {
  test('shows Canli Mod heading', () => {
    render(<LiveGateStatus releaseReady={true} liveAppliedTestingReady={false} liveBlocked={true} blockedReasons={[]} />)
    expect(screen.getByText('Canlı Mod Durumu')).toBeInTheDocument()
  })

  test('shows Yayin Hazırlığı row', () => {
    render(<LiveGateStatus releaseReady={true} liveAppliedTestingReady={false} liveBlocked={true} blockedReasons={[]} />)
    expect(screen.getByText('Yayın Hazırlığı')).toBeInTheDocument()
  })

  test('shows Canli Test Kapisi row', () => {
    render(<LiveGateStatus releaseReady={true} liveAppliedTestingReady={false} liveBlocked={true} blockedReasons={[]} />)
    expect(screen.getByText('Canlı Test Kapısı')).toBeInTheDocument()
  })

  test('shows release_ready as Hazır', () => {
    render(<LiveGateStatus releaseReady={true} liveAppliedTestingReady={false} liveBlocked={true} blockedReasons={[]} />)
    expect(screen.getByText('Hazır')).toBeInTheDocument()
  })

  test('shows live gate as Kapalı', () => {
    render(<LiveGateStatus releaseReady={true} liveAppliedTestingReady={false} liveBlocked={true} blockedReasons={[]} />)
    expect(screen.getByText('Kapalı')).toBeInTheDocument()
  })

  test('shows blocked reasons when present', () => {
    render(
      <LiveGateStatus
        releaseReady={true}
        liveAppliedTestingReady={false}
        liveBlocked={true}
        blockedReasons={['Yetkilendirme gerekli.']}
      />
    )
    expect(screen.getByText('Yetkilendirme gerekli.')).toBeInTheDocument()
  })
})

// ── UserPanel ─────────────────────────────────────────────────────────────────

describe('UserPanel', () => {
  afterEach(() => vi.clearAllMocks())

  test('shows loading skeleton when status=loading', () => {
    mockUseControlPlane.mockReturnValue({ state: null, status: 'loading', refresh: vi.fn() })
    const { container } = renderUserPanel()
    expect(container.querySelector('.animate-pulse')).not.toBeNull()
  })

  test('shows error message when status=error', () => {
    mockUseControlPlane.mockReturnValue({ state: null, status: 'error', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText("Backend'e ulaşılamıyor.")).toBeInTheDocument()
  })

  test('refresh button calls refresh on error', () => {
    const refresh = vi.fn()
    mockUseControlPlane.mockReturnValue({ state: null, status: 'error', refresh })
    renderUserPanel()
    fireEvent.click(screen.getByText('Yenile'))
    expect(refresh).toHaveBeenCalledTimes(1)
  })

  test('shows header when ready', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Kullanıcı Paneli')).toBeInTheDocument()
  })

  test('shows live blocked banner when live_mode_ui_blocked=true', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText(/Canlı mod kilitli/)).toBeInTheDocument()
  })

  test('shows open positions section', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText(/Açık Pozisyonlar/)).toBeInTheDocument()
  })

  test('shows closed positions section', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText(/Kapalı Pozisyonlar/)).toBeInTheDocument()
  })

  test('shows empty message for open positions by default', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Açık pozisyon yok.')).toBeInTheDocument()
  })

  test('shows empty message for closed positions by default', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Kapalı pozisyon yok.')).toBeInTheDocument()
  })

  test('shows pnl panel', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Seans K/Z')).toBeInTheDocument()
  })

  test('shows balance panel', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Bakiye')).toBeInTheDocument()
  })

  test('shows claim summary', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Talep / Uzlaşma')).toBeInTheDocument()
  })

  test('shows live gate status', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Canlı Mod Durumu')).toBeInTheDocument()
  })

  test('shows open position when present', () => {
    const stateWithPos = { ...EMPTY_STATE, open_positions: [OPEN_POS] }
    mockUseControlPlane.mockReturnValue({ state: stateWithPos, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('pos-001')).toBeInTheDocument()
  })

  test('live_applied_testing_ready shown as Kapali', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Kapalı')).toBeInTheDocument()
  })

  test('blocked reason visible in live gate', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    renderUserPanel()
    expect(screen.getByText('Canlı uygulamalı test henüz yetkilendirilmedi.')).toBeInTheDocument()
  })

  test('secrets not visible in rendered output', () => {
    mockUseControlPlane.mockReturnValue({ state: EMPTY_STATE, status: 'ready', refresh: vi.fn() })
    const { container } = renderUserPanel()
    const text = container.innerText ?? ''
    expect(text).not.toMatch(/api_key|secret|password|token|credential/i)
  })
})
