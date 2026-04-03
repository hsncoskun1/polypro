/** Readiness state shape returned by GET /readiness — v0.8.7 */
export interface ReadinessState {
  launcher_blocked: boolean
  setup_completed: boolean
  update_required: boolean
  preflight_passed: boolean
  backend_ready: boolean
  final_backend_ready: boolean
  release_ready: boolean
  live_applied_testing_ready: boolean
  blocked_reason_messages: string[]
  continue_destination: string | null
  frontend_port: number
  backend_port: number
  readiness_poll_interval_ms: number
}
