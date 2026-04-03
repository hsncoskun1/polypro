import { useNavigate } from 'react-router-dom'
import { useReadiness } from '../hooks/useReadiness'
import ReadinessCard from '../components/ReadinessCard'
import BlockedReasonList from '../components/BlockedReasonList'
import ReleaseGatePanel from '../components/ReleaseGatePanel'
import PortInfo from '../components/PortInfo'

const READINESS_ROWS: Array<{ key: keyof import('../types/readiness').ReadinessState; label: string; informational?: boolean }> = [
  { key: 'backend_ready',              label: 'Backend Hazırlık' },
  { key: 'setup_completed',            label: 'Kurulum Tamamlandı' },
  { key: 'update_required',            label: 'Güncelleme Gerekli', informational: true },
  { key: 'preflight_passed',           label: 'Ön Kontrol (Preflight)' },
  { key: 'final_backend_ready',        label: 'Backend Final Doğrulama' },
]

export default function Launcher() {
  const navigate = useNavigate()
  const { state, status, refresh } = useReadiness()

  const isLoading  = status === 'loading'
  const isError    = status === 'error'
  const isBlocked  = state?.launcher_blocked ?? true

  function handleContinue() {
    if (state?.continue_destination) {
      navigate(state.continue_destination)
    }
  }

  return (
    <div className="max-w-lg mx-auto space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-white">POLYPRO Başlatıcı</h1>
        <p className="text-slate-400 text-sm mt-1">
          Sistem hazırlık durumu ve giriş noktası.
        </p>
      </div>

      {/* Backend unreachable */}
      {isError && (
        <div className="rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 flex items-center justify-between">
          <span className="text-sm text-red-300">Backend'e ulaşılamıyor.</span>
          <button
            onClick={refresh}
            className="text-xs text-red-400 hover:text-red-200 underline"
          >
            Yenile
          </button>
        </div>
      )}

      {/* Loading skeleton */}
      {isLoading && (
        <div className="space-y-2">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-10 rounded-lg bg-white/5 animate-pulse" />
          ))}
        </div>
      )}

      {/* Readiness cards */}
      {state && (
        <>
          <div className="space-y-2">
            {READINESS_ROWS.map(({ key, label, informational }) => {
              const raw = state[key]
              // update_required: inverted — false means OK
              const value =
                key === 'update_required' ? !(raw as boolean) : (raw as boolean)
              return (
                <ReadinessCard
                  key={key}
                  label={label}
                  value={value}
                  informational={informational}
                />
              )
            })}
          </div>

          {/* Release / live gate */}
          <ReleaseGatePanel
            releaseReady={state.release_ready}
            liveAppliedTestingReady={state.live_applied_testing_ready}
          />

          {/* Blocked reasons */}
          <BlockedReasonList messages={state.blocked_reason_messages} />

          {/* Continue / blocked CTA */}
          {isBlocked ? (
            <div className="rounded-lg border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-400">
              Başlatıcı kilitli — canlı test kapısı yetkilendirilmeden uygulamaya erişilemez.
            </div>
          ) : (
            <button
              onClick={handleContinue}
              className="w-full py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition-colors"
            >
              Uygulamaya Devam Et →
            </button>
          )}

          {/* Port info */}
          <PortInfo
            frontendPort={state.frontend_port}
            backendPort={state.backend_port}
          />
        </>
      )}
    </div>
  )
}
