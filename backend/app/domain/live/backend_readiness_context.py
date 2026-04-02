"""Backend readiness context — v0.8.2.

Carries the state of every critical link in the live backend chain.
Used by BackendReadinessEvaluator to determine whether the backend is
fully assembled and ready for live execution.

No network calls. No side effects. Pure state model.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class BackendReadinessContext:
    """State snapshot of the end-to-end live backend chain.

    Each boolean field represents one critical link. If any link is
    False the backend is not ready and a blocker reason is emitted.

    Attributes:
        live_mode_requested: Live mode has been explicitly requested.
        explicit_live_enable: Live mode has been explicitly enabled via config.
        credentials_complete: All required exchange credentials are present.
        preflight_passed: Preflight checks passed (v0.7.2 guard chain).
        outbound_allowed: Outbound execution flag is enabled (v0.7.2).
        client_mode: Active ClientMode string label.
        production_wiring_ready: Production client wiring is complete (v0.7.9).
        adapter_available: A LiveExchangeClient adapter is resolved (v0.7.8).
        concrete_client_available: ProductionExchangeClient instance present (v0.8.0).
        submission_ready: Order submission seam is ready (v0.7.3).
        response_classification_ready: Response/fill confirmation chain ready (v0.7.4).
        cancel_replace_ready: Cancel/replace seam chain ready (v0.7.5).
        reconciliation_ready: Order event reconciliation ready (v0.7.6).
        orchestrator_ready: Live execution orchestrator ready (v0.7.7).
    """
    live_mode_requested: bool = False
    explicit_live_enable: bool = False
    credentials_complete: bool = False
    preflight_passed: bool = False
    outbound_allowed: bool = False
    client_mode: str = ""
    production_wiring_ready: bool = False
    adapter_available: bool = False
    concrete_client_available: bool = False
    submission_ready: bool = False
    response_classification_ready: bool = False
    cancel_replace_ready: bool = False
    reconciliation_ready: bool = False
    orchestrator_ready: bool = False
