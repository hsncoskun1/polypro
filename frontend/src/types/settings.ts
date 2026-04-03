/** SettingsState — TypeScript types for GET /settings — v0.9.0 */

export interface SettingsState {
  // Credential configured status (no plaintext values)
  api_key_configured: boolean
  api_secret_configured: boolean
  api_passphrase_configured: boolean
  relayer_api_configured: boolean
  wallet_address_configured: boolean
  funder_address_configured: boolean
  private_key_configured: boolean

  // Live configuration
  explicit_live_enable: boolean
  live_test_gate_enabled: boolean
  live_test_gate_passed: boolean

  // Trading configuration
  client_mode: string
  minimum_order_size: number
  selected_event: string
  selected_market: string

  // Release gate
  release_ready: boolean
  live_applied_testing_ready: boolean
  blocked_reason_messages: string[]

  // Masked secret fields list
  masked_secret_fields: string[]
}
