/** Control plane state shape returned by GET /control-plane — v0.8.8 */

export interface PositionViewData {
  position_id: string
  event_key: string
  side: string
  status: string
  trigger_price: number
  entry_fill_price: number
  current_price: number
  exit_fill_price: number
  trigger_move_value: number
  fill_move_value: number
  current_move_value: number
  realized_pnl: number
  unrealized_pnl: number
  entry_reason: string
  exit_reason: string
  opened_at: string
  closed_at: string | null
}

export interface ControlPlaneState {
  open_positions: PositionViewData[]
  closed_positions: PositionViewData[]
  session_realized_pnl: number
  session_unrealized_pnl: number
  session_total_pnl: number
  total_balance: number
  available_balance: number
  current_balance: number
  session_start_balance: number
  claim_status: string
  claim_available: boolean
  claimed_amount: number
  settlement_completed_at: string | null
  release_ready: boolean
  live_applied_testing_ready: boolean
  live_mode_ui_blocked: boolean
  blocked_reason_messages: string[]
}
