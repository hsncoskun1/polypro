/** launcher.test.tsx — v1.1.0 Launcher + Readiness + Launcher Grant Gate tests */

import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { vi } from 'vitest'

import ReadinessCard from '../components/ReadinessCard'
import BlockedReasonList from '../components/BlockedReasonList'
import ReleaseGatePanel from '../components/ReleaseGatePanel'
import PortInfo from '../components/PortInfo'
import Launcher from '../routes/Launcher'

// ── useReadiness mock ────────────────────────────────────────────────────────

vi.mock('../hooks/useReadiness', () => ({
  useReadiness: vi.fn(),
}))

vi.mock('../hooks/useLauncherStatus', () => ({
  useLauncherStatus: vi.fn(),
}))

import { useReadiness } from '../hooks/useReadiness'
import { useLauncherStatus } from '../hooks/useLauncherStatus'
const mockUseReadiness = vi.mocked(useReadiness)
const mockUseLauncherStatus = vi.mocked(useLauncherStatus)

// ── ReadinessCard ────────────────────────────────────────────────────────────

describe('ReadinessCard', () => {
  test('shows label', () => {
    render(<ReadinessCard label="Backend Hazırlık" value={true} />)
    expect(screen.getByText('Backend Hazırlık')).toBeInTheDocument()
  })

  test('shows Hazır when value=true', () => {
    render(<ReadinessCard label="X" value={true} />)
    expect(screen.getByText('Hazır')).toBeInTheDocument()
  })

  test('shows Hazır Değil when value=false', () => {
    render(<ReadinessCard label="X" value={false} />)
    expect(screen.getByText('Hazır Değil')).toBeInTheDocument()
  })

  test('shows loading placeholder when value=null', () => {
    render(<ReadinessCard label="X" value={null} />)
    expect(screen.getByText('…')).toBeInTheDocument()
  })

  test('informational=true does not show red text when false', () => {
    const { container } = render(
      <ReadinessCard label="X" value={false} informational={true} />
    )
    expect(container.querySelector('.text-red-400')).toBeNull()
  })

  test('non-informational false shows red dot class', () => {
    const { container } = render(<ReadinessCard label="X" value={false} />)
    expect(container.querySelector('.bg-red-500')).not.toBeNull()
  })
})

// ── BlockedReasonList ────────────────────────────────────────────────────────

describe('BlockedReasonList', () => {
  test('renders nothing when messages is empty', () => {
    const { container } = render(<BlockedReasonList messages={[]} />)
    expect(container.firstChild).toBeNull()
  })

  test('renders each message', () => {
    render(
      <BlockedReasonList
        messages={['Sebep 1', 'Sebep 2']}
      />
    )
    expect(screen.getByText('Sebep 1')).toBeInTheDocument()
    expect(screen.getByText('Sebep 2')).toBeInTheDocument()
  })

  test('shows Engel Nedenleri heading', () => {
    render(<BlockedReasonList messages={['x']} />)
    expect(screen.getByText('Engel Nedenleri')).toBeInTheDocument()
  })
})

// ── ReleaseGatePanel ─────────────────────────────────────────────────────────

describe('ReleaseGatePanel', () => {
  test('shows both gate labels', () => {
    render(<ReleaseGatePanel releaseReady={true} liveAppliedTestingReady={false} />)
    expect(screen.getByText(/release_ready/)).toBeInTheDocument()
    expect(screen.getByText(/live_applied_testing_ready/)).toBeInTheDocument()
  })

  test('shows Acik for true value', () => {
    render(<ReleaseGatePanel releaseReady={true} liveAppliedTestingReady={false} />)
    expect(screen.getByText('Açık')).toBeInTheDocument()
  })

  test('shows Kapali for false value', () => {
    render(<ReleaseGatePanel releaseReady={false} liveAppliedTestingReady={false} />)
    expect(screen.getAllByText('Kapalı').length).toBeGreaterThan(0)
  })

  test('shows loading dots for null values', () => {
    render(<ReleaseGatePanel releaseReady={null} liveAppliedTestingReady={null} />)
    expect(screen.getAllByText('…').length).toBe(2)
  })

  test('shows note for live_applied_testing_ready', () => {
    render(<ReleaseGatePanel releaseReady={true} liveAppliedTestingReady={false} />)
    expect(screen.getByText('Manuel yetkilendirme gerektirir')).toBeInTheDocument()
  })
})

// ── PortInfo ─────────────────────────────────────────────────────────────────

describe('PortInfo', () => {
  test('shows frontend port', () => {
    render(<PortInfo frontendPort={5173} backendPort={8000} />)
    expect(screen.getByText('http://localhost:5173')).toBeInTheDocument()
  })

  test('shows backend port', () => {
    render(<PortInfo frontendPort={5173} backendPort={8000} />)
    expect(screen.getByText('http://localhost:8000')).toBeInTheDocument()
  })

  test('shows startup commands', () => {
    render(<PortInfo frontendPort={5173} backendPort={8000} />)
    expect(screen.getByText(/npm run dev/)).toBeInTheDocument()
    expect(screen.getByText(/uvicorn/)).toBeInTheDocument()
  })
})

// ── Launcher ─────────────────────────────────────────────────────────────────

const READY_STATE = {
  launcher_blocked: false,
  setup_completed: true,
  update_required: false,
  preflight_passed: true,
  backend_ready: true,
  final_backend_ready: true,
  release_ready: true,
  live_applied_testing_ready: false,
  blocked_reason_messages: [],
  continue_destination: '/user',
  frontend_port: 5173,
  backend_port: 8000,
  readiness_poll_interval_ms: 5000,
}

const BLOCKED_STATE = {
  ...READY_STATE,
  launcher_blocked: true,
  blocked_reason_messages: ['Canlı uygulamalı test henüz yetkilendirilmedi.'],
}

function renderLauncher() {
  return render(
    <MemoryRouter>
      <Launcher />
    </MemoryRouter>
  )
}

describe('Launcher', () => {
  afterEach(() => vi.clearAllMocks())

  beforeEach(() => {
    // Default: grant not required, not launched
    mockUseLauncherStatus.mockReturnValue({ status: 'ready', data: { launched: false, grant_required: false } })
  })

  test('shows loading skeleton when status=loading', () => {
    mockUseReadiness.mockReturnValue({ state: null, status: 'loading', refresh: vi.fn() })
    const { container } = renderLauncher()
    expect(container.querySelector('.animate-pulse')).not.toBeNull()
  })

  test('shows error message when status=error', () => {
    mockUseReadiness.mockReturnValue({ state: null, status: 'error', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText("Backend'e ulaşılamıyor.")).toBeInTheDocument()
  })

  test('refresh button calls refresh on error', () => {
    const refresh = vi.fn()
    mockUseReadiness.mockReturnValue({ state: null, status: 'error', refresh })
    renderLauncher()
    fireEvent.click(screen.getByText('Yenile'))
    expect(refresh).toHaveBeenCalledTimes(1)
  })

  test('shows readiness cards when state is available', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText('Backend Hazırlık')).toBeInTheDocument()
    expect(screen.getByText('Kurulum Tamamlandı')).toBeInTheDocument()
    expect(screen.getByText('Güncelleme Gerekli')).toBeInTheDocument()
    expect(screen.getByText('Ön Kontrol (Preflight)')).toBeInTheDocument()
    expect(screen.getByText('Backend Final Doğrulama')).toBeInTheDocument()
  })

  test('shows continue button when not blocked', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText('Uygulamaya Devam Et \u2192')).toBeInTheDocument()
  })

  test('shows blocked message when launcher_blocked=true', () => {
    mockUseReadiness.mockReturnValue({ state: BLOCKED_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText(/Başlatıcı kilitli/)).toBeInTheDocument()
  })

  test('shows blocked reasons when present', () => {
    mockUseReadiness.mockReturnValue({ state: BLOCKED_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText('Canlı uygulamalı test henüz yetkilendirilmedi.')).toBeInTheDocument()
  })

  test('shows release gate panel', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText(/Yayın ve Canlı Test Kapısı/i)).toBeInTheDocument()
  })

  test('shows port info', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    renderLauncher()
    expect(screen.getByText('http://localhost:5173')).toBeInTheDocument()
    expect(screen.getByText('http://localhost:8000')).toBeInTheDocument()
  })

  test('update_required=false is shown as OK (Hazir)', () => {
    // update_required=false => inverted to true => "Hazır"
    mockUseReadiness.mockReturnValue({
      state: { ...READY_STATE, update_required: false },
      status: 'ready',
      refresh: vi.fn(),
    })
    renderLauncher()
    // The row for "Güncelleme Gerekli" should show Hazır (inversion logic)
    const cards = screen.getAllByText('Hazır')
    expect(cards.length).toBeGreaterThan(0)
  })
})

// ── Launcher grant gate tests ─────────────────────────────────────────────────

describe('Launcher grant gate', () => {
  afterEach(() => vi.clearAllMocks())

  test('does not show grant gate when grant_required=false', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'ready', data: { launched: false, grant_required: false } })
    renderLauncher()
    expect(screen.queryByTestId('launcher-grant-gate')).not.toBeInTheDocument()
  })

  test('does not show grant gate when launched=true and grant_required=true', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'ready', data: { launched: true, grant_required: true } })
    renderLauncher()
    expect(screen.queryByTestId('launcher-grant-gate')).not.toBeInTheDocument()
  })

  test('shows grant gate when grant_required=true and launched=false', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'ready', data: { launched: false, grant_required: true } })
    renderLauncher()
    expect(screen.getByTestId('launcher-grant-gate')).toBeInTheDocument()
    expect(screen.getByText('Başlatıcı Yetkisi Gerekli')).toBeInTheDocument()
  })

  test('shows correct message in grant gate', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'ready', data: { launched: false, grant_required: true } })
    renderLauncher()
    expect(screen.getByText(/başlatıcı üzerinden başlatın/i)).toBeInTheDocument()
  })

  test('does not show grant gate when launcher status is loading', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'loading', data: null })
    renderLauncher()
    expect(screen.queryByTestId('launcher-grant-gate')).not.toBeInTheDocument()
  })

  test('does not show grant gate when launcher status is error', () => {
    mockUseReadiness.mockReturnValue({ state: READY_STATE, status: 'ready', refresh: vi.fn() })
    mockUseLauncherStatus.mockReturnValue({ status: 'error', data: null })
    renderLauncher()
    expect(screen.queryByTestId('launcher-grant-gate')).not.toBeInTheDocument()
  })
})
