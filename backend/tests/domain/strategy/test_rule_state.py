from app.domain.strategy.rule_state import RuleState


def test_rule_state_values_are_strings():
    assert RuleState.PASS == "pass"
    assert RuleState.FAIL == "fail"
    assert RuleState.WAITING == "waiting"
    assert RuleState.DISABLED == "disabled"
    assert RuleState.LOCKED_BY_ADMIN == "locked_by_admin"


def test_rule_state_has_five_members():
    assert len(RuleState) == 5
