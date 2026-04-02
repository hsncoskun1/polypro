"""Tests for launcher readiness gate — ReadinessState, ReadinessResult, evaluate_readiness."""
from app.domain.launcher.readiness_evaluator import evaluate_readiness
from app.domain.launcher.readiness_result import ReadinessResult
from app.domain.launcher.readiness_state import ReadinessState


class TestReadinessState:
    def test_defaults_are_all_blocked(self):
        state = ReadinessState()
        assert state.setup_completed is False
        assert state.update_required is False
        assert state.preflight_passed is False

    def test_fully_ready_state(self):
        state = ReadinessState(
            setup_completed=True,
            update_required=False,
            preflight_passed=True,
        )
        assert state.setup_completed is True
        assert state.update_required is False
        assert state.preflight_passed is True


class TestReadinessResult:
    def test_access_allowed_fields(self):
        result = ReadinessResult(access_allowed=True)
        assert result.access_allowed is True
        assert result.blocker_reasons == []

    def test_access_blocked_with_reasons(self):
        result = ReadinessResult(
            access_allowed=False,
            blocker_reasons=["setup_not_completed", "preflight_not_passed"],
        )
        assert result.access_allowed is False
        assert len(result.blocker_reasons) == 2


class TestEvaluateReadiness:
    def test_setup_not_completed_blocks_access(self):
        state = ReadinessState(setup_completed=False, preflight_passed=True)
        result = evaluate_readiness(state)
        assert result.access_allowed is False
        assert "setup_not_completed" in result.blocker_reasons

    def test_update_required_blocks_access(self):
        state = ReadinessState(
            setup_completed=True,
            update_required=True,
            preflight_passed=True,
        )
        result = evaluate_readiness(state)
        assert result.access_allowed is False
        assert "update_required" in result.blocker_reasons

    def test_preflight_not_passed_blocks_access(self):
        state = ReadinessState(setup_completed=True, preflight_passed=False)
        result = evaluate_readiness(state)
        assert result.access_allowed is False
        assert "preflight_not_passed" in result.blocker_reasons

    def test_all_conditions_met_allows_access(self):
        state = ReadinessState(
            setup_completed=True,
            update_required=False,
            preflight_passed=True,
        )
        result = evaluate_readiness(state)
        assert result.access_allowed is True
        assert result.blocker_reasons == []

    def test_multiple_blockers_all_in_reason_list(self):
        state = ReadinessState(
            setup_completed=False,
            update_required=True,
            preflight_passed=False,
        )
        result = evaluate_readiness(state)
        assert result.access_allowed is False
        assert "setup_not_completed" in result.blocker_reasons
        assert "update_required" in result.blocker_reasons
        assert "preflight_not_passed" in result.blocker_reasons
        assert len(result.blocker_reasons) == 3

    def test_fail_closed_single_blocker_denies_access(self):
        """Any single blocker is sufficient to deny access — fail-closed."""
        state = ReadinessState(
            setup_completed=True,
            update_required=False,
            preflight_passed=False,  # only one blocker
        )
        result = evaluate_readiness(state)
        assert result.access_allowed is False

    def test_default_state_blocks_access(self):
        """Default ReadinessState (all defaults) must block access."""
        result = evaluate_readiness(ReadinessState())
        assert result.access_allowed is False
        assert "setup_not_completed" in result.blocker_reasons
        assert "preflight_not_passed" in result.blocker_reasons

    def test_update_not_required_does_not_add_blocker(self):
        state = ReadinessState(
            setup_completed=True,
            update_required=False,
            preflight_passed=True,
        )
        result = evaluate_readiness(state)
        assert "update_required" not in result.blocker_reasons
