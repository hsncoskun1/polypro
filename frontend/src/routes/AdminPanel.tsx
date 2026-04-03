/** AdminPanel — full admin operational control and reporting UI — v0.8.9 */
import { useAdminControlPlane } from '../hooks/useAdminControlPlane'
import OperationalControlPanel from '../components/OperationalControlPanel'
import AdminFinancialSummary from '../components/AdminFinancialSummary'
import BlockedEventsPanel from '../components/BlockedEventsPanel'
import ExecutionReportPanel from '../components/ExecutionReportPanel'
import AdminReleaseGate from '../components/AdminReleaseGate'

export default function AdminPanel() {
  const { state, status, refresh } = useAdminControlPlane()

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-semibold text-white mb-1">Admin Panel</h1>
      <p className="text-slate-400 text-sm mb-4">Operasyonel kontrol, finansal raporlama ve sistem durumu.</p>

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
          {state.global_disable_active && (
            <div className="bg-red-900/60 border border-red-600 rounded px-4 py-2 mb-4">
              <span className="text-red-200 text-sm font-medium">Genel devre dışı aktif — sistem durduruldu.</span>
            </div>
          )}
          {state.safe_stop_active && (
            <div className="bg-orange-900/50 border border-orange-600 rounded px-4 py-2 mb-4">
              <span className="text-orange-200 text-sm font-medium">Güvenli durdurma aktif.</span>
              {state.safe_stop_reason && (
                <span className="text-orange-300 text-xs ml-2">{state.safe_stop_reason}</span>
              )}
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div>
              <OperationalControlPanel state={state} />
              <AdminReleaseGate state={state} />
            </div>
            <div>
              <AdminFinancialSummary state={state} />
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-0">
            <BlockedEventsPanel state={state} />
            <ExecutionReportPanel state={state} />
          </div>
        </>
      )}
    </div>
  )
}
