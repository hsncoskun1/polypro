/** useControlPlane — polls GET /control-plane every 5 s — v0.8.8 */
import { useEffect, useState, useCallback } from 'react'
import type { ControlPlaneState } from '../types/controlPlane'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000'
const POLL_MS = 5000

export type ControlPlaneStatus = 'loading' | 'ready' | 'error'

export interface UseControlPlaneResult {
  state: ControlPlaneState | null
  status: ControlPlaneStatus
  refresh: () => void
}

export function useControlPlane(): UseControlPlaneResult {
  const [state, setState] = useState<ControlPlaneState | null>(null)
  const [status, setStatus] = useState<ControlPlaneStatus>('loading')

  const fetchData = useCallback(() => {
    fetch(`${BACKEND_URL}/control-plane`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<ControlPlaneState>
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
