// Admin user list table — v1.0.7
import React from 'react';
import type { AdminUserSummary } from '../../types/auth';

interface Props {
  users: AdminUserSummary[];
  onSelectUser: (user: AdminUserSummary) => void;
  selectedUserId: string | null;
}

export function AdminUserTable({ users, onSelectUser, selectedUserId }: Props) {
  if (users.length === 0) {
    return <p className="text-gray-400 text-sm">No users found.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left border-collapse">
        <thead>
          <tr className="border-b border-gray-700 text-gray-400">
            <th className="py-2 pr-4">Email</th>
            <th className="py-2 pr-4">Role</th>
            <th className="py-2 pr-4">License</th>
            <th className="py-2 pr-4">Trading</th>
            <th className="py-2 pr-4">Active</th>
            <th className="py-2">Last Login</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr
              key={user.user_id}
              onClick={() => onSelectUser(user)}
              className={`border-b border-gray-800 cursor-pointer hover:bg-gray-800 transition-colors ${
                selectedUserId === user.user_id ? 'bg-gray-800' : ''
              }`}
            >
              <td className="py-2 pr-4 font-mono text-xs">{user.email}</td>
              <td className="py-2 pr-4">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  user.role === 'admin' ? 'bg-purple-900 text-purple-300' : 'bg-gray-700 text-gray-300'
                }`}>
                  {user.role}
                </span>
              </td>
              <td className="py-2 pr-4">
                <span className={`px-2 py-0.5 rounded text-xs ${
                  user.license_status === 'active' ? 'bg-green-900 text-green-300' :
                  user.license_status === 'expired' ? 'bg-red-900 text-red-300' :
                  'bg-gray-700 text-gray-400'
                }`}>
                  {user.license_status ?? 'none'}
                </span>
              </td>
              <td className="py-2 pr-4">
                <span className={`text-xs ${user.trading_enabled ? 'text-green-400' : 'text-red-400'}`}>
                  {user.trading_enabled ? '✓ enabled' : '✗ disabled'}
                </span>
              </td>
              <td className="py-2 pr-4">
                <span className={`text-xs ${user.is_active ? 'text-gray-300' : 'text-gray-600'}`}>
                  {user.is_active ? 'yes' : 'no'}
                </span>
              </td>
              <td className="py-2 text-xs text-gray-500">
                {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
