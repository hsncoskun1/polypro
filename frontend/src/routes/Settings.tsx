/** Settings — settings and live configuration UI — v0.9.0 */
import { useSettings } from '../hooks/useSettings'
import CredentialStatusPanel from '../components/CredentialStatusPanel'
import LiveConfigPanel from '../components/LiveConfigPanel'
import TradingConfigPanel from '../components/TradingConfigPanel'
import SettingsGateStatus from '../components/SettingsGateStatus'

export default function Settings() {
  const { state, status, refresh } = useSettings()

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-semibold text-white mb-1">Ayarlar</h1>
      <p className="text-slate-400 text-sm mb-4">Kimlik bilgisi durumu, canlı yapılandırma ve işlem ayarları.</p>

      {status === 'loading' && (
        <p className="text-slate-400 text-sm">Yükleniyor...</p>
      )}

      {status === 'error' && (
        <div className="flex items-center justify-between bg-red-900/40 border border-red-700 rounded px-4 py-2 mb-4">
          <span className="text-red-300 text-sm">Backend&apos;e ulaşılamıyor.</span>
          <button
            onClick={refresh}
            className="text-red-300 text-xs underline ml-4 hover:text-red-200"
          >
            Yenile
          </button>
        </div>
      )}

      {status === 'ready' && state && (
        <>
          {state.masked_secret_fields.length === 0 && (
            <div className="bg-yellow-900/40 border border-yellow-700 rounded px-4 py-2 mb-4">
              <span className="text-yellow-200 text-sm">Hiçbir kimlik bilgisi yapılandırılmamış. Canlı mod için kimlik bilgileri gereklidir.</span>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <CredentialStatusPanel state={state} />
              <LiveConfigPanel state={state} />
            </div>
            <div>
              <TradingConfigPanel state={state} />
              <SettingsGateStatus state={state} />
            </div>
          </div>
        </>
      )}
    </div>
  )
}
