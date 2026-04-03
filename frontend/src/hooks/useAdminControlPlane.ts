/** useAdminControlPlane — polls GET /admin/control-plane every 5 s — v0.8.9 */
import { useEffect, useState, useCallback } from 'react'
import type { AdminControlPlaneState } from '../types/adminControlPlane'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000'
const POLL_MS = 5000

export type AdminControlPlaneStatus = 'loading' | 'ready' | 'error'

export interface UseAdminControlPlaneResult {
  state: AdminControlPlaneState | null
  status: AdminControlPlaneStatus
  refresh: () => void
}

export function useAdminControlPlane(): UseAdminControlPlaneResult {
  const [state, setState] = useState<AdminControlPlaneState | null>(null)
  const [status, setStatus] = useState<AdminControlPlaneStatus>('loading')

  const fetchData = useCallback(() => {
    fetch(`${BACKEND_URL}/admin/control-plane`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<AdminControlPlaneState>
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
