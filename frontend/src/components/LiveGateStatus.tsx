/** LiveGateStatus — release_ready / live_applied_testing_ready / blocked state — v0.8.8 */

interface Props {
  releaseReady: boolean
  liveAppliedTestingReady: boolean
  liveBlocked: boolean
  blockedReasons: string[]
}

export default function LiveGateStatus({
  releaseReady,
  liveAppliedTestingReady,
  liveBlocked,
  blockedReasons,
}: Props) {
  return (
    <div className="rounded-lg border border-white/10 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
        Canlı Mod Durumu
      </p>

      <div className="flex items-center justify-between">
        <span className="text-sm text-slate-300">Yayın Hazırlığı</span>
        <span className={`text-xs font-medium flex items-center gap-1.5 ${releaseReady ? 'text-emerald-400' : 'text-slate-400'}`}>
          <span className={`w-2 h-2 rounded-full ${releaseReady ? 'bg-emerald-500' : 'bg-slate-500'}`} />
          {releaseReady ? 'Hazır' : 'Hazır Değil'}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <span className="text-sm text-slate-300">Canlı Test Kapısı</span>
          <p className="text-xs text-slate-500 mt-0.5">Manuel yetkilendirme gerektirir</p>
        </div>
        <span className={`text-xs font-medium flex items-center gap-1.5 ${liveAppliedTestingReady ? 'text-emerald-400' : 'text-slate-400'}`}>
          <span className={`w-2 h-2 rounded-full ${liveAppliedTestingReady ? 'bg-emerald-500' : 'bg-slate-500'}`} />
          {liveAppliedTestingReady ? 'Açık' : 'Kapalı'}
        </span>
      </div>

      {liveBlocked && blockedReasons.length > 0 && (
        <div className="border-t border-white/8 pt-2 space-y-1">
          {blockedReasons.map((msg, i) => (
            <p key={i} className="text-xs text-slate-500 flex items-start gap-1.5">
              <span className="shrink-0 mt-0.5">•</span>
              <span>{msg}</span>
            </p>
          ))}
        </div>
      )}
    </div>
  )
}
