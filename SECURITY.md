# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities directly to **nxme176@gmail.com** with subject `SECURITY: <repo>`.

- We will acknowledge within 48h and provide a timeline for a fix.
- Please do not disclose publicly until a fix is released (coordinated disclosure, 90 days).
- Redacted NDA-related repos (Predictive, Plexta) — do not include confidential data in reports.

## Scope

This policy covers all code in this repository. For enterprise deployments, contact the maintainer for private patch coordination.

## Payment and fulfillment boundary

- This repository is a static storefront only. It must not contain product files in the deployed output.
- Revenue OS owns Stripe secret keys, webhook verification, catalog identity, entitlements, and private delivery URLs.
- Never add Stripe secret keys, webhook signing secrets, customer payloads, card data, or raw provider responses to this repository.
- `downloads/` is source-only material and is excluded by `.vercelignore`; it is not a fulfillment endpoint.
- A live launch requires dashboard key rotation evidence, staging money-path evidence, a production dark-mode receipt, and one explicitly approved canary charge.

## Incident response

If a secret-shaped value appears in current files or history, stop live deployment, revoke or rotate it in the provider dashboard, record only the provider, timestamp, and safe fingerprint suffix, then remove the value from current files. History rewriting requires a separate explicit approval.
