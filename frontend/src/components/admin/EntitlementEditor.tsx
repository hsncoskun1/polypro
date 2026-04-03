// Entitlement editor for admin — v1.0.7
import React, { useState, useEffect } from 'react';
import type { EntitlementResponse, AdminEntitlementUpdateRequest } from '../../types/auth';

interface Props {
  userId: string;
  entitlement: EntitlementResponse | null;
  onSave: (userId: string, data: AdminEntitlementUpdateRequest) => Promise<void>;
  onClose: () => void;
}

export function EntitlementEditor({ userId, entitlement, onSave, onClose }: Props) {
  const [licenseStatus, setLicenseStatus] = useState('inactive');
  const [expiresAt, setExpiresAt] = useState('');
  const [tradingEnabled, setTradingEnabled] = useState(false);
  const [visiblePanels, setVisiblePanels] = useState('');
  const [visibleRules, setVisibleRules] = useState('');
  const [editableRules, setEditableRules] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (entitlement) {
      setLicenseStatus(entitlement.license_status);
      setExpiresAt(entitlement.expires_at ? entitlement.expires_at.slice(0, 10) : '');
      setTradingEnabled(entitlement.trading_enabled);
      setVisiblePanels(entitlement.visible_panels.join(', '));
      setVisibleRules(entitlement.visible_rules.join(', '));
      setEditableRules(entitlement.editable_rules.join(', '));
    }
  }, [entitlement]);

  const parseList = (val: string) =>
    val.split(',').map(s => s.trim()).filter(Boolean);

  const handleSave = async () => {
    setSaving(true);
    const data: AdminEntitlementUpdateRequest = {
      license_status: licenseStatus,
      expires_at: expiresAt ? `${expiresAt}T00:00:00` : null,
      trading_enabled: tradingEnabled,
      allowed_features: [],
      visible_panels: parseList(visiblePanels),
      visible_rules: parseList(visibleRules),
      editable_rules: parseList(editableRules),
      blocked_reason_messages: [],
    };
    await onSave(userId, data);
    setSaving(false);
    onClose();
  };

  return (
    <div className="bg-gray-800 border border-gray-600 rounded p-4 mt-4">
      <h3 className="text-sm font-semibold text-gray-200 mb-3">Edit Entitlement</h3>
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
            placeholder="e.g. dashboard, positions, pnl"
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
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-4 py-1.5 bg-green-700 hover:bg-green-600 text-white text-sm rounded disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-gray-600 hover:bg-gray-500 text-white text-sm rounded"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
