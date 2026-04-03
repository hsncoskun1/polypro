/**
 * useLauncherStatus — fetch launcher authority state — v1.1.0
 *
 * Fetches GET /api/v1/launcher/status (always open, no auth).
 * Returns launched (bool) and grant_required (bool).
 */
import { useState, useEffect } from 'react'

export interface LauncherStatusState {
  launched: boolean
  grant_required: boolean
}

export type LauncherStatusResult =
  | { status: 'loading'; data: null }
  | { status: 'ready'; data: LauncherStatusState }
  | { status: 'error'; data: null }

export function useLauncherStatus(): LauncherStatusResult {
  const [result, setResult] = useState<LauncherStatusResult>({ status: 'loading', data: null })

  useEffect(() => {
    let cancelled = false
    fetch('/api/v1/launcher/status')
      .then(async (res) => {
        if (!res.ok) throw new Error(`${res.status}`)
        return res.json() as Promise<LauncherStatusState>
      })
      .then((data) => {
        if (!cancelled) setResult({ status: 'ready', data })
      })
      .catch(() => {
        if (!cancelled) setResult({ status: 'error', data: null })
      })
    return () => { cancelled = true }
  }, [])

  return result
}
