import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

// Mock the hooks
vi.mock('../hooks/useAdminUsers', () => ({
  useAdminUsers: () => ({
    users: [
      {
        user_id: 'u1',
        email: 'user@test.com',
        role: 'user',
        is_active: true,
        last_login_at: null,
        license_status: 'active',
        trading_enabled: true,
      },
    ],
    summary: {
      online_user_count: 1,
      total_user_count: 1,
      active_bot_count: 0,
      open_position_count: 0,
      closed_position_count: 0,
      blocked_trade_count: 0,
      alert_count: 0,
    },
    loading: false,
    error: null,
    fetchUsers: vi.fn(),
    getEntitlement: vi.fn(),
    updateEntitlement: vi.fn(),
  }),
}));

// Mock sessionStorage (useAuth stores token in sessionStorage with key polypro_session_token)
beforeEach(() => {
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => {
    if (key === 'polypro_session_token') return 'test-token';
    return null;
  });
});

describe('AdminPanel v1.0.7', () => {
  it('renders admin panel heading', async () => {
    const { default: AdminPanel } = await import('../routes/AdminPanel');
    render(
      <MemoryRouter>
        <AdminPanel />
      </MemoryRouter>
    );
    expect(screen.getByText('Admin Control Panel')).toBeDefined();
  });

  it('shows summary cards', async () => {
    const { default: AdminPanel } = await import('../routes/AdminPanel');
    render(
      <MemoryRouter>
        <AdminPanel />
      </MemoryRouter>
    );
    expect(screen.getByText('Online Users')).toBeDefined();
    expect(screen.getByText('Total Users')).toBeDefined();
  });

  it('shows user in table', async () => {
    const { default: AdminPanel } = await import('../routes/AdminPanel');
    render(
      <MemoryRouter>
        <AdminPanel />
      </MemoryRouter>
    );
    expect(screen.getByText('user@test.com')).toBeDefined();
  });

  it('shows not authenticated when no session token', async () => {
    vi.spyOn(Storage.prototype, 'getItem').mockReturnValue(null);
    const { default: AdminPanel } = await import('../routes/AdminPanel');
    render(
      <MemoryRouter>
        <AdminPanel />
      </MemoryRouter>
    );
    expect(screen.getByText(/Not authenticated/)).toBeDefined();
  });
});

describe('AdminSummaryCards', () => {
  it('renders all metric labels', async () => {
    const { AdminSummaryCards } = await import('../components/admin/AdminSummaryCards');
    const summary = {
      online_user_count: 3,
      total_user_count: 10,
      active_bot_count: 2,
      open_position_count: 5,
      closed_position_count: 20,
      blocked_trade_count: 1,
      alert_count: 0,
    };
    render(<AdminSummaryCards summary={summary} />);
    expect(screen.getByText('Online Users')).toBeDefined();
    expect(screen.getByText('3')).toBeDefined();
  });
});
