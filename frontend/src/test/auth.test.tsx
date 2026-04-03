/**
 * Auth tests — v1.0.5
 */
import { render, screen } from '@testing-library/react'
import { MemoryRouter, Routes, Route, Navigate } from 'react-router-dom'
import Login from '../routes/Login'
import { useAuth } from '../hooks/useAuth'
import { renderHook, act } from '@testing-library/react'

// --- Login page renders ---

describe('Login page', () => {
  test('login page renders email/password fields and submit button', () => {
    render(
      <MemoryRouter>
        <Login onLogin={vi.fn()} />
      </MemoryRouter>
    )
    expect(screen.getByTestId('login-page')).toBeInTheDocument()
    expect(screen.getByTestId('login-email')).toBeInTheDocument()
    expect(screen.getByTestId('login-password')).toBeInTheDocument()
    expect(screen.getByTestId('login-submit')).toBeInTheDocument()
  })
})

// --- useAuth hook ---

describe('useAuth hook', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  test('stores session token on storeSession', () => {
    const { result } = renderHook(() => useAuth())
    act(() => {
      result.current.storeSession({
        session_token: 'tok123',
        user_id: 'uid1',
        email: 'test@example.com',
        role: 'user',
      })
    })
    expect(result.current.sessionToken).toBe('tok123')
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.role).toBe('user')
  })

  test('clears session on clearSession', () => {
    const { result } = renderHook(() => useAuth())
    act(() => {
      result.current.storeSession({
        session_token: 'tok123',
        user_id: 'uid1',
        email: 'test@example.com',
        role: 'user',
      })
    })
    act(() => {
      result.current.clearSession()
    })
    expect(result.current.sessionToken).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })
})

// --- Route guards ---

function MockUserPanel() {
  return <div data-testid="user-panel">User Panel</div>
}

function MockAdminPanel() {
  return <div data-testid="admin-panel">Admin Panel</div>
}

function MockLogin() {
  return <div data-testid="login-page-redirect">Login</div>
}

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (role !== 'admin') return <Navigate to="/user" replace />
  return <>{children}</>
}

describe('Route guards', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  test('unauthenticated user cannot access /user and is redirected to /login', () => {
    render(
      <MemoryRouter initialEntries={['/user']}>
        <Routes>
          <Route path="/login" element={<MockLogin />} />
          <Route
            path="/user"
            element={
              <RequireAuth>
                <MockUserPanel />
              </RequireAuth>
            }
          />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByTestId('login-page-redirect')).toBeInTheDocument()
    expect(screen.queryByTestId('user-panel')).not.toBeInTheDocument()
  })

  test('unauthenticated user cannot access /admin and is redirected to /login', () => {
    render(
      <MemoryRouter initialEntries={['/admin']}>
        <Routes>
          <Route path="/login" element={<MockLogin />} />
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <MockAdminPanel />
              </RequireAdmin>
            }
          />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByTestId('login-page-redirect')).toBeInTheDocument()
    expect(screen.queryByTestId('admin-panel')).not.toBeInTheDocument()
  })
})
