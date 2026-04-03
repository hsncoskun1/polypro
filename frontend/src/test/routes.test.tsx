import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Home from '../routes/Home'
import UserPanel from '../routes/UserPanel'
import AdminPanel from '../routes/AdminPanel'
import Settings from '../routes/Settings'
import NotFound from '../routes/NotFound'

describe('Routes render', () => {
  test('Home renders heading', () => {
    render(<MemoryRouter><Home /></MemoryRouter>)
    expect(screen.getByText('POLYPRO')).toBeInTheDocument()
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
