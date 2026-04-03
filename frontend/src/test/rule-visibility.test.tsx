/** rule-visibility.test.tsx — v1.1.1
 * Tests for:
 * - RulesPanel visibility enforcement (visible_rules)
 * - RulesPanel editability enforcement (editable_rules)
 * - UserPanel rules panel gate (visible_panels)
 */
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import RulesPanel from '../components/RulesPanel'
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

// ── RulesPanel component tests ────────────────────────────────────────────────

describe('RulesPanel', () => {
  test('shows all known rules when visible_rules is empty', () => {
    render(<RulesPanel visibleRules={[]} editableRules={[]} />)
    expect(screen.getByText('Zaman Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Fiyat Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Hareket Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Spread Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Etkinlik Limiti Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Maksimum Pozisyon Kuralı')).toBeInTheDocument()
  })

  test('shows only listed rules when visible_rules is non-empty', () => {
    render(<RulesPanel visibleRules={['time_rule', 'price_rule']} editableRules={[]} />)
    expect(screen.getByText('Zaman Kuralı')).toBeInTheDocument()
    expect(screen.getByText('Fiyat Kuralı')).toBeInTheDocument()
    expect(screen.queryByText('Hareket Kuralı')).not.toBeInTheDocument()
    expect(screen.queryByText('Spread Kuralı')).not.toBeInTheDocument()
    expect(screen.queryByText('Etkinlik Limiti Kuralı')).not.toBeInTheDocument()
    expect(screen.queryByText('Maksimum Pozisyon Kuralı')).not.toBeInTheDocument()
  })

  test('shows single rule correctly', () => {
    render(<RulesPanel visibleRules={['spread_rule']} editableRules={[]} />)
    expect(screen.getByText('Spread Kuralı')).toBeInTheDocument()
    expect(screen.queryByText('Zaman Kuralı')).not.toBeInTheDocument()
  })

  test('all rules show Salt Okunur badge when editable_rules is empty', () => {
    render(<RulesPanel visibleRules={[]} editableRules={[]} />)
    const readonly = screen.getAllByText('Salt Okunur')
    expect(readonly.length).toBe(6) // all 6 known rules
    expect(screen.queryByText('Düzenlenebilir')).not.toBeInTheDocument()
  })

  test('rule in editable_rules shows Düzenlenebilir badge', () => {
    render(<RulesPanel visibleRules={[]} editableRules={['time_rule']} />)
    expect(screen.getByTestId('rule-editable-time_rule')).toBeInTheDocument()
    expect(screen.getByText('Düzenlenebilir')).toBeInTheDocument()
  })

  test('rule not in editable_rules shows Salt Okunur badge', () => {
    render(<RulesPanel visibleRules={[]} editableRules={['time_rule']} />)
    expect(screen.getByTestId('rule-readonly-price_rule')).toBeInTheDocument()
  })

  test('multiple editable rules all show Düzenlenebilir', () => {
    render(<RulesPanel visibleRules={[]} editableRules={['time_rule', 'price_rule', 'move_rule']} />)
    expect(screen.getAllByText('Düzenlenebilir').length).toBe(3)
    expect(screen.getAllByText('Salt Okunur').length).toBe(3)
  })

  test('returns null when no rules are visible (all filtered out)', () => {
    const { container } = render(
      <RulesPanel visibleRules={['nonexistent_rule']} editableRules={[]} />
    )
    expect(container.firstChild).toBeNull()
  })

  test('renders panel testid', () => {
    render(<RulesPanel visibleRules={[]} editableRules={[]} />)
    expect(screen.getByTestId('rules-panel')).toBeInTheDocument()
  })

  test('renders correct row testids', () => {
    render(<RulesPanel visibleRules={['time_rule']} editableRules={[]} />)
    expect(screen.getByTestId('rule-row-time_rule')).toBeInTheDocument()
  })

  test('shows Strateji Kuralları heading', () => {
    render(<RulesPanel visibleRules={[]} editableRules={[]} />)
    expect(screen.getByText('Strateji Kuralları')).toBeInTheDocument()
  })
})

// ── UserPanel rules panel gate tests ─────────────────────────────────────────

describe('UserPanel rules panel gate', () => {
  beforeEach(() => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'polypro_session_token') return 'test-token'
      return null
    })
  })

  test('shows rules panel when visible_panels is empty (default: all panels visible)', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: [], visible_rules: [] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByTestId('rules-panel')).toBeInTheDocument()
  })

  test('shows rules panel when "rules" is in visible_panels', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: ['rules'], visible_rules: [] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByTestId('rules-panel')).toBeInTheDocument()
  })

  test('hides rules panel when visible_panels excludes "rules"', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: { ...baseEntitlement, visible_panels: ['balance', 'pnl'], visible_rules: [] },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.queryByTestId('rules-panel')).not.toBeInTheDocument()
  })

  test('UserPanel passes visible_rules to RulesPanel — filters rules', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: {
        ...baseEntitlement,
        visible_panels: [],
        visible_rules: ['time_rule'],
        editable_rules: [],
      },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByText('Zaman Kuralı')).toBeInTheDocument()
    expect(screen.queryByText('Fiyat Kuralı')).not.toBeInTheDocument()
  })

  test('UserPanel passes editable_rules to RulesPanel — marks editable', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: {
        ...baseEntitlement,
        visible_panels: [],
        visible_rules: ['time_rule', 'price_rule'],
        editable_rules: ['time_rule'],
      },
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByTestId('rule-editable-time_rule')).toBeInTheDocument()
    expect(screen.getByTestId('rule-readonly-price_rule')).toBeInTheDocument()
  })

  test('no entitlement: rules panel shown with all rules (default open)', () => {
    mockEntitlement = vi.fn().mockReturnValue({
      entitlement: null,
      loading: false,
      error: null,
    })
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    // No entitlement: visible_panels=[], visible_rules=[] → all panels + all rules shown
    expect(screen.getByTestId('rules-panel')).toBeInTheDocument()
  })
})
