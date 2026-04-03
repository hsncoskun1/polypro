/** CredentialStatusPanel — credential configured status (masked) — v0.9.0 */
import type { SettingsState } from '../types/settings'

interface Props {
  state: SettingsState
}

const CREDENTIAL_LABELS: Record<string, string> = {
  api_key_configured: 'API Anahtarı',
  api_secret_configured: 'API Gizli Anahtarı',
  api_passphrase_configured: 'API Parolası',
  relayer_api_configured: 'Aktarıcı API',
  wallet_address_configured: 'Cüzdan Adresi',
  funder_address_configured: 'Finansör Adresi',
  private_key_configured: 'Özel Anahtar',
}

const CREDENTIAL_FIELDS = [
  'api_key_configured',
  'api_secret_configured',
  'api_passphrase_configured',
  'relayer_api_configured',
  'wallet_address_configured',
  'funder_address_configured',
  'private_key_configured',
] as const

type CredentialField = typeof CREDENTIAL_FIELDS[number]

export default function CredentialStatusPanel({ state }: Props) {
  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Kimlik Bilgisi Durumu
      </h2>
      <p className="text-slate-500 text-xs mb-3 italic">
        Değerler güvenlik nedeniyle gösterilmez. Yalnızca yapılandırma durumu görünür.
      </p>
      {CREDENTIAL_FIELDS.map((field) => {
        const configured = state[field as CredentialField]
        return (
          <div
            key={field}
            className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0"
          >
            <span className="text-slate-300 text-sm">{CREDENTIAL_LABELS[field]}</span>
            <span className={`text-sm font-medium ${configured ? 'text-emerald-400' : 'text-slate-500'}`}>
              {configured ? '✓ Yapılandırıldı' : '— Yapılandırılmadı'}
            </span>
          </div>
        )
      })}
    </div>
  )
}
