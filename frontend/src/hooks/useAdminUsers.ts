// Admin users API hook — v1.0.7
import { useState, useEffect, useCallback } from 'react';
import type { AdminUserSummary, AdminSummaryResponse, EntitlementResponse, AdminEntitlementUpdateRequest } from '../types/auth';

const BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';

function getHeaders(sessionToken: string) {
  return {
    'Content-Type': 'application/json',
    'X-Session-Token': sessionToken,
  };
}

export function useAdminUsers(sessionToken: string | null) {
  const [users, setUsers] = useState<AdminUserSummary[]>([]);
  const [summary, setSummary] = useState<AdminSummaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    if (!sessionToken) return;
    setLoading(true);
    setError(null);
    try {
      const [usersRes, summaryRes] = await Promise.all([
        fetch(`${BASE_URL}/api/v1/admin/users`, { headers: getHeaders(sessionToken) }),
        fetch(`${BASE_URL}/api/v1/admin/summary`, { headers: getHeaders(sessionToken) }),
      ]);
      if (!usersRes.ok) throw new Error(`Users fetch failed: ${usersRes.status}`);
      if (!summaryRes.ok) throw new Error(`Summary fetch failed: ${summaryRes.status}`);
      const usersData: AdminUserSummary[] = await usersRes.json();
      const summaryData: AdminSummaryResponse = await summaryRes.json();
      setUsers(usersData);
      setSummary(summaryData);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  }, [sessionToken]);

  const getEntitlement = useCallback(async (userId: string): Promise<EntitlementResponse | null> => {
    if (!sessionToken) return null;
    const res = await fetch(`${BASE_URL}/api/v1/admin/users/${userId}/entitlement`, {
      headers: getHeaders(sessionToken),
    });
    if (!res.ok) return null;
    return res.json();
  }, [sessionToken]);

  const updateEntitlement = useCallback(async (
    userId: string,
    data: AdminEntitlementUpdateRequest
  ): Promise<EntitlementResponse | null> => {
    if (!sessionToken) return null;
    const res = await fetch(`${BASE_URL}/api/v1/admin/users/${userId}/entitlement`, {
      method: 'PUT',
      headers: getHeaders(sessionToken),
      body: JSON.stringify(data),
    });
    if (!res.ok) return null;
    return res.json();
  }, [sessionToken]);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  return { users, summary, loading, error, fetchUsers, getEntitlement, updateEntitlement };
}
