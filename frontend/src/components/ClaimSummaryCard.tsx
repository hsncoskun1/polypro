/** ClaimSummaryCard — claim/settlement summary — v0.8.8 */

const STATUS_LABELS: Record<string, string> = {
  not_claimable_outcome_unknown:     'Sonuç Bilinmiyor',
  not_claimable_resolution_pending:  'Çözüm Bekliyor',
  not_claimable_claim_unavailable:   'Talep Kullanılamaz',
  claim_available:                   'Talep Kullanılabilir',
  claim_submitted:                   'Talep Gönderildi',
  claim_completed:                   'Talep Tamamlandı',
  claim_failed:                      'Talep Başarısız',
}

const STATUS_CLASS: Record<string, string> = {
  not_claimable_outcome_unknown:     'text-slate-400',
  not_claimable_resolution_pending:  'text-slate-400',
  not_claimable_claim_unavailable:   'text-slate-400',
  claim_available:                   'text-emerald-400',
  claim_submitted:                   'text-yellow-400',
  claim_completed:                   'text-emerald-400',
  claim_failed:                      'text-red-400',
}

interface Props {
  claimStatus: string
  claimAvailable: boolean
  claimedAmount: number
  settlementCompletedAt: string | null
}

export default function ClaimSummaryCard({
  claimStatus,
  claimAvailable,
  claimedAmount,
  settlementCompletedAt,
}: Props) {
  const label = STATUS_LABELS[claimStatus] ?? claimStatus
  const cls = STATUS_CLASS[claimStatus] ?? 'text-slate-400'

  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
        Talep / Uzlaşma
      </p>
      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-300">Talep Durumu</span>
        <span className={`text-xs font-medium ${cls}`}>{label}</span>
      </div>
      {claimAvailable && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-300">Talep Edilebilir Tutar</span>
          <span className="text-xs text-emerald-400 font-mono">{claimedAmount.toFixed(4)}</span>
        </div>
      )}
      {settlementCompletedAt && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-300">Uzlaşma Tamamlandı</span>
          <span className="text-xs text-slate-400">{settlementCompletedAt}</span>
        </div>
      )}
    </div>
  )
}
