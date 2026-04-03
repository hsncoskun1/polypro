import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from '../components/Layout'
import Launcher from '../routes/Launcher'
import UserPanel from '../routes/UserPanel'
import AdminPanel from '../routes/AdminPanel'
import Settings from '../routes/Settings'
import NotFound from '../routes/NotFound'
import Login from '../routes/Login'
import { useAuth } from '../hooks/useAuth'
import type { LoginPayload } from '../hooks/useAuth'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <>{children}</>
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  if (role !== 'admin') {
    return <Navigate to="/user" replace />
  }
  return <>{children}</>
}

export default function Router() {
  const { storeSession } = useAuth()

  function handleLogin(payload: LoginPayload) {
    storeSession(payload)
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login onLogin={handleLogin} />} />
        <Route element={<Layout />}>
          <Route path="/" element={<Launcher />} />
          <Route
            path="/user"
            element={
              <RequireAuth>
                <UserPanel />
              </RequireAuth>
            }
          />
          <Route
            path="/admin"
            element={
              <RequireAdmin>
                <AdminPanel />
              </RequireAdmin>
            }
          />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
