/** PortInfo — shows frontend/backend ports and startup instructions — v0.8.7 */

interface Props {
  frontendPort: number
  backendPort: number
}

export default function PortInfo({ frontendPort, backendPort }: Props) {
  return (
    <div className="rounded-lg border border-white/8 bg-white/3 px-4 py-3 space-y-2">
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
        Bağlantı Bilgisi
      </p>

      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="flex flex-col gap-0.5">
          <span className="text-slate-500 text-xs">Frontend</span>
          <code className="text-slate-300 font-mono">
            http://localhost:{frontendPort}
          </code>
        </div>
        <div className="flex flex-col gap-0.5">
          <span className="text-slate-500 text-xs">Backend API</span>
          <code className="text-slate-300 font-mono">
            http://localhost:{backendPort}
          </code>
        </div>
      </div>

      <div className="border-t border-white/8 pt-2 mt-1 space-y-1 text-xs text-slate-500">
        <p>
          <span className="text-slate-400 font-medium">Frontend başlatma: </span>
          <code className="font-mono">cd frontend &amp;&amp; npm run dev</code>
        </p>
        <p>
          <span className="text-slate-400 font-medium">Backend başlatma: </span>
          <code className="font-mono">cd backend &amp;&amp; uvicorn app.main:app --reload</code>
        </p>
      </div>
    </div>
  )
}
