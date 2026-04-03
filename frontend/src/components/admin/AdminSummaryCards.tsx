// Admin summary metric cards — v1.0.7
import React from 'react';
import type { AdminSummaryResponse } from '../../types/auth';

interface Props {
  summary: AdminSummaryResponse;
}

export function AdminSummaryCards({ summary }: Props) {
  const cards = [
    { label: 'Online Users', value: summary.online_user_count, color: 'text-green-400' },
    { label: 'Total Users', value: summary.total_user_count, color: 'text-blue-400' },
    { label: 'Active Bots', value: summary.active_bot_count, color: 'text-yellow-400' },
    { label: 'Open Positions', value: summary.open_position_count, color: 'text-cyan-400' },
    { label: 'Closed Positions', value: summary.closed_position_count, color: 'text-gray-400' },
    { label: 'Blocked Trades', value: summary.blocked_trade_count, color: 'text-red-400' },
    { label: 'Alerts', value: summary.alert_count, color: 'text-orange-400' },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
      {cards.map((card) => (
        <div key={card.label} className="bg-gray-800 rounded p-3 border border-gray-700">
          <div className={`text-2xl font-bold ${card.color}`}>{card.value}</div>
          <div className="text-xs text-gray-400 mt-1">{card.label}</div>
        </div>
      ))}
    </div>
  );
}
