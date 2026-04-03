/** ReadinessCard — displays a single readiness field as a status row — v0.8.7 */

interface Props {
  label: string
  value: boolean | null
  /** If true, row is styled as secondary/informational rather than pass/fail */
  informational?: boolean
}

export default function ReadinessCard({ label, value, informational = false }: Props) {
  const isLoading = value === null

  const dotClass = isLoading
    ? 'bg-yellow-500 animate-pulse'
    : value
      ? 'bg-emerald-500'
      : informational
        ? 'bg-slate-500'
        : 'bg-red-500'

  const textClass = isLoading
    ? 'text-slate-400'
    : value
      ? 'text-emerald-400'
      : informational
        ? 'text-slate-400'
        : 'text-red-400'

  const statusText = isLoading ? '…' : value ? 'Hazır' : 'Hazır Değil'

  return (
    <div className="flex items-center justify-between px-4 py-2.5 rounded-lg bg-white/5 border border-white/8">
      <span className="text-sm text-slate-300">{label}</span>
      <span className={`flex items-center gap-1.5 text-xs font-medium ${textClass}`}>
        <span className={`w-2 h-2 rounded-full ${dotClass}`} />
        {statusText}
      </span>
    </div>
  )
}
