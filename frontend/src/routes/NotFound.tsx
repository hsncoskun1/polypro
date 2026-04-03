/** NotFound — 404 fallback route — v0.9.1 */
import { Link } from 'react-router-dom'

export default function NotFound() {
  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-semibold text-white mb-2">Sayfa Bulunamadı</h1>
      <p className="text-slate-400 text-sm mb-6">
        İstediğiniz sayfa mevcut değil veya taşınmış olabilir.
      </p>
      <div className="flex gap-3 flex-wrap">
        <Link
          to="/"
          className="px-4 py-2 bg-white/10 text-white text-sm rounded hover:bg-white/15 transition-colors"
        >
          Başlatıcıya Dön
        </Link>
        <Link
          to="/user"
          className="px-4 py-2 text-slate-400 text-sm rounded hover:text-white hover:bg-white/5 transition-colors"
        >
          Kullanıcı Paneli
        </Link>
        <Link
          to="/admin"
          className="px-4 py-2 text-slate-400 text-sm rounded hover:text-white hover:bg-white/5 transition-colors"
        >
          Admin Panel
        </Link>
        <Link
          to="/settings"
          className="px-4 py-2 text-slate-400 text-sm rounded hover:text-white hover:bg-white/5 transition-colors"
        >
          Ayarlar
        </Link>
      </div>
    </div>
  )
}
