/** useSettings — polls GET /settings every 5 s — v0.9.0 */
import { useEffect, useState, useCallback } from 'react'
import type { SettingsState } from '../types/settings'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000'
const POLL_MS = 5000

export type SettingsStatus = 'loading' | 'ready' | 'error'

export interface UseSettingsResult {
  state: SettingsState | null
  status: SettingsStatus
  refresh: () => void
}

export function useSettings(): UseSettingsResult {
  const [state, setState] = useState<SettingsState | null>(null)
  const [status, setStatus] = useState<SettingsStatus>('loading')

  const fetchData = useCallback(() => {
    fetch(`${BACKEND_URL}/settings`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<SettingsState>
      })
      .then((data) => {
        setState(data)
        setStatus('ready')
      })
      .catch(() => {
        setState(null)
        setStatus('error')
      })
  }, [])

  useEffect(() => {
    fetchData()
    const interval = window.setInterval(fetchData, POLL_MS)
    return () => window.clearInterval(interval)
  }, [fetchData])

  return { state, status, refresh: fetchData }
}
