import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <div style={{ fontFamily: 'system-ui, sans-serif', minHeight: '100vh' }}>
      <nav style={{ padding: '12px 24px', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '16px' }}>
        <Link to="/" style={{ textDecoration: 'none', fontWeight: 600, color: '#111' }}>POLYPRO</Link>
        <Link to="/user" style={{ textDecoration: 'none', color: '#6b7280' }}>User</Link>
        <Link to="/admin" style={{ textDecoration: 'none', color: '#6b7280' }}>Admin</Link>
      </nav>
      <main style={{ padding: '24px' }}>{children}</main>
    </div>
  )
}
