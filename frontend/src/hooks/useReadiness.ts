import { useEffect, useState, useCallback } from 'react'
import type { ReadinessState } from '../types/readiness'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? 'http://127.0.0.1:8000'
const DEFAULT_POLL_MS = 5000

export type ReadinessStatus = 'loading' | 'ready' | 'error'

export interface UseReadinessResult {
  state: ReadinessState | null
  status: ReadinessStatus
  refresh: () => void
}

export function useReadiness(): UseReadinessResult {
  const [state, setState] = useState<ReadinessState | null>(null)
  const [status, setStatus] = useState<ReadinessStatus>('loading')

  const fetch_readiness = useCallback(() => {
    fetch(`${BACKEND_URL}/readiness`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json() as Promise<ReadinessState>
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
    fetch_readiness()
    const interval = window.setInterval(
      fetch_readiness,
      state?.readiness_poll_interval_ms ?? DEFAULT_POLL_MS,
    )
    return () => window.clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fetch_readiness])

  return { state, status, refresh: fetch_readiness }
}
