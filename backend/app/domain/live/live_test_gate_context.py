"""Live test gate context — v0.8.4.

The live test gate is the technical barrier between backend-ready and
live applied testing. It is ALWAYS evaluated separately from release readiness.
live_applied_testing_ready can only be True when ALL gate conditions are met
AND the gate is explicitly enabled — it is never auto-propagated.
"""
from dataclasses import dataclass


@dataclass
class LiveTestGateContext:
    """Context for live test gate evaluation.

    Attributes:
        release_ready: Backend release readiness has been confirmed.
        live_test_gate_enabled: Live test gate has been explicitly enabled.
        live_test_gate_passed: All live test gate conditions are met.
    """
    release_ready: bool = False
    live_test_gate_enabled: bool = False
    live_test_gate_passed: bool = False
