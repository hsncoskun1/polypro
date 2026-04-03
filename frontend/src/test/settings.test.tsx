/** settings.test.tsx — v0.9.0 settings UI component tests */
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import type { SettingsState } from '../types/settings'
import CredentialStatusPanel from '../components/CredentialStatusPanel'
import LiveConfigPanel from '../components/LiveConfigPanel'
import TradingConfigPanel from '../components/TradingConfigPanel'
import SettingsGateStatus from '../components/SettingsGateStatus'
import Settings from '../routes/Settings'

// --- Mock useSettings ---
const mockRefresh = vi.fn()
let mockStatus: 'loading' | 'ready' | 'error' = 'ready'
let mockState: SettingsState | null = null

vi.mock('../hooks/useSettings', () => ({
  useSettings: () => ({ state: mockState, status: mockStatus, refresh: mockRefresh }),
}))

const defaultState: SettingsState = {
  api_key_configured: false,
  api_secret_configured: false,
  api_passphrase_configured: false,
  relayer_api_configured: false,
  wallet_address_configured: false,
  funder_address_configured: false,
  private_key_configured: false,
  explicit_live_enable: false,
  live_test_gate_enabled: false,
  live_test_gate_passed: false,
  client_mode: 'simulation_mock',
  minimum_order_size: 0.0,
  selected_event: '',
  selected_market: '',
  release_ready: true,
  live_applied_testing_ready: false,
  blocked_reason_messages: ['Canlı uygulamalı test henüz yetkilendirilmedi.'],
  masked_secret_fields: [],
}

// --- CredentialStatusPanel ---
describe('CredentialStatusPanel', () => {
  test('shows heading', () => {
    render(<CredentialStatusPanel state={defaultState} />)
    expect(screen.getByText('Kimlik Bilgisi Durumu')).toBeInTheDocument()
  })

  test('shows security note', () => {
    render(<CredentialStatusPanel state={defaultState} />)
    expect(screen.getByText(/Değerler güvenlik nedeniyle/)).toBeInTheDocument()
  })

  test('shows API Anahtarı label', () => {
    render(<CredentialStatusPanel state={defaultState} />)
    expect(screen.getByText('API Anahtarı')).toBeInTheDocument()
  })

  test('shows Yapılandırılmadı when not configured', () => {
    render(<CredentialStatusPanel state={defaultState} />)
    const items = screen.getAllByText('— Yapılandırılmadı')
    expect(items.length).toBe(7)
  })

  test('shows Yapılandırıldı when configured', () => {
    const s = { ...defaultState, api_key_configured: true }
    render(<CredentialStatusPanel state={s} />)
    expect(screen.getByText('✓ Yapılandırıldı')).toBeInTheDocument()
  })

  test('shows all credential labels', () => {
    render(<CredentialStatusPanel state={defaultState} />)
    expect(screen.getByText('API Gizli Anahtarı')).toBeInTheDocument()
    expect(screen.getByText('API Parolası')).toBeInTheDocument()
    expect(screen.getByText('Aktarıcı API')).toBeInTheDocument()
    expect(screen.getByText('Cüzdan Adresi')).toBeInTheDocument()
    expect(screen.getByText('Finansör Adresi')).toBeInTheDocument()
    expect(screen.getByText('Özel Anahtar')).toBeInTheDocument()
  })

  test('never shows plaintext credential values', () => {
    const s = { ...defaultState, api_key_configured: true }
    render(<CredentialStatusPanel state={s} />)
    const content = document.body.textContent || ''
    // Status text only — no actual key values
    expect(content).not.toMatch(/[a-f0-9]{32,}/)  // no hex strings that look like keys
  })
})

// --- LiveConfigPanel ---
describe('LiveConfigPanel', () => {
  test('shows heading', () => {
    render(<LiveConfigPanel state={defaultState} />)
    expect(screen.getByText('Canlı Yapılandırma')).toBeInTheDocument()
  })

  test('shows explicit live enable label', () => {
    render(<LiveConfigPanel state={defaultState} />)
    expect(screen.getByText('Açık Canlı Etkinleştirme')).toBeInTheDocument()
  })

  test('shows live test gate enabled label', () => {
    render(<LiveConfigPanel state={defaultState} />)
    expect(screen.getByText('Canlı Test Kapısı Etkin')).toBeInTheDocument()
  })

  test('shows live test gate passed label', () => {
    render(<LiveConfigPanel state={defaultState} />)
    expect(screen.getByText('Canlı Test Kapısı Geçildi')).toBeInTheDocument()
  })

  test('all fields show Kapalı/Geçilmedi by default', () => {
    render(<LiveConfigPanel state={defaultState} />)
    const kapaliItems = screen.getAllByText('Kapalı')
    expect(kapaliItems.length).toBeGreaterThanOrEqual(2)
    expect(screen.getByText('Geçilmedi')).toBeInTheDocument()
  })

  test('explicit_live_enable true shows Etkin', () => {
    const s = { ...defaultState, explicit_live_enable: true }
    render(<LiveConfigPanel state={s} />)
    const etkinItems = screen.getAllByText('Etkin')
    expect(etkinItems.length).toBeGreaterThan(0)
  })
})

// --- TradingConfigPanel ---
describe('TradingConfigPanel', () => {
  test('shows heading', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('İşlem Yapılandırması')).toBeInTheDocument()
  })

  test('shows İstemci Modu label', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('İstemci Modu')).toBeInTheDocument()
  })

  test('shows simulation_mock in Turkish', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('Simülasyon (Mock)')).toBeInTheDocument()
  })

  test('shows minimum order label', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('Minimum Emir Boyutu')).toBeInTheDocument()
  })

  test('shows selected event label', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('Seçili Etkinlik')).toBeInTheDocument()
  })

  test('shows selected market label', () => {
    render(<TradingConfigPanel state={defaultState} />)
    expect(screen.getByText('Seçili Piyasa')).toBeInTheDocument()
  })

  test('empty event shows Seçilmedi', () => {
    render(<TradingConfigPanel state={defaultState} />)
    const items = screen.getAllByText('Seçilmedi')
    expect(items.length).toBeGreaterThanOrEqual(2)
  })

  test('shows selected event when set', () => {
    const s = { ...defaultState, selected_event: 'us-election-2024' }
    render(<TradingConfigPanel state={s} />)
    expect(screen.getByText('us-election-2024')).toBeInTheDocument()
  })
})

// --- SettingsGateStatus ---
describe('SettingsGateStatus', () => {
  test('shows heading', () => {
    render(<SettingsGateStatus state={defaultState} />)
    expect(screen.getByText('Yayın Durumu')).toBeInTheDocument()
  })

  test('shows release ready label', () => {
    render(<SettingsGateStatus state={defaultState} />)
    expect(screen.getByText('Yayın Hazırlığı')).toBeInTheDocument()
  })

  test('release_ready true shows Hazır', () => {
    render(<SettingsGateStatus state={defaultState} />)
    expect(screen.getByText('Hazır')).toBeInTheDocument()
  })

  test('live_applied_testing_ready false shows Kapalı', () => {
    render(<SettingsGateStatus state={defaultState} />)
    expect(screen.getByText('Kapalı')).toBeInTheDocument()
  })

  test('shows blocked reasons when present', () => {
    render(<SettingsGateStatus state={defaultState} />)
    expect(screen.getByText('• Canlı uygulamalı test henüz yetkilendirilmedi.')).toBeInTheDocument()
  })

  test('does not show blocked header when list is empty', () => {
    const s = { ...defaultState, blocked_reason_messages: [] }
    render(<SettingsGateStatus state={s} />)
    expect(screen.queryByText('Engel Nedenleri')).not.toBeInTheDocument()
  })
})

// --- Settings route integration ---
describe('Settings', () => {
  beforeEach(() => {
    mockStatus = 'ready'
    mockState = { ...defaultState }
  })

  test('shows heading', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Ayarlar')).toBeInTheDocument()
  })

  test('shows subheading', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Kimlik bilgisi durumu, canlı yapılandırma ve işlem ayarları.')).toBeInTheDocument()
  })

  test('shows loading state', () => {
    mockStatus = 'loading'
    mockState = null
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Yükleniyor...')).toBeInTheDocument()
  })

  test('shows error state', () => {
    mockStatus = 'error'
    mockState = null
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText(/Backend/)).toBeInTheDocument()
  })

  test('shows refresh button in error state', () => {
    mockStatus = 'error'
    mockState = null
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Yenile')).toBeInTheDocument()
  })

  test('shows no credentials banner when none configured', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText(/Hiçbir kimlik bilgisi yapılandırılmamış/)).toBeInTheDocument()
  })

  test('no credentials banner hidden when some configured', () => {
    mockState = { ...defaultState, masked_secret_fields: ['api_key'] }
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.queryByText(/Hiçbir kimlik bilgisi yapılandırılmamış/)).not.toBeInTheDocument()
  })

  test('shows credential status panel', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Kimlik Bilgisi Durumu')).toBeInTheDocument()
  })

  test('shows live config panel', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Canlı Yapılandırma')).toBeInTheDocument()
  })

  test('shows trading config panel', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('İşlem Yapılandırması')).toBeInTheDocument()
  })

  test('shows gate status panel', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Yayın Durumu')).toBeInTheDocument()
  })

  test('live_applied_testing_ready always false', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    const kapaliItems = screen.getAllByText('Kapalı')
    expect(kapaliItems.length).toBeGreaterThan(0)
  })

  test('no plaintext credentials visible', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    const content = document.body.textContent || ''
    const secretTerms = ['api_key', 'password', 'token', 'credential', 'private_key']
    // Only check that no actual secret values appear (labels are fine)
    expect(content.toLowerCase()).not.toContain('secret=')
    expect(content.toLowerCase()).not.toContain('key=0x')
    for (const term of secretTerms) {
      // Ensure these don't appear as values (raw hex etc)
      expect(content).not.toMatch(new RegExp(`${term}:[^\\s]`))
    }
  })
})
