/** TradingConfigPanel — client mode, min order, event/market selection — v0.9.0 */
import type { SettingsState } from '../types/settings'

interface Props {
  state: SettingsState
}

const CLIENT_MODE_LABELS: Record<string, string> = {
  simulation_mock: 'Simülasyon (Mock)',
  live_mock: 'Canlı Mock',
  live_dry_run: 'Canlı Kuru Çalıştırma',
  live_production: 'Canlı Üretim',
}

function ConfigField({ label, value, emptyLabel }: { label: string; value: string | number; emptyLabel?: string }) {
  const isEmpty = value === '' || value === 0
  return (
    <div className="flex justify-between items-center py-2 border-b border-slate-700 last:border-0">
      <span className="text-slate-300 text-sm">{label}</span>
      <span className={`text-sm font-mono ${isEmpty ? 'text-slate-500 italic' : 'text-slate-200'}`}>
        {isEmpty ? (emptyLabel ?? '—') : String(value)}
      </span>
    </div>
  )
}

export default function TradingConfigPanel({ state }: Props) {
  const clientModeLabel = CLIENT_MODE_LABELS[state.client_mode] ?? state.client_mode

  return (
    <div className="bg-slate-800 rounded p-4 mb-4">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        İşlem Yapılandırması
      </h2>
      <div className="flex justify-between items-center py-2 border-b border-slate-700">
        <span className="text-slate-300 text-sm">İstemci Modu</span>
        <span className="text-sm font-medium text-slate-200">{clientModeLabel}</span>
      </div>
      <ConfigField
        label="Minimum Emir Boyutu"
        value={state.minimum_order_size}
        emptyLabel="Yapılandırılmadı"
      />
      <ConfigField
        label="Seçili Etkinlik"
        value={state.selected_event}
        emptyLabel="Seçilmedi"
      />
      <ConfigField
        label="Seçili Piyasa"
        value={state.selected_market}
        emptyLabel="Seçilmedi"
      />
    </div>
  )
}
