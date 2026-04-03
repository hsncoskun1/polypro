/**
 * useEntitlement — fetch user entitlement state — v1.0.5
 */
import { useState, useEffect } from 'react'

export interface EntitlementState {
  user_id: string
  license_status: string
  expires_at: string | null
  trading_enabled: boolean
  allowed_features: string[]
  visible_panels: string[]
  visible_rules: string[]
  editable_rules: string[]
  blocked_reason_messages: string[]
}

export function useEntitlement(sessionToken: string | null) {
  const [entitlement, setEntitlement] = useState<EntitlementState | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionToken) {
      setEntitlement(null)
      return
    }
    setLoading(true)
    setError(null)
    fetch('/api/v1/user/entitlement', {
      headers: { 'X-Session-Token': sessionToken },
    })
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text()
          throw new Error(`${res.status}: ${text}`)
        }
        return res.json() as Promise<EntitlementState>
      })
      .then((data) => {
        setEntitlement(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [sessionToken])

  return { entitlement, loading, error }
}
