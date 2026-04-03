import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Launcher from '../routes/Launcher'
import UserPanel from '../routes/UserPanel'
import AdminPanel from '../routes/AdminPanel'
import Settings from '../routes/Settings'
import NotFound from '../routes/NotFound'

vi.mock('../hooks/useReadiness', () => ({
  useReadiness: () => ({ state: null, status: 'loading', refresh: vi.fn() }),
}))

vi.mock('../hooks/useAdminUsers', () => ({
  useAdminUsers: () => ({
    users: [],
    summary: {
      online_user_count: 0,
      total_user_count: 0,
      active_bot_count: 0,
      open_position_count: 0,
      closed_position_count: 0,
      blocked_trade_count: 0,
      alert_count: 0,
    },
    loading: false,
    error: null,
    fetchUsers: vi.fn(),
    getEntitlement: vi.fn(),
    updateEntitlement: vi.fn(),
  }),
}))

describe('Routes render', () => {
  beforeEach(() => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
      if (key === 'session_token' || key === 'polypro_session_token') return 'test-token'
      return null
    })
  })

  test('Launcher renders heading', () => {
    render(<MemoryRouter><Launcher /></MemoryRouter>)
    expect(screen.getByText('POLYPRO Başlatıcı')).toBeInTheDocument()
  })

  test('UserPanel renders heading', () => {
    render(<MemoryRouter><UserPanel /></MemoryRouter>)
    expect(screen.getByText('Kullanıcı Paneli')).toBeInTheDocument()
  })

  test('AdminPanel renders heading', () => {
    render(<MemoryRouter><AdminPanel /></MemoryRouter>)
    expect(screen.getByText('Admin Control Panel')).toBeInTheDocument()
  })

  test('Settings renders heading', () => {
    render(<MemoryRouter><Settings /></MemoryRouter>)
    expect(screen.getByText('Ayarlar')).toBeInTheDocument()
  })

  test('NotFound renders heading', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Sayfa Bulunamadı')).toBeInTheDocument()
  })
})
