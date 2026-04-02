import { useEffect, useState } from 'react'

type Status = 'ok' | 'error' | 'loading'

export default function HealthBadge() {
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/health')
      .then((r) => (r.ok ? setStatus('ok') : setStatus('error')))
      .catch(() => setStatus('error'))
  }, [])

  const color =
    status === 'ok'
      ? 'bg-emerald-500'
      : status === 'error'
        ? 'bg-red-500'
        : 'bg-yellow-500 animate-pulse'

  const label = status === 'ok' ? 'API' : status === 'error' ? 'API offline' : '…'

  return (
    <span className="flex items-center gap-1.5 text-xs text-slate-400">
      <span className={`w-2 h-2 rounded-full ${color}`} />
      {label}
    </span>
  )
}
