# Credential Rotation Runbook — POLYPRO

## Incident Summary

**Date:** 2026-04-03
**Commit:** `466e428` (feat: v1.0.7 Admin Control + Visibility UI Completion Pack)
**Exposure:** `env.txt` containing real Polymarket credentials was committed
and pushed to remote (`origin/main`).

**Cleanup:** Commit `82f8600` removed the file from tracking and added it to
`.gitignore`. The file no longer exists in the working tree or current HEAD.

**Status of history:** Git history on remote (`github.com/hsncoskun1/polypro`)
still contains the credential values at commit `466e428`. History was NOT
rewritten. See Section 5 for history rewrite guidance.

---

## 1. Credentials Exposed

The following credential types were present in `env.txt`:

| Credential | Type | Action Required |
|------------|------|-----------------|
| POLYMARKET_API_KEY | Polymarket CLOB API key | ⚠️ ROTATE |
| POLYMARKET_SECRET | Polymarket API secret | ⚠️ ROTATE |
| POLYMARKET_PASSPHRASE | Polymarket API passphrase | ⚠️ ROTATE |
| POLYMARKET_FUNDER | Funder wallet address | Review — address is public by nature; review associated key |
| POLYMARKET_PRIVATE_KEY | Wallet private key (if present) | ⚠️ ROTATE if exposed |
| POLYMARKET_SIG_TYPE | Signature type integer | Not sensitive |

---

## 2. Immediate Actions (Operator)

### Step 1 — Revoke exposed API credentials
1. Log in to Polymarket CLOB dashboard
2. Navigate to API Keys section
3. Revoke / delete the exposed API key
4. Generate a new API key + secret + passphrase
5. Record new values in a secure secret manager (NOT in any file in this repo)

### Step 2 — Review wallet security
- If the funder wallet private key was exposed, consider moving funds to a
  new wallet immediately
- Generate a new wallet and transfer any funds
- Update the funder address in new credentials

### Step 3 — Verify no unauthorized activity
- Review Polymarket order history for the exposed credentials
- Check for any orders not placed by you
- Review wallet transaction history for unexpected activity

---

## 3. How to Load New Credentials into POLYPRO

### Current mechanism (development)
The application does NOT automatically read Polymarket credentials from
environment variables at startup. `LiveCredentials` defaults to empty strings.
Credentials must be injected at the integration layer.

**For development/testing:** Pass credentials as constructor arguments to
`ProductionExchangeClient` or `LiveExecutionDriver`.

**For local operation:** Set environment variables before starting the backend.
The backend does not currently call `os.getenv()` for Polymarket credentials —
this is a planned feature (credential loader from env).

### Secure local credential loading (interim pattern)

Until a credential loader is implemented, use OS-level environment variables:

```bash
# Windows PowerShell — set before starting backend
$env:POLYMARKET_API_KEY = "your_new_key"
$env:POLYMARKET_SECRET = "your_new_secret"
$env:POLYMARKET_PASSPHRASE = "your_new_passphrase"
$env:POLYMARKET_FUNDER = "your_funder_address"
$env:POLYMARKET_PRIVATE_KEY = "your_private_key"

# Then start backend
cd backend
.venv/Scripts/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Never:**
- Store credentials in `env.txt` or any file that could be committed
- Hardcode credential values in source files
- Log credential values anywhere

---

## 4. Fail-Closed Verification

The application enforces fail-closed behavior for missing credentials:

| Layer | Mechanism | Behavior when credentials missing |
|-------|-----------|----------------------------------|
| `credential_evaluator.py` | `evaluate_credential_completeness()` | Returns `is_complete=False`, lists `missing_fields` |
| `live_execution_driver.py` | `outbound_allowed` + `preflight_passed` guards | Returns `PREFLIGHT_BLOCKED` immediately |
| `polymarket_request_signer.py` | `_assert_credentials_ready()` | Raises `PolymarketAuthError` |
| `LiveCredentials.__repr__` | Override | Credential values never appear in repr/logs |

**No fake success at any step.** Empty credentials → blocked, not passed through.

---

## 5. Git History — Rewrite Guidance

The credentials exist in git commit history at `466e428`. To remove from history:

```
# WARNING: History rewrite rewrites all commits after the target.
# All collaborators must re-clone or rebase after this.
# Only perform if this is a critical security requirement.

# Option A: BFP Repo Cleaner (recommended)
# java -jar bfg.jar --delete-files env.txt your-repo.git

# Option B: git filter-branch (slower)
# git filter-branch --force --index-filter \
#   "git rm --cached --ignore-unmatch env.txt" \
#   --prune-empty --tag-name-filter cat -- --all
# git push origin --force --all
```

**Recommendation:** Since credentials are being rotated (Step 2 above), history
rewrite is optional. Rotated credentials in history are no longer valid and pose
no operational risk. Rewrite only if required by a compliance policy.

---

## 6. Prevention — What Changed in v1.0.8

| Change | File | Effect |
|--------|------|--------|
| `env.txt` added to `.gitignore` | `.gitignore` | File cannot be committed again |
| `*.secret`, `credentials.*` added | `.gitignore` | Common secret file patterns blocked |
| `logs/`, `*.log`, `*.pem`, `*.key` added | `.gitignore` | Log and key files blocked |
| `LiveCredentials.__repr__` override | `live_credentials.py` | Credential values never appear in repr/logs |
| `.env.example` created | `.env.example` | Safe template with placeholder values |
| Security warning on forgot-password | `api/auth.py` | Production email delivery requirement documented |

---

## 7. Checklist

- [ ] Polymarket API key revoked
- [ ] New API key + secret + passphrase generated
- [ ] New credentials stored in secure secret manager
- [ ] Wallet reviewed (no unauthorized activity)
- [ ] New credentials loaded into application (see Section 3)
- [ ] Application tested with new credentials (fail-closed test: empty → blocked)
- [ ] History rewrite performed (if required by policy)
- [ ] This runbook reviewed and signed off
