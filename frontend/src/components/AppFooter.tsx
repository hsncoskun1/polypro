/** AppFooter — global port/startup guidance footer — v0.9.1 */

const BACKEND_PORT = 8000
const FRONTEND_PORT = 5173

export default function AppFooter() {
  return (
    <footer className="border-t border-white/10 px-6 py-2 flex items-center justify-between mt-auto">
      <span className="text-slate-600 text-xs">POLYPRO</span>
      <div className="flex gap-4 text-xs text-slate-600">
        <span>
          Frontend{' '}
          <span className="text-slate-500 font-mono">:{FRONTEND_PORT}</span>
        </span>
        <span>
          Backend{' '}
          <span className="text-slate-500 font-mono">:{BACKEND_PORT}</span>
        </span>
        <span className="text-slate-600">
          Başlatma:{' '}
          <span className="text-slate-500 font-mono">uvicorn</span>
          {' · '}
          <span className="text-slate-500 font-mono">vite</span>
        </span>
      </div>
    </footer>
  )
}
