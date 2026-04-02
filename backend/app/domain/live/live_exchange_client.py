"""Live exchange client adapter interface — v0.7.8.

Abstract base class that defines the single adapter surface the orchestrator
and business logic interact with. Concrete implementations (real exchange,
mock/stub) implement this contract.

No network calls are made here. This is the seam only.
"""
from abc import ABC, abstractmethod
from app.domain.live.adapter_submit_request import AdapterSubmitRequest
from app.domain.live.adapter_submit_response import AdapterSubmitResponse
from app.domain.live.adapter_cancel_request import AdapterCancelRequest
from app.domain.live.adapter_cancel_response import AdapterCancelResponse
from app.domain.live.adapter_replace_request import AdapterReplaceRequest
from app.domain.live.adapter_replace_response import AdapterReplaceResponse
from app.domain.live.adapter_order_update import AdapterOrderUpdate


class LiveExchangeClient(ABC):
    """Abstract adapter contract for live exchange operations.

    All live exchange interactions pass through this surface.
    Business logic and orchestrator never access exchange details directly.
    """

    @abstractmethod
    def submit_order(self, request: AdapterSubmitRequest) -> AdapterSubmitResponse:
        """Submit a new live order to the exchange."""
        ...

    @abstractmethod
    def cancel_order(self, request: AdapterCancelRequest) -> AdapterCancelResponse:
        """Send a cancel request for an existing live order."""
        ...

    @abstractmethod
    def replace_order(self, request: AdapterReplaceRequest) -> AdapterReplaceResponse:
        """Send a replace/amend request for an existing live order."""
        ...

    @abstractmethod
    def get_order_update(self, order_id: str) -> AdapterOrderUpdate:
        """Fetch the latest status/fill update for an order."""
        ...
