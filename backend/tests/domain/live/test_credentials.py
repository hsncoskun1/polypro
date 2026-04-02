"""Tests for live credential integration + secrets handling — v0.7.1."""
from app.domain.live.live_credentials import LiveCredentials
from app.domain.live.secrets_masker import mask_secret
from app.domain.live.secrets_result import SecretsResult
from app.domain.live.credential_evaluator import evaluate_credential_completeness
from app.domain.live.credential_readiness_bridge import credentials_to_readiness_flags


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def empty_creds(**overrides) -> LiveCredentials:
    """All credentials absent."""
    defaults = dict(
        wallet_address="",
        private_key="",
        funder_address="",
        relayer_api="",
        api_key="",
        api_secret="",
        api_passphrase="",
    )
    defaults.update(overrides)
    return LiveCredentials(**defaults)


def full_creds(**overrides) -> LiveCredentials:
    """All credentials present."""
    defaults = dict(
        wallet_address="0xABCDEF1234567890",
        private_key="priv_key_secret_value",
        funder_address="0xFUNDER1234567890",
        relayer_api="https://relayer.example.com/api",
        api_key="APIKEY1234",
        api_secret="APISECRET5678",
        api_passphrase="PASSPHRASE9012",
    )
    defaults.update(overrides)
    return LiveCredentials(**defaults)


# ---------------------------------------------------------------------------
# TestLiveCredentials
# ---------------------------------------------------------------------------

class TestLiveCredentials:
    def test_all_fields_default_to_empty_string(self):
        creds = LiveCredentials()
        assert creds.wallet_address == ""
        assert creds.private_key == ""
        assert creds.funder_address == ""
        assert creds.relayer_api == ""
        assert creds.api_key == ""
        assert creds.api_secret == ""
        assert creds.api_passphrase == ""

    def test_all_fields_can_be_set(self):
        creds = full_creds()
        assert creds.wallet_address == "0xABCDEF1234567890"
        assert creds.api_key == "APIKEY1234"
        assert creds.private_key == "priv_key_secret_value"

    def test_partial_credentials(self):
        creds = empty_creds(wallet_address="0xABC", api_key="KEY123")
        assert creds.wallet_address == "0xABC"
        assert creds.api_key == "KEY123"
        assert creds.private_key == ""


# ---------------------------------------------------------------------------
# TestSecretsMasker
# ---------------------------------------------------------------------------

class TestSecretsMasker:
    def test_empty_string_returns_not_set(self):
        assert mask_secret("") == "NOT_SET"

    def test_single_char_returns_mask(self):
        assert mask_secret("x") == "****"

    def test_four_chars_returns_mask(self):
        assert mask_secret("abcd") == "****"

    def test_five_chars_shows_first_four_plus_mask(self):
        result = mask_secret("abcde")
        assert result == "abcd****"

    def test_long_secret_shows_first_four_plus_mask(self):
        result = mask_secret("APIKEY1234567890")
        assert result == "APIK****"

    def test_plaintext_not_in_masked_output(self):
        secret = "SuperSecretValue123"
        result = mask_secret(secret)
        assert "SuperSecretValue" not in result
        assert result == "Supe****"

    def test_mask_does_not_return_full_value(self):
        secret = "longpassphrase"
        result = mask_secret(secret)
        assert result != secret


# ---------------------------------------------------------------------------
# TestSecretsResult
# ---------------------------------------------------------------------------

class TestSecretsResult:
    def test_complete_result_fields(self):
        result = SecretsResult(is_complete=True, missing_fields=[], masked_summary={"api_key": "APIK****"})
        assert result.is_complete is True
        assert result.missing_fields == []
        assert result.masked_summary["api_key"] == "APIK****"

    def test_incomplete_result_fields(self):
        result = SecretsResult(is_complete=False, missing_fields=["api_key"], masked_summary={"api_key": "NOT_SET"})
        assert result.is_complete is False
        assert "api_key" in result.missing_fields

    def test_defaults_are_empty(self):
        result = SecretsResult(is_complete=True)
        assert result.missing_fields == []
        assert result.masked_summary == {}


# ---------------------------------------------------------------------------
# TestCredentialEvaluator
# ---------------------------------------------------------------------------

class TestCredentialEvaluator:
    def test_all_present_is_complete(self):
        result = evaluate_credential_completeness(full_creds())
        assert result.is_complete is True
        assert result.missing_fields == []

    def test_all_absent_is_not_complete(self):
        result = evaluate_credential_completeness(empty_creds())
        assert result.is_complete is False
        assert len(result.missing_fields) == 7

    def test_wallet_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(wallet_address=""))
        assert result.is_complete is False
        assert "wallet_address" in result.missing_fields

    def test_private_key_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(private_key=""))
        assert "private_key" in result.missing_fields

    def test_api_key_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(api_key=""))
        assert "api_key" in result.missing_fields

    def test_api_secret_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(api_secret=""))
        assert "api_secret" in result.missing_fields

    def test_api_passphrase_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(api_passphrase=""))
        assert "api_passphrase" in result.missing_fields

    def test_funder_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(funder_address=""))
        assert "funder_address" in result.missing_fields

    def test_relayer_missing_detected(self):
        result = evaluate_credential_completeness(full_creds(relayer_api=""))
        assert "relayer_api" in result.missing_fields

    def test_all_checks_run_no_short_circuit(self):
        """Multiple missing fields must all appear in missing_fields."""
        result = evaluate_credential_completeness(
            full_creds(wallet_address="", api_key="", private_key="")
        )
        assert "wallet_address" in result.missing_fields
        assert "api_key" in result.missing_fields
        assert "private_key" in result.missing_fields
        assert len(result.missing_fields) == 3

    def test_masked_summary_contains_all_fields(self):
        result = evaluate_credential_completeness(full_creds())
        expected_fields = {
            "wallet_address", "private_key", "funder_address",
            "relayer_api", "api_key", "api_secret", "api_passphrase",
        }
        assert set(result.masked_summary.keys()) == expected_fields

    def test_masked_summary_missing_field_shows_not_set(self):
        result = evaluate_credential_completeness(full_creds(api_key=""))
        assert result.masked_summary["api_key"] == "NOT_SET"

    def test_masked_summary_present_field_does_not_expose_plaintext(self):
        creds = full_creds(api_key="APIKEY1234")
        result = evaluate_credential_completeness(creds)
        assert result.masked_summary["api_key"] != "APIKEY1234"
        assert "APIKEY1234" not in result.masked_summary["api_key"]

    def test_two_missing_fields_both_in_result(self):
        result = evaluate_credential_completeness(
            full_creds(relayer_api="", funder_address="")
        )
        assert result.is_complete is False
        assert len(result.missing_fields) == 2


# ---------------------------------------------------------------------------
# TestCredentialReadinessBridge
# ---------------------------------------------------------------------------

class TestCredentialReadinessBridge:
    def test_all_present_all_flags_true(self):
        flags = credentials_to_readiness_flags(full_creds())
        assert flags["wallet_address_present"] is True
        assert flags["private_key_present"] is True
        assert flags["funder_address_present"] is True
        assert flags["relayer_api_present"] is True
        assert flags["api_key_present"] is True
        assert flags["api_secret_present"] is True
        assert flags["api_passphrase_present"] is True

    def test_all_absent_all_flags_false(self):
        flags = credentials_to_readiness_flags(empty_creds())
        assert flags["wallet_address_present"] is False
        assert flags["private_key_present"] is False
        assert flags["funder_address_present"] is False
        assert flags["relayer_api_present"] is False
        assert flags["api_key_present"] is False
        assert flags["api_secret_present"] is False
        assert flags["api_passphrase_present"] is False

    def test_wallet_absent_flag_false(self):
        flags = credentials_to_readiness_flags(full_creds(wallet_address=""))
        assert flags["wallet_address_present"] is False

    def test_api_key_absent_flag_false(self):
        flags = credentials_to_readiness_flags(full_creds(api_key=""))
        assert flags["api_key_present"] is False

    def test_partial_creds_partial_flags(self):
        creds = empty_creds(wallet_address="0xABC", api_key="KEY")
        flags = credentials_to_readiness_flags(creds)
        assert flags["wallet_address_present"] is True
        assert flags["api_key_present"] is True
        assert flags["private_key_present"] is False
        assert flags["api_secret_present"] is False

    def test_flags_feed_live_readiness_context(self):
        """Bridge output maps onto LiveReadinessContext credential fields."""
        from app.domain.live.live_readiness_context import LiveReadinessContext
        from app.domain.live.live_readiness_evaluator import evaluate_live_readiness
        flags = credentials_to_readiness_flags(full_creds())
        ctx = LiveReadinessContext(
            simulation_mode_default=False,
            live_mode_requested=True,
            live_mode_enabled=True,
            explicit_live_enable=True,
            **flags,
        )
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is True
        assert result.blocker_reasons == []

    def test_partial_flags_block_live_readiness(self):
        """Missing credentials via bridge → readiness blocked."""
        from app.domain.live.live_readiness_context import LiveReadinessContext
        from app.domain.live.live_readiness_evaluator import evaluate_live_readiness
        flags = credentials_to_readiness_flags(full_creds(api_key="", private_key=""))
        ctx = LiveReadinessContext(
            simulation_mode_default=False,
            live_mode_requested=True,
            live_mode_enabled=True,
            explicit_live_enable=True,
            **flags,
        )
        result = evaluate_live_readiness(ctx)
        assert result.live_ready is False
        assert "api_key_missing" in result.blocker_reasons
        assert "private_key_missing" in result.blocker_reasons
