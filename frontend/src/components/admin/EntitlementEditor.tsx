// Entitlement editor for admin — v1.0.9
import React, { useState, useEffect } from 'react';
import type { EntitlementResponse, AdminEntitlementUpdateRequest } from '../../types/auth';

interface Props {
  userId: string;
  entitlement: EntitlementResponse | null;
  onSave: (userId: string, data: AdminEntitlementUpdateRequest) => Promise<{ ok: boolean; error?: string }>;
  onClose: () => void;
}

export function EntitlementEditor({ userId, entitlement, onSave, onClose }: Props) {
  const [licenseStatus, setLicenseStatus] = useState('inactive');
  const [expiresAt, setExpiresAt] = useState('');
  const [tradingEnabled, setTradingEnabled] = useState(false);
  const [visiblePanels, setVisiblePanels] = useState('');
  const [visibleRules, setVisibleRules] = useState('');
  const [editableRules, setEditableRules] = useState('');
  const [blockedReasons, setBlockedReasons] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const loadFromEntitlement = (ent: EntitlementResponse) => {
    setLicenseStatus(ent.license_status);
    setExpiresAt(ent.expires_at ? ent.expires_at.slice(0, 10) : '');
    setTradingEnabled(ent.trading_enabled);
    setVisiblePanels(ent.visible_panels.join(', '));
    setVisibleRules(ent.visible_rules.join(', '));
    setEditableRules(ent.editable_rules.join(', '));
    setBlockedReasons(ent.blocked_reason_messages.join('\n'));
  };

  useEffect(() => {
    if (entitlement) {
      loadFromEntitlement(entitlement);
    }
  }, [entitlement]);

  const parseList = (val: string) =>
    val.split(',').map(s => s.trim()).filter(Boolean);

  const parseLines = (val: string) =>
    val.split('\n').map(s => s.trim()).filter(Boolean);

  const handleSave = async () => {
    setSaving(true);
    setSaveError(null);
    const data: AdminEntitlementUpdateRequest = {
      license_status: licenseStatus,
      expires_at: expiresAt ? `${expiresAt}T00:00:00` : null,
      trading_enabled: tradingEnabled,
      allowed_features: [],
      visible_panels: parseList(visiblePanels),
      visible_rules: parseList(visibleRules),
      editable_rules: parseList(editableRules),
      blocked_reason_messages: parseLines(blockedReasons),
    };
    const result = await onSave(userId, data);
    setSaving(false);
    if (result.ok) {
      onClose();
    } else {
      setSaveError(result.error ?? 'Save failed. Please try again.');
    }
  };

  const handleCancel = () => {
    if (entitlement) {
      loadFromEntitlement(entitlement);
    }
    setSaveError(null);
    onClose();
  };

  return (
    <div className="bg-gray-800 border border-gray-600 rounded p-4 mt-4">
      <h3 className="text-sm font-semibold text-gray-200 mb-3">Edit Entitlement</h3>

      {saveError && (
        <div className="mb-3 p-2 bg-red-900 border border-red-700 rounded text-red-300 text-xs" data-testid="save-error">
          {saveError}
        </div>
      )}

      <div className="grid grid-cols-1 gap-3">
        <div>
          <label className="text-xs text-gray-400">License Status</label>
          <select
            value={licenseStatus}
            onChange={e => setLicenseStatus(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1"
          >
            <option value="active">active</option>
            <option value="expired">expired</option>
            <option value="inactive">inactive</option>
          </select>
        </div>
        <div>
          <label className="text-xs text-gray-400">Expires At (YYYY-MM-DD)</label>
          <input
            type="date"
            value={expiresAt}
            onChange={e => setExpiresAt(e.target.value)}
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1"
          />
        </div>
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="tradingEnabled"
            checked={tradingEnabled}
            onChange={e => setTradingEnabled(e.target.checked)}
            className="accent-green-500"
          />
          <label htmlFor="tradingEnabled" className="text-xs text-gray-300">Trading Enabled</label>
        </div>
        <div>
          <label className="text-xs text-gray-400">Visible Panels (comma-separated)</label>
          <input
            type="text"
            value={visiblePanels}
            onChange={e => setVisiblePanels(e.target.value)}
            placeholder="e.g. positions, pnl, balance, claims, live_gate"
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400">Visible Rules (comma-separated)</label>
          <input
            type="text"
            value={visibleRules}
            onChange={e => setVisibleRules(e.target.value)}
            placeholder="e.g. rule_a, rule_b"
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400">Editable Rules (comma-separated)</label>
          <input
            type="text"
            value={editableRules}
            onChange={e => setEditableRules(e.target.value)}
            placeholder="e.g. rule_a"
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1"
          />
        </div>
        <div>
          <label className="text-xs text-gray-400">Blocked Reason Messages (one per line)</label>
          <textarea
            value={blockedReasons}
            onChange={e => setBlockedReasons(e.target.value)}
            placeholder="e.g. License expired. Contact support."
            rows={3}
            className="w-full bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 mt-1 resize-y"
          />
        </div>
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-1.5 bg-green-700 hover:bg-green-600 text-white text-sm rounded disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button
            onClick={handleCancel}
            disabled={saving}
            className="px-4 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded disabled:opacity-50"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
