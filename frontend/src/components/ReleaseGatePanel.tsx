/** ReleaseGatePanel — shows release_ready and live_applied_testing_ready separately — v0.8.7 */

interface Props {
  releaseReady: boolean | null
  liveAppliedTestingReady: boolean | null
}

export default function ReleaseGatePanel({ releaseReady, liveAppliedTestingReady }: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-1">
        Yayın ve Canlı Test Kapısı
      </p>

      <GateRow
        label="Yayın Hazırlığı (release_ready)"
        value={releaseReady}
      />
      <GateRow
        label="Canlı Test Kapısı (live_applied_testing_ready)"
        value={liveAppliedTestingReady}
        note="Manuel yetkilendirme gerektirir"
      />
    </div>
  )
}

function GateRow({
  label,
  value,
  note,
}: {
  label: string
  value: boolean | null
  note?: string
}) {
  const isLoading = value === null
  const dotClass = isLoading
    ? 'bg-yellow-500 animate-pulse'
    : value
      ? 'bg-emerald-500'
      : 'bg-slate-500'
  const textClass = isLoading
    ? 'text-slate-500'
    : value
      ? 'text-emerald-400'
      : 'text-slate-400'
  const statusText = isLoading ? '…' : value ? 'Açık' : 'Kapalı'

  return (
    <div className="flex items-center justify-between">
      <div>
        <span className="text-sm text-slate-300">{label}</span>
        {note && <p className="text-xs text-slate-500 mt-0.5">{note}</p>}
      </div>
      <span className={`flex items-center gap-1.5 text-xs font-medium ${textClass}`}>
        <span className={`w-2 h-2 rounded-full ${dotClass}`} />
        {statusText}
      </span>
    </div>
  )
}
