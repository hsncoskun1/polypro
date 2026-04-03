/** BlockedReasonList — shows Turkish blocked reason messages — v0.8.7 */

interface Props {
  messages: string[]
}

export default function BlockedReasonList({ messages }: Props) {
  if (messages.length === 0) return null

  return (
    <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3">
      <p className="text-xs font-semibold text-red-400 mb-2 uppercase tracking-wide">
        Engel Nedenleri
      </p>
      <ul className="space-y-1">
        {messages.map((msg, i) => (
          <li key={i} className="text-sm text-red-300 flex items-start gap-2">
            <span className="mt-0.5 shrink-0">•</span>
            <span>{msg}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
