/** audit-trail.test.tsx — v1.1.2
 * Tests for:
 * - AuditTrailPanel rendering states
 * - AdminPanel audit integration
 */
import { describe, test, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuditTrailPanel } from '../components/admin/AuditTrailPanel'
import AdminPanel from '../routes/AdminPanel'
import type { PolicyAuditRecord } from '../hooks/useAdminAudit'

// ── Mocks ────────────────────────────────────────────────────────────────────

vi.mock('../hooks/useAdminUsers', () => ({
  useAdminUsers: () => ({
    users: [],
    summary: null,
    loading: false,
    error: null,
    fetchUsers: vi.fn(),
    getEntitlement: vi.fn(),
    updateEntitlement: vi.fn(),
  }),
}))

let mockAudit: ReturnType<typeof vi.fn>
vi.mock('../hooks/useAdminAudit', () => ({
  useAdminAudit: () => mockAudit(),
}))

const SAMPLE_RECORD: PolicyAuditRecord = {
  audit_id: 'audit-001',
  actor_id: 'admin-1',
  target_user_id: 'user-1',
  action: 'update_entitlement',
  snapshot_before: { trading_enabled: false },
  snapshot_after: { trading_enabled: true },
  changed_at: '2026-01-01T12:00:00+00:00',
  changed_fields: ['trading_enabled'],
}

// ── AuditTrailPanel tests ─────────────────────────────────────────────────────

describe('AuditTrailPanel', () => {
  test('shows loading state', () => {
    render(<AuditTrailPanel records={[]} loading={true} error={null} />)
    expect(screen.getByTestId('audit-loading')).toBeInTheDocument()
  })

  test('shows error state', () => {
    render(<AuditTrailPanel records={[]} loading={false} error="403" />)
    expect(screen.getByTestId('audit-error')).toBeInTheDocument()
    expect(screen.getByText(/403/)).toBeInTheDocument()
  })

  test('shows empty state when no records', () => {
    render(<AuditTrailPanel records={[]} loading={false} error={null} />)
    expect(screen.getByTestId('audit-empty')).toBeInTheDocument()
    expect(screen.getByText('Kayıt bulunamadı.')).toBeInTheDocument()
  })

  test('renders audit record with action', () => {
    render(<AuditTrailPanel records={[SAMPLE_RECORD]} loading={false} error={null} />)
    expect(screen.getByText('update_entitlement')).toBeInTheDocument()
  })

  test('shows changed fields', () => {
    render(<AuditTrailPanel records={[SAMPLE_RECORD]} loading={false} error={null} />)
    expect(screen.getByText('trading_enabled')).toBeInTheDocument()
  })

  test('shows actor_id', () => {
    render(<AuditTrailPanel records={[SAMPLE_RECORD]} loading={false} error={null} />)
    expect(screen.getByText(/admin-1/)).toBeInTheDocument()
  })

  test('renders panel testid', () => {
    render(<AuditTrailPanel records={[SAMPLE_RECORD]} loading={false} error={null} />)
    expect(screen.getByTestId('audit-trail-panel')).toBeInTheDocument()
  })

  test('renders record testid with audit_id', () => {
    render(<AuditTrailPanel records={[SAMPLE_RECORD]} loading={false} error={null} />)
    expect(screen.getByTestId('audit-record-audit-001')).toBeInTheDocument()
  })

  test('renders heading', () => {
    render(<AuditTrailPanel records={[]} loading={false} error={null} />)
    expect(screen.getByText('Politika Değişiklik Geçmişi')).toBeInTheDocument()
  })

  test('renders multiple records', () => {
    const r2 = { ...SAMPLE_RECORD, audit_id: 'audit-002' }
    render(<AuditTrailPanel records={[SAMPLE_RECORD, r2]} loading={false} error={null} />)
    expect(screen.getByTestId('audit-record-audit-001')).toBeInTheDocument()
    expect(screen.getByTestId('audit-record-audit-002')).toBeInTheDocument()
  })

  test('does not show changed_fields section when empty', () => {
    const r = { ...SAMPLE_RECORD, changed_fields: [] }
    render(<AuditTrailPanel records={[r]} loading={false} error={null} />)
    expect(screen.queryByText('Değişen alanlar:')).not.toBeInTheDocument()
  })
})

// ── AdminPanel audit integration ──────────────────────────────────────────────

describe('AdminPanel audit integration', () => {
  beforeEach(() => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'polypro_session_token') return 'admin-token'
      return null
    })
    mockAudit = vi.fn().mockReturnValue({
      records: [],
      loading: false,
      error: null,
    })
  })

  test('renders without crashing', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Admin Control Panel')).toBeInTheDocument()
  })

  test('does not show AuditTrailPanel when no user is selected', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.queryByTestId('audit-trail-panel')).not.toBeInTheDocument()
  })
})
