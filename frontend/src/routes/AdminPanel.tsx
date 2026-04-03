// Admin Panel — v1.0.7 (real API data)
import React, { useState, useCallback } from 'react';
import { AdminSummaryCards } from '../components/admin/AdminSummaryCards';
import { AdminUserTable } from '../components/admin/AdminUserTable';
import { EntitlementEditor } from '../components/admin/EntitlementEditor';
import { useAdminUsers } from '../hooks/useAdminUsers';
import type { AdminUserSummary, EntitlementResponse, AdminEntitlementUpdateRequest } from '../types/auth';

export default function AdminPanel() {
  // Session token is stored in sessionStorage by useAuth (key: polypro_session_token)
  const sessionToken = sessionStorage.getItem('polypro_session_token');
  const { users, summary, loading, error, fetchUsers, getEntitlement, updateEntitlement } =
    useAdminUsers(sessionToken);

  const [selectedUser, setSelectedUser] = useState<AdminUserSummary | null>(null);
  const [entitlement, setEntitlement] = useState<EntitlementResponse | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [loadingEntitlement, setLoadingEntitlement] = useState(false);

  const handleSelectUser = useCallback(async (user: AdminUserSummary) => {
    setSelectedUser(user);
    setEditorOpen(false);
    setLoadingEntitlement(true);
    const ent = await getEntitlement(user.user_id);
    setEntitlement(ent);
    setLoadingEntitlement(false);
    setEditorOpen(true);
  }, [getEntitlement]);

  const handleSave = useCallback(async (userId: string, data: AdminEntitlementUpdateRequest) => {
    await updateEntitlement(userId, data);
    await fetchUsers();
  }, [updateEntitlement, fetchUsers]);

  if (!sessionToken) {
    return (
      <div className="p-6 text-red-400">
        Not authenticated. Please <a href="/login" className="underline">log in</a>.
      </div>
    );
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-100">Admin Control Panel</h1>
        <button
          onClick={fetchUsers}
          disabled={loading}
          className="text-xs px-3 py-1 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded disabled:opacity-50"
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-900 border border-red-700 rounded text-red-300 text-sm">
          Error: {error}
        </div>
      )}

      {summary && <AdminSummaryCards summary={summary} />}

      <div className="mt-4">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Users</h2>
        {loading && !users.length ? (
          <p className="text-gray-500 text-sm">Loading users...</p>
        ) : (
          <AdminUserTable
            users={users}
            onSelectUser={handleSelectUser}
            selectedUserId={selectedUser?.user_id ?? null}
          />
        )}
      </div>

      {selectedUser && editorOpen && (
        <div className="mt-4">
          <h2 className="text-sm font-semibold text-gray-300 mb-1">
            Editing: <span className="text-gray-100 font-mono">{selectedUser.email}</span>
          </h2>
          {loadingEntitlement ? (
            <p className="text-gray-500 text-sm">Loading entitlement...</p>
          ) : (
            <EntitlementEditor
              userId={selectedUser.user_id}
              entitlement={entitlement}
              onSave={handleSave}
              onClose={() => setEditorOpen(false)}
            />
          )}
        </div>
      )}
    </div>
  );
}
