/** PageShell — shared loading / error / content wrapper — v0.9.1
 *
 * Provides consistent loading skeleton, error banner, and content slot
 * for all route-level pages. Every page using this gets the same UX pattern.
 */
import type { ReactNode } from 'react'

interface Props {
  title: string
  subtitle?: string
  status: 'loading' | 'ready' | 'error'
  onRefresh?: () => void
  children: ReactNode
}

export default function PageShell({ title, subtitle, status, onRefresh, children }: Props) {
  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-semibold text-white mb-1">{title}</h1>
      {subtitle && <p className="text-slate-400 text-sm mb-4">{subtitle}</p>}

      {status === 'loading' && (
        <div className="space-y-3 mt-4" aria-label="Yükleniyor">
          <div className="h-4 bg-slate-700 rounded animate-pulse w-3/4" />
          <div className="h-4 bg-slate-700 rounded animate-pulse w-1/2" />
          <div className="h-4 bg-slate-700 rounded animate-pulse w-2/3" />
        </div>
      )}

      {status === 'error' && (
        <div className="flex items-center justify-between bg-red-900/40 border border-red-700 rounded px-4 py-2 mb-4">
          <span className="text-red-300 text-sm">Backend&apos;e ulaşılamıyor.</span>
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="text-red-300 text-xs underline ml-4 hover:text-red-200"
            >
              Yenile
            </button>
          )}
        </div>
      )}

      {status === 'ready' && children}
    </div>
  )
}
