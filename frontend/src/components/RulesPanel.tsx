/** RulesPanel — user-facing rule visibility + editability display — v1.1.1
 *
 * Visibility rules:
 *   - If visible_rules is empty → all known rules are shown
 *   - If visible_rules is non-empty → only listed rule keys are shown
 *
 * Editability rules:
 *   - If rule key is in editable_rules → badge shows "Düzenlenebilir"
 *   - Otherwise → badge shows "Salt Okunur"
 */

interface RuleEntry {
  key: string
  label: string
}

const KNOWN_RULES: RuleEntry[] = [
  { key: 'time_rule',          label: 'Zaman Kuralı' },
  { key: 'price_rule',         label: 'Fiyat Kuralı' },
  { key: 'move_rule',          label: 'Hareket Kuralı' },
  { key: 'spread_rule',        label: 'Spread Kuralı' },
  { key: 'event_limit_rule',   label: 'Etkinlik Limiti Kuralı' },
  { key: 'max_positions_rule', label: 'Maksimum Pozisyon Kuralı' },
]

interface Props {
  visibleRules: string[]
  editableRules: string[]
}

function isRuleVisible(key: string, visibleRules: string[]): boolean {
  if (visibleRules.length === 0) return true
  return visibleRules.includes(key)
}

function isRuleEditable(key: string, editableRules: string[]): boolean {
  return editableRules.includes(key)
}

export default function RulesPanel({ visibleRules, editableRules }: Props) {
  const visibleEntries = KNOWN_RULES.filter(r => isRuleVisible(r.key, visibleRules))

  if (visibleEntries.length === 0) return null

  return (
    <div className="bg-slate-800 rounded p-4" data-testid="rules-panel">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
        Strateji Kuralları
      </h2>
      <div className="space-y-2">
        {visibleEntries.map(({ key, label }) => {
          const editable = isRuleEditable(key, editableRules)
          return (
            <div
              key={key}
              className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0"
              data-testid={`rule-row-${key}`}
            >
              <span className="text-sm text-slate-300">{label}</span>
              <span
                className={`text-xs px-2 py-0.5 rounded font-medium ${
                  editable
                    ? 'bg-emerald-900/50 text-emerald-300 border border-emerald-700/40'
                    : 'bg-slate-700 text-slate-400 border border-slate-600'
                }`}
                data-testid={editable ? `rule-editable-${key}` : `rule-readonly-${key}`}
              >
                {editable ? 'Düzenlenebilir' : 'Salt Okunur'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
