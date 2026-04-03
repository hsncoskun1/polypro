/** AdminPanel — full admin operational control and reporting UI — v0.8.9 / v0.9.1 */
import { useAdminControlPlane } from '../hooks/useAdminControlPlane'
import PageShell from '../components/PageShell'
import OperationalControlPanel from '../components/OperationalControlPanel'
import AdminFinancialSummary from '../components/AdminFinancialSummary'
import BlockedEventsPanel from '../components/BlockedEventsPanel'
import ExecutionReportPanel from '../components/ExecutionReportPanel'
import AdminReleaseGate from '../components/AdminReleaseGate'

export default function AdminPanel() {
  const { state, status, refresh } = useAdminControlPlane()

  return (
    <PageShell
      title="Admin Panel"
      subtitle="Operasyonel kontrol, finansal raporlama ve sistem durumu."
      status={status}
      onRefresh={refresh}
    >
      {state && (
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
    </PageShell>
  )
}
