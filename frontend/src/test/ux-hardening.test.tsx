/** ux-hardening.test.tsx — v0.9.1 shared UX component tests */
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import PageShell from '../components/PageShell'
import AppFooter from '../components/AppFooter'
import NotFound from '../routes/NotFound'

// --- PageShell ---
describe('PageShell', () => {
  test('shows title', () => {
    render(
      <PageShell title="Test Başlığı" status="ready" onRefresh={vi.fn()}>
        <p>İçerik</p>
      </PageShell>
    )
    expect(screen.getByText('Test Başlığı')).toBeInTheDocument()
  })

  test('shows subtitle when provided', () => {
    render(
      <PageShell title="T" subtitle="Alt başlık" status="ready" onRefresh={vi.fn()}>
        <p>content</p>
      </PageShell>
    )
    expect(screen.getByText('Alt başlık')).toBeInTheDocument()
  })

  test('shows loading skeleton when status=loading', () => {
    render(
      <PageShell title="T" status="loading" onRefresh={vi.fn()}>
        <p>content</p>
      </PageShell>
    )
    expect(screen.getByLabelText('Yükleniyor')).toBeInTheDocument()
    expect(screen.queryByText('content')).not.toBeInTheDocument()
  })

  test('shows error banner when status=error', () => {
    render(
      <PageShell title="T" status="error" onRefresh={vi.fn()}>
        <p>content</p>
      </PageShell>
    )
    expect(screen.getByText(/Backend/)).toBeInTheDocument()
    expect(screen.queryByText('content')).not.toBeInTheDocument()
  })

  test('shows refresh button in error state', () => {
    const refresh = vi.fn()
    render(
      <PageShell title="T" status="error" onRefresh={refresh}>
        <p>content</p>
      </PageShell>
    )
    expect(screen.getByText('Yenile')).toBeInTheDocument()
  })

  test('shows children when status=ready', () => {
    render(
      <PageShell title="T" status="ready" onRefresh={vi.fn()}>
        <p>Görünür içerik</p>
      </PageShell>
    )
    expect(screen.getByText('Görünür içerik')).toBeInTheDocument()
  })

  test('hides children when loading', () => {
    render(
      <PageShell title="T" status="loading" onRefresh={vi.fn()}>
        <p>Gizli içerik</p>
      </PageShell>
    )
    expect(screen.queryByText('Gizli içerik')).not.toBeInTheDocument()
  })

  test('hides children when error', () => {
    render(
      <PageShell title="T" status="error" onRefresh={vi.fn()}>
        <p>Gizli içerik</p>
      </PageShell>
    )
    expect(screen.queryByText('Gizli içerik')).not.toBeInTheDocument()
  })

  test('works without subtitle', () => {
    render(
      <PageShell title="Başlık" status="ready">
        <p>içerik</p>
      </PageShell>
    )
    expect(screen.getByText('Başlık')).toBeInTheDocument()
  })

  test('works without onRefresh in error state', () => {
    render(
      <PageShell title="T" status="error">
        <p>content</p>
      </PageShell>
    )
    expect(screen.getByText(/Backend/)).toBeInTheDocument()
    expect(screen.queryByText('Yenile')).not.toBeInTheDocument()
  })
})

// --- AppFooter ---
describe('AppFooter', () => {
  test('shows frontend port', () => {
    render(<AppFooter />)
    expect(screen.getByText(':5173')).toBeInTheDocument()
  })

  test('shows backend port', () => {
    render(<AppFooter />)
    expect(screen.getByText(':8000')).toBeInTheDocument()
  })

  test('shows startup commands', () => {
    render(<AppFooter />)
    expect(screen.getByText('uvicorn')).toBeInTheDocument()
    expect(screen.getByText('vite')).toBeInTheDocument()
  })

  test('shows POLYPRO label', () => {
    render(<AppFooter />)
    expect(screen.getByText('POLYPRO')).toBeInTheDocument()
  })
})

// --- NotFound ---
describe('NotFound', () => {
  test('shows page not found heading', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Sayfa Bulunamadı')).toBeInTheDocument()
  })

  test('shows explanation text', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText(/İstediğiniz sayfa mevcut değil/)).toBeInTheDocument()
  })

  test('shows link to launcher', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Başlatıcıya Dön')).toBeInTheDocument()
  })

  test('shows link to user panel', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Kullanıcı Paneli')).toBeInTheDocument()
  })

  test('shows link to admin panel', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Admin Panel')).toBeInTheDocument()
  })

  test('shows link to settings', () => {
    render(<MemoryRouter><NotFound /></MemoryRouter>)
    expect(screen.getByText('Ayarlar')).toBeInTheDocument()
  })
})
