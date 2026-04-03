/**
 * LicenseStatusBanner — displays license state for user — v1.0.5
 */
import React from 'react'
import type { EntitlementState } from '../../hooks/useEntitlement'

interface Props {
  entitlement: EntitlementState | null
  loading?: boolean
}

export default function LicenseStatusBanner({ entitlement, loading }: Props) {
  if (loading) {
    return (
      <div className="license-status-banner license-status-loading">
        Loading license status...
      </div>
    )
  }

  if (!entitlement) {
    return null
  }

  const isActive = entitlement.license_status === 'active' && entitlement.trading_enabled
  const statusLabel = entitlement.license_status.toUpperCase()

  return (
    <div
      className={`license-status-banner license-status-${entitlement.license_status}`}
      data-testid="license-status-banner"
    >
      <span className="license-status-label">License: {statusLabel}</span>
      {entitlement.expires_at && (
        <span className="license-expires">
          {' '}Expires: {new Date(entitlement.expires_at).toLocaleDateString()}
        </span>
      )}
      {!isActive && entitlement.blocked_reason_messages.length > 0 && (
        <span className="license-blocked-reason">
          {' '}&mdash; {entitlement.blocked_reason_messages[0]}
        </span>
      )}
    </div>
  )
}
