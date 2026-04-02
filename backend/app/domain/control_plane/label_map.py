"""label_map — Turkish UI label mapping for simulation control plane fields."""

TURKISH_LABELS: dict = {
    # Position lists
    "open_positions": "Açık Pozisyonlar",
    "closed_positions": "Kapalı Pozisyonlar",

    # Price fields
    "trigger_price": "Tetik Fiyatı",
    "entry_fill_price": "Giriş Gerçekleşme Fiyatı",
    "current_price": "Güncel Fiyat",
    "exit_fill_price": "Çıkış Gerçekleşme Fiyatı",

    # Move values
    "trigger_move_value": "Tetik Hareket Değeri",
    "fill_move_value": "Gerçekleşme Hareket Değeri",
    "current_move_value": "Güncel Hareket Değeri",

    # PnL
    "realized_pnl": "Gerçekleşen K/Z",
    "unrealized_pnl": "Gerçekleşmemiş K/Z",
    "session_realized_pnl": "Seans Gerçekleşen K/Z",
    "session_unrealized_pnl": "Seans Gerçekleşmemiş K/Z",
    "session_total_pnl": "Seans Toplam K/Z",

    # Balance
    "total_balance": "Toplam Bakiye",
    "available_balance": "Kullanılabilir Bakiye",
    "current_balance": "Güncel Bakiye",
    "session_start_balance": "Seans Başlangıç Bakiyesi",

    # Claim / settlement
    "claim_status": "Talep Durumu",
    "claim_available": "Talep Kullanılabilir",
    "claimed_amount": "Talep Edilen Tutar",
    "settlement_completed_at": "Uzlaşma Tamamlanma Zamanı",

    # Position metadata
    "side": "Taraf",
    "status": "Durum",
    "event_key": "Etkinlik",
    "entry_reason": "Giriş Nedeni",
    "exit_reason": "Çıkış Nedeni",
    "opened_at": "Açılış Zamanı",
    "closed_at": "Kapanış Zamanı",
    "position_id": "Pozisyon ID",
}
