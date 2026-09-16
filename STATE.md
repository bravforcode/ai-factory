# STATE — Ai Factory Sales Funnel

## Current status

`TEST_MODE_ONLY — LIVE_LAUNCH_BLOCKED`

This repository is a static storefront. Revenue OS is the canonical owner of
catalog identity, webhook verification, orders, entitlements, and private
fulfillment. No production or live-payment claim is made by this file.

## Verified local surfaces

- Ten product landing pages and ten thank-you pages are present in the source tree.
- `products.json` is the storefront display catalog.
- `stripe-links-live.json` contains customer-facing Payment Link URLs only; it is
  not proof that the links are live, reachable, correctly priced, or fulfilled.
- `test-smoke.ps1` is local-only and must not be read as deployment evidence.
- `test-all-stripe.py` is a test-mode browser flow and must not be run against
  live links or live keys.
- `downloads/` is source material only and is excluded from Vercel output.

## Launch blockers

1. Rotate/revoke every uncertain Stripe and GitHub credential associated with
   historical repository content; record only safe dashboard evidence privately.
2. Move paid assets to private storage managed by Revenue OS.
3. Complete Revenue OS staging and production-dark evidence, including signed
   webhook, idempotency, entitlement, delivery, refund, and rollback receipts.
4. Obtain explicit approval for one bounded real-payment canary.
5. Reconcile the canary before enabling additional products or paid traffic.

See `security/secret-remediation-2026-09-16.md` for the redacted remediation
record. No dashboard mutation, deploy, archive, delete, or live payment was
performed by this change.
