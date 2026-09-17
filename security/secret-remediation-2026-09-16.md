# Ai Factory secret remediation — 2026-09-16

Status: `BLOCKED_PENDING_DASHBOARD_ROTATION`

This record intentionally contains no key values, customer data, raw provider response, or full identifier.

## Findings

| Source | Finding | Current action | Owner gate |
|---|---|---|---|
| `STATE.md` | Historical secret-shaped notes were present in tracked content | Remove from current content; do not copy values | Provider dashboard rotation |
| `verify-stripe.py` | Previously read a local key file and could persist raw API data | Use an environment-only test key and aggregate output | Test-mode operator |
| `stripe-intents.json` | Tracked raw provider response artifact | Remove from source and ignore future artifacts | Repository maintainer |
| `downloads/` | Paid fulfillment files exist in source tree | Exclude from static deployment | Revenue OS private storage |

## Required external actions

1. In Stripe Dashboard, revoke/rotate every uncertain test or live key associated with this repository.
2. Rotate any webhook signing secret and verify the Revenue OS endpoint uses the new secret.
3. Revoke any GitHub credential that was ever pasted into repository notes or chat.
4. Record only rotation timestamp, provider, environment, and safe fingerprint suffix in a private operator system.
5. Do not enable live checkout until Revenue OS production dark-mode and canary gates pass.

No dashboard mutation or live payment was performed by this change.
