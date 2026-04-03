/** entitlement-visibility.test.tsx — v1.0.9
 * Tests for:
 * - EntitlementEditor save/cancel/error flow
 * - UserPanel entitlement visibility enforcement
 */
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { EntitlementEditor } from '../components/admin/EntitlementEditor'
import UserPanel from '../routes/UserPanel'
import type { EntitlementResponse } from '../types/auth'

// ── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('../hooks/useControlPlane', () => ({
  useControlPlane: () => ({
    state: {
      open_positions: [],
      closed_positions: [],
      session_realized_pnl: 0,
      session_unrealized_pnl: 0,
      session_total_pnl: 0,
      total_balance: 0,
      available_balance: 0,
      current_balance: 0,
      session_start_balance: 0,
      claim_status: 'not_claimable_outcome_unknown',
      claim_available: false,
      claimed_amount: 0,
      settlement_completed_at: null,
      release_ready: true,
      live_applied_testing_ready: false,
      live_mode_ui_blocked: false,
      blocked_reason_messages: [],
    },
    status: 'ready',
    refresh: vi.fn(),
  }),
}))

let mockEntitlement: ReturnType<typeof vi.fn>
vi.mock('../hooks/useEntitlement', () => ({
  useEntitlement: () => mockEntitlement(),
}))

const baseEntitlement: EntitlementResponse = {
  user_id: 'u1',
  license_status: 'active',
  expires_at: null,
  trading_enabled: true,
  allowed_features: [],
  visible_panels: [],
  visible_rules: [],
  editable_rules: [],
  blocked_reason_messages: [],
}

// ── EntitlementEditor tests ──────────────────────────────────────────────────

describe('EntitlementEditor', () => {
  const noop = vi.fn()

  test('renders Save and Cancel buttons', () => {
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={baseEntitlement}
        onSave={async () => ({ ok: true })}
        onClose={noop}
      />
    )
    expect(screen.getByText('Save')).toBeInTheDocument()
    expect(screen.getByText('Cancel')).toBeInTheDocument()
  })

  test('renders blocked reason messages textarea', () => {
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={{ ...baseEntitlement, blocked_reason_messages: ['Lisans sona erdi'] }}
        onSave={async () => ({ ok: true })}
        onClose={noop}
      />
    )
    expect(screen.getByDisplayValue('Lisans sona erdi')).toBeInTheDocument()
  })

  test('shows save error when onSave returns ok: false', async () => {
    const onSaveFail = vi.fn().mockResolvedValue({ ok: false, error: 'Server error: could not save entitlement.' })
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={baseEntitlement}
        onSave={onSaveFail}
        onClose={noop}
      />
    )
    fireEvent.click(screen.getByText('Save'))
    await waitFor(() => {
      expect(screen.getByTestId('save-error')).toBeInTheDocument()
      expect(screen.getByText('Server error: could not save entitlement.')).toBeInTheDocument()
    })
  })

  test('calls onClose when save succeeds', async () => {
    const onClose = vi.fn()
    const onSaveOk = vi.fn().mockResolvedValue({ ok: true })
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={baseEntitlement}
        onSave={onSaveOk}
        onClose={onClose}
      />
    )
    fireEvent.click(screen.getByText('Save'))
    await waitFor(() => {
      expect(onClose).toHaveBeenCalled()
    })
  })

  test('calls onClose when Cancel clicked', () => {
    const onClose = vi.fn()
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={baseEntitlement}
        onSave={async () => ({ ok: true })}
        onClose={onClose}
      />
    )
    fireEvent.click(screen.getByText('Cancel'))
    expect(onClose).toHaveBeenCalled()
  })

  test('does not show save error initially', () => {
    render(
      <EntitlementEditor
        userId="u1"
        entitlement={baseEntitlement}
        onSave={async () => ({ ok: true })}
        onClose={noop}
      />
    )
    expect(screen.queryByTestId('save-error')).not.toBeInTheDocument()
  })
})

// ── UserPanel entitlement enforcement tests ──────────────────────────────────

describe('UserPanel entitlement enforcement', () => {
  beforeEach(() => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'polypro_session_token') return 'test-token'
      return null
    })
  })

  test('shows trading lock when trading_enabled is false', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, trading_enabled: false },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByTestId('trading-lock')).toBeInTheDocument()
    expect(screen.getByText('İşlem Kilidi Aktif')).toBeInTheDocument()
  })

  test('does not show trading lock when trading_enabled is true', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, trading_enabled: true },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.queryByTestId('trading-lock')).not.toBeInTheDocument()
  })

  test('shows blocked reason messages inside trading lock', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: {
        ...baseEntitlement,
        trading_enabled: false,
        blocked_reason_messages: ['Lisans sona erdi', 'Destek ile iletisime gecin'],
      },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByText('Lisans sona erdi')).toBeInTheDocument()
    expect(screen.getByText('Destek ile iletisime gecin')).toBeInTheDocument()
  })

  test('shows all panels when visible_panels is empty', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: [] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    // All panels rendered — check for known text from each panel
    expect(screen.getByText('Açık Pozisyonlar')).toBeInTheDocument()
    expect(screen.getByText('Kapalı Pozisyonlar')).toBeInTheDocument()
  })

  test('hides panels not in visible_panels', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: ['balance'] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.queryByText('Açık Pozisyonlar')).not.toBeInTheDocument()
    expect(screen.queryByText('Kapalı Pozisyonlar')).not.toBeInTheDocument()
  })

  test('shows panels included in visible_panels', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: ['positions', 'pnl'] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByText('Açık Pozisyonlar')).toBeInTheDocument()
    expect(screen.getByText('Kapalı Pozisyonlar')).toBeInTheDocument()
  })

  test('no trading lock when entitlement is null (default: enabled)', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: null,
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.queryByTestId('trading-lock')).not.toBeInTheDocument()
  })
})
