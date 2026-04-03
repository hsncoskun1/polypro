/** admin-control-plane.test.tsx — v0.8.9 admin UI component tests */
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { AdminControlPlaneState } from '../types/adminControlPlane'
import OperationalControlPanel from '../components/OperationalControlPanel'
import AdminFinancialSummary from '../components/AdminFinancialSummary'
import BlockedEventsPanel from '../components/BlockedEventsPanel'
import ExecutionReportPanel from '../components/ExecutionReportPanel'
import AdminReleaseGate from '../components/AdminReleaseGate'
import AdminPanel from '../routes/AdminPanel'

// --- Mock useAdminControlPlane ---
const mockRefresh = vi.fn()
let mockStatus: 'loading' | 'ready' | 'error' = 'ready'
let mockState: AdminControlPlaneState | null = null

vi.mock('../hooks/useAdminControlPlane', () => ({
  useAdminControlPlane: () => ({ state: mockState, status: mockStatus, refresh: mockRefresh }),
}))

const defaultState: AdminControlPlaneState = {
  safe_stop_active: false,
  safe_stop_reason: '',
  scheduler_enabled: true,
  global_disable_active: false,
  config_reload_available: true,
  config_reset_available: true,
  total_balance: 0.0,
  available_balance: 0.0,
  current_balance: 0.0,
  session_start_balance: 0.0,
  realized_pnl: 0.0,
  unrealized_pnl: 0.0,
  session_total_pnl: 0.0,
  claim_adjusted_balance_effect: 0.0,
  blocked_trades: [],
  blocked_rules: [],
  blocked_risk_events: [],
  execution_fill_events: [],
  claim_events: [],
  operational_alerts: [],
  release_ready: true,
  live_applied_testing_ready: false,
}

// --- OperationalControlPanel ---
describe('OperationalControlPanel', () => {
  test('shows heading', () => {
    render(<OperationalControlPanel state={defaultState} />)
    expect(screen.getByText('Operasyonel Kontrol')).toBeInTheDocument()
  })

  test('shows safe stop label', () => {
    render(<OperationalControlPanel state={defaultState} />)
    expect(screen.getByText('Güvenli Durdurma')).toBeInTheDocument()
  })

  test('safe stop inactive shows Pasif', () => {
    render(<OperationalControlPanel state={defaultState} />)
    const pasifElements = screen.getAllByText('Pasif')
    expect(pasifElements.length).toBeGreaterThan(0)
  })

  test('safe stop active shows Aktif', () => {
    render(<OperationalControlPanel state={{ ...defaultState, safe_stop_active: true }} />)
    const aktifElements = screen.getAllByText('Aktif')
    expect(aktifElements.length).toBeGreaterThan(0)
  })

  test('scheduler enabled shows Etkin', () => {
    render(<OperationalControlPanel state={defaultState} />)
    expect(screen.getByText('Etkin')).toBeInTheDocument()
  })

  test('global disable shows label', () => {
    render(<OperationalControlPanel state={defaultState} />)
    expect(screen.getByText('Genel Devre Dışı')).toBeInTheDocument()
  })

  test('config reload shows Mevcut', () => {
    render(<OperationalControlPanel state={defaultState} />)
    const mevcutElements = screen.getAllByText('Mevcut')
    expect(mevcutElements.length).toBeGreaterThanOrEqual(2)
  })

  test('shows safe stop reason when active', () => {
    const s = { ...defaultState, safe_stop_active: true, safe_stop_reason: 'Test durumu' }
    render(<OperationalControlPanel state={s} />)
    expect(screen.getByText('• Test durumu')).toBeInTheDocument()
  })
})

// --- AdminFinancialSummary ---
describe('AdminFinancialSummary', () => {
  test('shows heading', () => {
    render(<AdminFinancialSummary state={defaultState} />)
    expect(screen.getByText('Finansal Özet')).toBeInTheDocument()
  })

  test('shows all balance labels', () => {
    render(<AdminFinancialSummary state={defaultState} />)
    expect(screen.getByText('Toplam Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Kullanılabilir Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Güncel Bakiye')).toBeInTheDocument()
    expect(screen.getByText('Seans Başlangıç Bakiyesi')).toBeInTheDocument()
  })

  test('shows pnl labels', () => {
    render(<AdminFinancialSummary state={defaultState} />)
    expect(screen.getByText('Gerçekleşen K/Z')).toBeInTheDocument()
    expect(screen.getByText('Gerçekleşmemiş K/Z')).toBeInTheDocument()
    expect(screen.getByText('Seans Toplam K/Z')).toBeInTheDocument()
  })

  test('shows claim adjusted label', () => {
    render(<AdminFinancialSummary state={defaultState} />)
    expect(screen.getByText('Talep Düzeltilmiş Bakiye Etkisi')).toBeInTheDocument()
  })

  test('positive pnl shows + prefix', () => {
    render(<AdminFinancialSummary state={{ ...defaultState, realized_pnl: 10 }} />)
    expect(screen.getByText('+10.0000')).toBeInTheDocument()
  })
})

// --- BlockedEventsPanel ---
describe('BlockedEventsPanel', () => {
  test('shows heading', () => {
    render(<BlockedEventsPanel state={defaultState} />)
    expect(screen.getByText('Bloke Olaylar')).toBeInTheDocument()
  })

  test('shows empty trade message', () => {
    render(<BlockedEventsPanel state={defaultState} />)
    expect(screen.getByText('Bloke işlem yok')).toBeInTheDocument()
  })

  test('shows empty rule message', () => {
    render(<BlockedEventsPanel state={defaultState} />)
    expect(screen.getByText('Bloke kural yok')).toBeInTheDocument()
  })

  test('shows empty risk message', () => {
    render(<BlockedEventsPanel state={defaultState} />)
    expect(screen.getByText('Bloke risk olayı yok')).toBeInTheDocument()
  })

  test('shows blocked trade item', () => {
    const s = { ...defaultState, blocked_trades: ['Trade-001 bloke edildi'] }
    render(<BlockedEventsPanel state={s} />)
    expect(screen.getByText('• Trade-001 bloke edildi')).toBeInTheDocument()
  })

  test('shows blocked rule item', () => {
    const s = { ...defaultState, blocked_rules: ['Kural-A bloke'] }
    render(<BlockedEventsPanel state={s} />)
    expect(screen.getByText('• Kural-A bloke')).toBeInTheDocument()
  })
})

// --- ExecutionReportPanel ---
describe('ExecutionReportPanel', () => {
  test('shows heading', () => {
    render(<ExecutionReportPanel state={defaultState} />)
    expect(screen.getByText('Gerçekleşme ve Uyarı Raporu')).toBeInTheDocument()
  })

  test('shows empty fill message', () => {
    render(<ExecutionReportPanel state={defaultState} />)
    expect(screen.getByText('Gerçekleşme olayı yok')).toBeInTheDocument()
  })

  test('shows empty claim message', () => {
    render(<ExecutionReportPanel state={defaultState} />)
    expect(screen.getByText('Talep olayı yok')).toBeInTheDocument()
  })

  test('shows empty alert message', () => {
    render(<ExecutionReportPanel state={defaultState} />)
    expect(screen.getByText('Uyarı yok')).toBeInTheDocument()
  })

  test('shows fill event item', () => {
    const s = { ...defaultState, execution_fill_events: ['Fill #42 tamamlandı'] }
    render(<ExecutionReportPanel state={s} />)
    expect(screen.getByText('• Fill #42 tamamlandı')).toBeInTheDocument()
  })

  test('shows operational alert item', () => {
    const s = { ...defaultState, operational_alerts: ['Yüksek gecikme uyarısı'] }
    render(<ExecutionReportPanel state={s} />)
    expect(screen.getByText('• Yüksek gecikme uyarısı')).toBeInTheDocument()
  })
})

// --- AdminReleaseGate ---
describe('AdminReleaseGate', () => {
  test('shows heading', () => {
    render(<AdminReleaseGate state={defaultState} />)
    expect(screen.getByText('Yayın Kapısı')).toBeInTheDocument()
  })

  test('shows release ready label', () => {
    render(<AdminReleaseGate state={defaultState} />)
    expect(screen.getByText('Yayın Hazırlığı')).toBeInTheDocument()
  })

  test('release_ready true shows Hazır', () => {
    render(<AdminReleaseGate state={defaultState} />)
    expect(screen.getByText('Hazır')).toBeInTheDocument()
  })

  test('live_applied_testing_ready false shows Kapalı', () => {
    render(<AdminReleaseGate state={defaultState} />)
    expect(screen.getByText('Kapalı')).toBeInTheDocument()
  })

  test('shows live testing label', () => {
    render(<AdminReleaseGate state={defaultState} />)
    expect(screen.getByText('Canlı Uygulamalı Test')).toBeInTheDocument()
  })
})

// --- AdminPanel integration ---
describe('AdminPanel', () => {
  beforeEach(() => {
    mockStatus = 'ready'
    mockState = { ...defaultState }
  })

  test('shows heading', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Admin Panel')).toBeInTheDocument()
  })

  test('shows subheading', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Operasyonel kontrol, finansal raporlama ve sistem durumu.')).toBeInTheDocument()
  })

  test('shows loading state', () => {
    mockStatus = 'loading'
    mockState = null
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByLabelText('Yükleniyor')).toBeInTheDocument()
  })

  test('shows error state', () => {
    mockStatus = 'error'
    mockState = null
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText(/Backend/)).toBeInTheDocument()
  })

  test('shows refresh button in error state', () => {
    mockStatus = 'error'
    mockState = null
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Yenile')).toBeInTheDocument()
  })

  test('shows operational control panel when ready', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Operasyonel Kontrol')).toBeInTheDocument()
  })

  test('shows financial summary when ready', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Finansal Özet')).toBeInTheDocument()
  })

  test('shows blocked events panel when ready', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Bloke Olaylar')).toBeInTheDocument()
  })

  test('shows execution report panel when ready', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Gerçekleşme ve Uyarı Raporu')).toBeInTheDocument()
  })

  test('shows release gate when ready', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Yayın Kapısı')).toBeInTheDocument()
  })

  test('global disable banner shown when active', () => {
    mockState = { ...defaultState, global_disable_active: true }
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText(/Genel devre dışı aktif/)).toBeInTheDocument()
  })

  test('safe stop banner shown when active', () => {
    mockState = { ...defaultState, safe_stop_active: true, safe_stop_reason: 'Test' }
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText(/Güvenli durdurma aktif/)).toBeInTheDocument()
  })

  test('no safe stop banner when inactive', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.queryByText(/Güvenli durdurma aktif/)).not.toBeInTheDocument()
  })

  test('live_applied_testing_ready always false in default state', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Kapalı')).toBeInTheDocument()
  })

  test('no secret fields visible', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    const content = document.body.innerText || document.body.textContent || ''
    const secretTerms = ['api_key', 'password', 'token', 'credential', 'secret']
    for (const term of secretTerms) {
      expect(content.toLowerCase()).not.toContain(term)
    }
  })
})
