/** Settings — settings and live configuration UI — v0.9.0 / v0.9.1 */
import { useSettings } from '../hooks/useSettings'
import PageShell from '../components/PageShell'
import CredentialStatusPanel from '../components/CredentialStatusPanel'
import LiveConfigPanel from '../components/LiveConfigPanel'
import TradingConfigPanel from '../components/TradingConfigPanel'
import SettingsGateStatus from '../components/SettingsGateStatus'

export default function Settings() {
  const { state, status, refresh } = useSettings()

  return (
    <PageShell
      title="Ayarlar"
      subtitle="Kimlik bilgisi durumu, canlı yapılandırma ve işlem ayarları."
      status={status}
      onRefresh={refresh}
    >
      {state && (
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
    </PageShell>
  )
}
