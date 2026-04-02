"""admin_label_map — Turkish UI label mapping for admin operational + reporting fields."""

ADMIN_TURKISH_LABELS: dict = {
    # Operational control
    "safe_stop_active": "Güvenli Durdurma Aktif",
    "safe_stop_reason": "Güvenli Durdurma Nedeni",
    "scheduler_enabled": "Zamanlayıcı Etkin",
    "global_disable_active": "Genel Devre Dışı Aktif",
    "config_reload_available": "Yapılandırma Yeniden Yükleme Mevcut",
    "config_reset_available": "Yapılandırma Sıfırlama Mevcut",

    # Financial reporting
    "total_balance": "Toplam Bakiye",
    "available_balance": "Kullanılabilir Bakiye",
    "session_start_balance": "Seans Başlangıç Bakiyesi",
    "current_balance": "Güncel Bakiye",
    "realized_pnl": "Gerçekleşen K/Z",
    "unrealized_pnl": "Gerçekleşmemiş K/Z",
    "session_total_pnl": "Seans Toplam K/Z",
    "claim_adjusted_balance_effect": "Talep Düzeltilmiş Bakiye Etkisi",

    # Operational event lists
    "blocked_trades": "Bloke Edilen İşlemler",
    "blocked_rules": "Bloke Edilen Kurallar",
    "blocked_risk_events": "Bloke Edilen Risk Olayları",
    "execution_fill_events": "Gerçekleşme Olayları",
    "claim_events": "Talep Olayları",
    "operational_alerts": "Operasyonel Uyarılar",
}
