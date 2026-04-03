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

describe('Routes render', () => {
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
    expect(screen.getByText('Admin Panel')).toBeInTheDocument()
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
