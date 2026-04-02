import { NavLink, Outlet } from 'react-router-dom'
import HealthBadge from './HealthBadge'

const nav = [
  { to: '/', label: 'Home', end: true },
  { to: '/user', label: 'User' },
  { to: '/admin', label: 'Admin' },
]

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-[#0f1117]">
      <header className="border-b border-white/10 px-6 py-3 flex items-center justify-between">
        <span className="font-semibold tracking-wide text-white text-sm">POLYPRO</span>
        <nav className="flex gap-1">
          {nav.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded text-sm transition-colors ${
                  isActive
                    ? 'bg-white/10 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <HealthBadge />
      </header>
      <main className="flex-1 p-6">
        <Outlet />
      </main>
    </div>
  )
}
