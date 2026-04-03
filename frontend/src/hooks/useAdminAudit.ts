/**
 * useAdminAudit — fetch policy audit trail for a user — v1.1.2
 */
import { useState, useEffect } from 'react'

export interface PolicyAuditRecord {
  audit_id: string
  actor_id: string
  target_user_id: string
  action: string
  snapshot_before: Record<string, unknown>
  snapshot_after: Record<string, unknown>
  changed_at: string
  changed_fields: string[]
}

export function useAdminAudit(sessionToken: string | null, userId: string | null) {
  const [records, setRecords] = useState<PolicyAuditRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionToken || !userId) {
      setRecords([])
      return
    }
    setLoading(true)
    setError(null)
    fetch(`/api/v1/admin/users/${userId}/audit`, {
      headers: { 'X-Session-Token': sessionToken },
    })
      .then(async (res) => {
        if (!res.ok) throw new Error(`${res.status}`)
        return res.json() as Promise<PolicyAuditRecord[]>
      })
      .then((data) => {
        setRecords(data)
        setLoading(false)
      })
      .catch((err: Error) => {
        setError(err.message)
        setLoading(false)
      })
  }, [sessionToken, userId])

  return { records, loading, error }
}
