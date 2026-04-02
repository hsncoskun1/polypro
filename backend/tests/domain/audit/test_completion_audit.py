"""Tests for Final Completion Audit + Gap Closure Pack — v0.8.6."""
from app.domain.audit.audit_step_result import AuditStepResult
from app.domain.audit.gap_report import GapReport
from app.domain.audit.completion_audit_result import CompletionAuditResult
from app.domain.audit.completion_audit_evaluator import (
    evaluate_completion_audit,
    build_roadmap_audit_steps,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _complete_step(name: str) -> AuditStepResult:
    return AuditStepResult(
        roadmap_step=name,
        implemented=True,
        verified=True,
        integrated=True,
        docs_aligned=True,
        gap_found=False,
        gap_closed=False,
        remaining_blockers=[],
    )


def _incomplete_step(name: str, blocker: str) -> AuditStepResult:
    return AuditStepResult(
        roadmap_step=name,
        implemented=True,
        verified=False,
        integrated=False,
        docs_aligned=False,
        gap_found=True,
        gap_closed=False,
        remaining_blockers=[blocker],
    )


# ---------------------------------------------------------------------------
# TestAuditStepResult
# ---------------------------------------------------------------------------

class TestAuditStepResult:
    def test_defaults_not_complete(self):
        s = AuditStepResult()
        assert s.implemented is False
        assert s.verified is False
        assert s.integrated is False
        assert s.docs_aligned is False
        assert s.gap_found is False
        assert s.gap_closed is False
        assert s.remaining_blockers == []
        assert s.fully_complete is False

    def test_fully_complete_when_all_true_no_blockers(self):
        s = _complete_step("v0.1.1")
        assert s.fully_complete is True

    def test_not_fully_complete_if_not_verified(self):
        s = _complete_step("v0.1.1")
        s.verified = False
        assert s.fully_complete is False

    def test_not_fully_complete_if_gap_found(self):
        s = _complete_step("v0.1.1")
        s.gap_found = True
        assert s.fully_complete is False

    def test_not_fully_complete_if_remaining_blockers(self):
        s = _complete_step("v0.1.1")
        s.remaining_blockers = ["missing_test"]
        assert s.fully_complete is False

    def test_gap_open_when_found_not_closed(self):
        s = AuditStepResult(gap_found=True, gap_closed=False)
        assert s.gap_open is True

    def test_gap_not_open_when_closed(self):
        s = AuditStepResult(gap_found=True, gap_closed=True)
        assert s.gap_open is False

    def test_gap_not_open_when_not_found(self):
        s = AuditStepResult(gap_found=False, gap_closed=False)
        assert s.gap_open is False

    def test_blocked_reasons_independent(self):
        s1 = AuditStepResult()
        s2 = AuditStepResult()
        s1.remaining_blockers.append("x")
        assert s2.remaining_blockers == []


# ---------------------------------------------------------------------------
# TestGapReport
# ---------------------------------------------------------------------------

class TestGapReport:
    def test_defaults(self):
        g = GapReport()
        assert g.gap_type == ""
        assert g.description == ""
        assert g.severity == "low"
        assert g.closed is False
        assert g.is_open is True
        assert g.is_blocking is False

    def test_high_severity_open_is_blocking(self):
        g = GapReport(gap_type="integration_seam", severity="high", closed=False)
        assert g.is_blocking is True

    def test_high_severity_closed_not_blocking(self):
        g = GapReport(gap_type="integration_seam", severity="high", closed=True)
        assert g.is_blocking is False

    def test_low_severity_open_not_blocking(self):
        g = GapReport(gap_type="docs_misalignment", severity="low", closed=False)
        assert g.is_blocking is False

    def test_medium_severity_open_not_blocking(self):
        g = GapReport(gap_type="state_divergence", severity="medium", closed=False)
        assert g.is_blocking is False

    def test_closed_gap_is_not_open(self):
        g = GapReport(closed=True)
        assert g.is_open is False

    def test_affected_steps_independent(self):
        g1 = GapReport()
        g2 = GapReport()
        g1.affected_steps.append("v0.1.1")
        assert g2.affected_steps == []


# ---------------------------------------------------------------------------
# TestCompletionAuditResult
# ---------------------------------------------------------------------------

class TestCompletionAuditResult:
    def test_defaults_not_ready(self):
        r = CompletionAuditResult()
        assert r.completion_ready is False
        assert r.live_applied_testing_ready is False
        assert r.remaining_blockers == []
        assert r.audit_steps == []
        assert r.gap_reports == []

    def test_live_applied_testing_ready_never_auto_true(self):
        """live_applied_testing_ready must never be auto-enabled."""
        r = CompletionAuditResult(completion_ready=True)
        assert r.live_applied_testing_ready is False

    def test_total_steps(self):
        r = CompletionAuditResult(audit_steps=[_complete_step("v0.1.1"), _complete_step("v0.1.2")])
        assert r.total_steps == 2

    def test_fully_complete_steps_count(self):
        r = CompletionAuditResult(
            audit_steps=[
                _complete_step("v0.1.1"),
                _incomplete_step("v0.1.2", "missing_test"),
            ]
        )
        assert r.fully_complete_steps == 1

    def test_open_gaps(self):
        g_open = GapReport(severity="low", closed=False)
        g_closed = GapReport(severity="low", closed=True)
        r = CompletionAuditResult(gap_reports=[g_open, g_closed])
        assert len(r.open_gaps) == 1

    def test_blocking_gaps(self):
        g_high_open = GapReport(severity="high", closed=False)
        g_high_closed = GapReport(severity="high", closed=True)
        g_low_open = GapReport(severity="low", closed=False)
        r = CompletionAuditResult(gap_reports=[g_high_open, g_high_closed, g_low_open])
        assert len(r.blocking_gaps) == 1

    def test_system_coverage_summary_contains_ready(self):
        r = CompletionAuditResult(completion_ready=True)
        summary = r.system_coverage_summary
        assert "Completion ready: True" in summary
        assert "Live testing ready: False" in summary

    def test_system_coverage_summary_step_counts(self):
        r = CompletionAuditResult(
            audit_steps=[_complete_step("v0.1.1"), _complete_step("v0.1.2")],
            completion_ready=True,
        )
        assert "2/2" in r.system_coverage_summary

    def test_independent_lists(self):
        r1 = CompletionAuditResult()
        r2 = CompletionAuditResult()
        r1.remaining_blockers.append("x")
        assert r2.remaining_blockers == []


# ---------------------------------------------------------------------------
# TestCompletionAuditEvaluator
# ---------------------------------------------------------------------------

class TestCompletionAuditEvaluator:
    def test_all_complete_no_gaps_is_ready(self):
        steps = [_complete_step("v0.1.1"), _complete_step("v0.1.2")]
        result = evaluate_completion_audit(steps)
        assert result.completion_ready is True
        assert result.remaining_blockers == []

    def test_one_incomplete_step_blocks_completion(self):
        steps = [_complete_step("v0.1.1"), _incomplete_step("v0.1.2", "docs_missing")]
        result = evaluate_completion_audit(steps)
        assert result.completion_ready is False
        assert any("v0.1.2" in b for b in result.remaining_blockers)

    def test_high_severity_open_gap_blocks_completion(self):
        steps = [_complete_step("v0.1.1")]
        gaps = [GapReport(gap_type="integration_seam", severity="high", closed=False, description="seam missing")]
        result = evaluate_completion_audit(steps, gaps)
        assert result.completion_ready is False
        assert len(result.remaining_blockers) > 0

    def test_high_severity_closed_gap_does_not_block(self):
        steps = [_complete_step("v0.1.1")]
        gaps = [GapReport(gap_type="integration_seam", severity="high", closed=True, description="was fixed")]
        result = evaluate_completion_audit(steps, gaps)
        assert result.completion_ready is True

    def test_low_severity_open_gap_does_not_block(self):
        steps = [_complete_step("v0.1.1")]
        gaps = [GapReport(gap_type="docs_misalignment", severity="low", closed=False, description="minor")]
        result = evaluate_completion_audit(steps, gaps)
        assert result.completion_ready is True

    def test_live_applied_testing_ready_always_false(self):
        steps = [_complete_step("v0.1.1")]
        result = evaluate_completion_audit(steps)
        assert result.live_applied_testing_ready is False

    def test_multiple_step_blockers_aggregated(self):
        steps = [
            _incomplete_step("v0.1.1", "blocker_a"),
            _incomplete_step("v0.1.2", "blocker_b"),
        ]
        result = evaluate_completion_audit(steps)
        assert len(result.remaining_blockers) == 2
        assert result.completion_ready is False

    def test_empty_steps_ready(self):
        result = evaluate_completion_audit([])
        assert result.completion_ready is True
        assert result.remaining_blockers == []

    def test_empty_steps_live_not_ready(self):
        result = evaluate_completion_audit([])
        assert result.live_applied_testing_ready is False

    def test_gap_reports_forwarded(self):
        g = GapReport(gap_type="state_divergence", severity="medium", description="minor drift")
        result = evaluate_completion_audit([], [g])
        assert len(result.gap_reports) == 1

    def test_no_duplicate_blockers(self):
        # Two steps with same blocker text should not duplicate if same step name
        step = _incomplete_step("v0.1.1", "blocker_x")
        result = evaluate_completion_audit([step])
        count = sum(1 for b in result.remaining_blockers if "blocker_x" in b)
        assert count == 1


# ---------------------------------------------------------------------------
# TestBuildRoadmapAuditSteps
# ---------------------------------------------------------------------------

class TestBuildRoadmapAuditSteps:
    def test_all_steps_present(self):
        steps = build_roadmap_audit_steps()
        names = [s.roadmap_step for s in steps]
        assert "v0.1.1-backend-shell" in names
        assert "v0.8.5-frontend-launcher-surface-wiring-final-app-integration-pack" in names

    def test_step_count(self):
        steps = build_roadmap_audit_steps()
        assert len(steps) == 66  # v0.1.1 through v0.8.5

    def test_all_steps_fully_complete(self):
        steps = build_roadmap_audit_steps()
        for step in steps:
            assert step.fully_complete is True, f"Step not complete: {step.roadmap_step}"

    def test_full_roadmap_audit_is_ready(self):
        steps = build_roadmap_audit_steps()
        result = evaluate_completion_audit(steps)
        assert result.completion_ready is True
        assert result.remaining_blockers == []

    def test_full_roadmap_live_not_auto_enabled(self):
        steps = build_roadmap_audit_steps()
        result = evaluate_completion_audit(steps)
        assert result.live_applied_testing_ready is False

    def test_full_coverage_summary(self):
        steps = build_roadmap_audit_steps()
        result = evaluate_completion_audit(steps)
        summary = result.system_coverage_summary
        assert "66/66" in summary
        assert "Completion ready: True" in summary
        assert "Live testing ready: False" in summary
