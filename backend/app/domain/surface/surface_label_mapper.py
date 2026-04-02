"""Surface label mapper — v0.8.5.

Turkish label mappings for user and admin surfaces.
Internal enum/code/reason_code values remain in English;
only the display labels shown on the UI are translated.

Secrets and credential field names are excluded from all mappings.
"""
from typing import Dict, List

# ---------------------------------------------------------------------------
# User surface labels (Turkish)
# ---------------------------------------------------------------------------

USER_SURFACE_LABELS_TR: Dict[str, str] = {
    "open_positions": "Açık Pozisyonlar",
    "closed_positions": "Kapalı Pozisyonlar",
    "balance_summary": "Bakiye Özeti",
    "pnl_summary": "Kar/Zarar Özeti",
    "claim_summary": "Hak Talebi Özeti",
    "release_status": "Yayın Hazırlık Durumu",
    "live_gate_status": "Canlı Test Kapısı",
    "launcher_status": "Başlatıcı Durumu",
    "live_mode": "Canlı Mod",
    "simulation_mode": "Simülasyon Modu",
}

# ---------------------------------------------------------------------------
# Admin surface labels (Turkish) — superset of user labels
# ---------------------------------------------------------------------------

ADMIN_SURFACE_LABELS_TR: Dict[str, str] = {
    **USER_SURFACE_LABELS_TR,
    "safe_stop": "Güvenli Durdurma",
    "scheduler": "Zamanlayıcı",
    "global_disable": "Genel Devre Dışı",
    "blocked_trades": "Engellenen İşlemler",
    "blocked_rules": "Engellenen Kurallar",
    "blocked_risk_events": "Engellenen Risk Olayları",
    "execution_fills": "Gerçekleşen İşlemler",
    "claim_events": "Hak Talebi Olayları",
    "operational_alerts": "Operasyonel Uyarılar",
    "backend_readiness": "Backend Hazırlık",
    "release_readiness": "Yayın Hazırlığı",
    "live_test_gate": "Canlı Test Kapısı (Teknik)",
    "admin_report": "Yönetici Raporu",
}

# ---------------------------------------------------------------------------
# Blocked reason messages (Turkish)
# ---------------------------------------------------------------------------

BLOCKED_REASON_MESSAGES_TR: Dict[str, str] = {
    "launcher_blocked": "Başlatıcı hazır değil — uygulama kullanılamaz.",
    "backend_not_ready": "Backend hazır değil.",
    "release_not_ready": "Yayın hazırlığı tamamlanmadı.",
    "live_gate_not_passed": "Canlı test kapısı geçilmedi.",
    "live_mode_not_authorized": "Canlı mod henüz yetkilendirilmedi.",
    "final_backend_not_ready": "Backend final doğrulaması tamamlanmadı.",
    "credentials_incomplete": "Kimlik bilgileri eksik.",
    "preflight_not_ready": "Uçuş öncesi kontrol başarısız.",
    "outbound_guard_not_ready": "Giden işlem güvenlik kapısı hazır değil.",
}

# ---------------------------------------------------------------------------
# Visible panels per role
# ---------------------------------------------------------------------------

USER_VISIBLE_PANELS: List[str] = [
    "open_positions",
    "closed_positions",
    "balance_summary",
    "pnl_summary",
    "claim_summary",
    "release_status",
    "live_gate_status",
]

ADMIN_VISIBLE_PANELS: List[str] = USER_VISIBLE_PANELS + [
    "safe_stop",
    "scheduler",
    "global_disable",
    "blocked_trades",
    "blocked_rules",
    "blocked_risk_events",
    "execution_fills",
    "claim_events",
    "operational_alerts",
    "backend_readiness",
    "release_readiness",
    "live_test_gate",
    "admin_report",
]


def get_blocked_reason_message_tr(reason_code: str) -> str:
    """Return a Turkish display message for a given blocker reason code.

    Returns a generic fallback if the code is not in the map.
    """
    return BLOCKED_REASON_MESSAGES_TR.get(
        reason_code,
        f"Bilinmeyen engel: {reason_code}",
    )
