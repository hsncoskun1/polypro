/** AuditTrailPanel — shows policy audit history for a selected user — v1.1.2 */
import type { PolicyAuditRecord } from '../../hooks/useAdminAudit'

interface Props {
  records: PolicyAuditRecord[]
  loading: boolean
  error: string | null
}

function formatDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString('tr-TR', { timeZone: 'UTC' })
  } catch {
    return iso
  }
}

export function AuditTrailPanel({ records, loading, error }: Props) {
  if (loading) {
    return (
      <div className="mt-4 p-3 text-gray-400 text-sm" data-testid="audit-loading">
        Denetim kayıtları yükleniyor...
      </div>
    )
  }

  if (error) {
    return (
      <div className="mt-4 p-3 bg-red-900 border border-red-700 rounded text-red-300 text-xs" data-testid="audit-error">
        Denetim yüklenemedi: {error}
      </div>
    )
  }

  return (
    <div className="mt-4" data-testid="audit-trail-panel">
      <h3 className="text-sm font-semibold text-gray-300 mb-2">Politika Değişiklik Geçmişi</h3>
      {records.length === 0 ? (
        <p className="text-gray-500 text-xs" data-testid="audit-empty">Kayıt bulunamadı.</p>
      ) : (
        <div className="space-y-2">
          {records.map((r) => (
            <div
              key={r.audit_id}
              className="bg-gray-800 border border-gray-700 rounded p-3 text-xs"
              data-testid={`audit-record-${r.audit_id}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="text-gray-300 font-medium">{r.action}</span>
                <span className="text-gray-500">{formatDate(r.changed_at)}</span>
              </div>
              {r.changed_fields.length > 0 && (
                <div className="text-gray-400 mb-1">
                  Değişen alanlar:{' '}
                  <span className="text-amber-300 font-mono">{r.changed_fields.join(', ')}</span>
                </div>
              )}
              <div className="text-gray-500 font-mono">
                Aktör: {r.actor_id}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
