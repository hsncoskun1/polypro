/** AdminControlPlaneState — TypeScript types for GET /admin/control-plane — v0.8.9 */

export interface AdminControlPlaneState {
  // Operational control
  safe_stop_active: boolean
  safe_stop_reason: string
  scheduler_enabled: boolean
  global_disable_active: boolean
  config_reload_available: boolean
  config_reset_available: boolean

  // Financial reporting
  total_balance: number
  available_balance: number
  current_balance: number
  session_start_balance: number
  realized_pnl: number
  unrealized_pnl: number
  session_total_pnl: number
  claim_adjusted_balance_effect: number

  // Operational event lists
  blocked_trades: string[]
  blocked_rules: string[]
  blocked_risk_events: string[]
  execution_fill_events: string[]
  claim_events: string[]
  operational_alerts: string[]

  // Release gate
  release_ready: boolean
  live_applied_testing_ready: boolean
}
