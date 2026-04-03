import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from '../components/Layout'
import Launcher from '../routes/Launcher'
import UserPanel from '../routes/UserPanel'
import AdminPanel from '../routes/AdminPanel'
import Settings from '../routes/Settings'
import NotFound from '../routes/NotFound'

export default function Router() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Launcher />} />
          <Route path="/user" element={<UserPanel />} />
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
