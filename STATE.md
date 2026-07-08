# STATE — Ai Factory Sales Funnel

## Status: ✅ E2E TESTED + DEPLOYED (Test Mode)

## Live URL
**https://Ai Factory-sales-pages.vercel.app** (aliased)

## E2E Test Results (10/10 PASS)
**Date:** 2026-06-05 ~23:02-23:05 (UTC+7)
**Tool:** Playwright + Python (Chromium headless)
**Card:** 4242 4242 4242 4242 (test mode, no 3DS)
**Avg time per product:** 23.3s

| # | Product | Final URL | Stripe PI | Status |
|---|---|---|---|---|
| 1 | Prompt Pack | /thanks-01-prompt-pack-th.html | pi_3TfMfq9F7z3axLAJ0bl4iejW | succeeded |
| 2 | Obsidian | /thanks-02-obsidian-student-kit.html | pi_3TfMgD9F7z3axLAJ1cl1hKkC | succeeded |
| 3 | Calculator | /thanks-03-freelance-pricing-calculator.html | pi_3TfMgb9F7z3axLAJ1rgeS6FI | succeeded |
| 4 | Cold Email | /thanks-04-cold-email-template-pack.html | pi_3TfMhk9F7z3axLAJ1VBKfFOy | succeeded |
| 5 | AI Automation | /thanks-05-ai-automation-workflow.html | pi_3TfMiV9F7z3axLAJ0mfEhXSC | succeeded |
| 6 | CV | /thanks-06-cv-international-template.html | pi_3TfMit9F7z3axLAJ0Rn1t141 | succeeded |
| 7 | n8n | /thanks-07-n8n-sme-workflow-pack.html | pi_3TfMjG9F7z3axLAJ1wkN5vaV | succeeded |
| 8 | Calendar | /thanks-08-content-calendar-90d.html | pi_3TfMhN9F7z3axLAJ00McpKFn | succeeded |
| 9 | Finance | /thanks-09-finance-tracker-thb.html | pi_3TfMgz9F7z3axLAJ0jkmWsVZ | succeeded |
| 10 | AI Agent | /thanks-10-ai-agent-starter-github.html | pi_3TfMi79F7z3axLAJ1BMQ1487 | succeeded |

**Total test revenue:** 9,178 THB (22 PIs, 2 test runs, verified via Stripe API)

## Audit 7d — 2026-06-05
- 22 PaymentIntents, 22 Charges, 0 Refunds, 0 Disputes
- Account: TH, charges+payouts enabled, default_currency=thb
- All charges `paid=True`, 0 customers (guest checkout)
- **No suspicious activity**

## Product Name Sync (HTML ↔ Stripe) — 2026-06-05
- 3 products renamed via API to match HTML:
  - "N8N Workflow Pack SME" → "n8n SME Workflow Pack"
  - "Obsidian Starter Kit นักศึกษา" → "Obsidian Student Kit (นักศึกษา)"
  - "AI Prompt Pack ภาษาไทย" → "AI Prompt Pack (ภาษาไทย)"
- 5 already matched
- 2 simplified: "Cold Email Template Pack TH/EN" → "Cold Email Template Pack", "CV/Resume Template สมัครงานต่างประเทศ" → "CV International Template"
- **Verified**: product 07 checkout now shows "n8n SME Workflow Pack — THB 799.00" (match HTML)

## Test Files
- `test-all-stripe.py` — main E2E script (Playwright)
- `test-1.py` — single-product debug
- `verify-stripe.py` — Stripe API verification
- `inspect-stripe.py` / `inspect-stripe2.py` — DOM inspection (debug)
- `e2e-screenshots/` — 20 PNGs (card filled + success page per product)
- `e2e-results.json` — structured results
- `stripe-intents.json` — raw API response

## Key Discovery
**Stripe Payment Link ที่ Stripe สร้าง default ใช้ legacy "accordion" layout** ไม่ใช่ Payment Element iframes:
- Card form เป็น regular HTML inputs (`input[name="cardNumber"]`, `cardExpiry`, `cardCvc`, `billingName`)
- ไม่ใช่ Stripe Elements iframe
- ใช้ selector ตรงๆ ได้ ไม่ต้อง `frameLocator`

## Verified URL Patterns
| Pattern | Status | Example |
|---|---|---|
| `/` | 200 | Homepage |
| `/products` | 200 | Rewrite → index.html |
| `/01-prompt-pack-th` | 200 | Clean URL (via rewrite) |
| `/01-prompt-pack-th.html` | 200 | Direct file |
| `/t/prompt-pack-th` | 200 | Short URL (via rewrite) |
| `/thanks-01-prompt-pack-th` | 200 | Post-purchase |
| `/demo` | 200 | Mock Stripe flow |

## Security Headers (Vercel)
- X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, HSTS, Permissions-Policy

## 🔴 P0 — Keys to Roll
1. **Stripe test** `sk_test_51TRgPq9F7z3axLAJ...` (was in chat + used in verify-stripe.py)
2. **Stripe live** `sk_live_51SwptU0u86vWnztX...` (was in chat)
3. **GitHub PAT** `ghp_HSC063GShAJoYdZZg...` (was in chat)

## 🔴 P0 — Before Live Mode
1. **Roll ALL 3 keys above** (paste = leaked, must rotate in Dashboard)
2. **Change Stripe account name** "Ai Factory" → "Ai Factory" (Dashboard → Settings → Public details → Business name) — visible on every checkout
3. **Optional**: delete 22 test PIs in Dashboard (test mode ไม่กระทบ)

## 🟡 P1 — Before Live Mode
- Replace "Ai Factory" / "support@aifactory.co" placeholders in footer + thanks pages (10 files) with real brand + email
- Update Stripe products to real product images (optional, cosmetic)

## What User Can Do Now
| Option | Action |
|---|---|
| **B** | Switch to live mode (roll keys first, fix Ai Factory) |
| **D2** | Update "Ai Factory" placeholders with real brand name (I need real name) |
| **D3** | Cleanup test data (delete 22 test PIs) |
| **D4** | Deploy to Netlify as backup |
| **D5** | Other copy/design |

## Files
- `vercel.json` — 23 rewrites + 6 security headers
- `deploy-and-test.ps1` — main deploy script (env-based, safety guard)
- `test-smoke.ps1` — local tests (79/79)
- `test-deployed.ps1` — Vercel tests (24/24)
- `test-all-stripe.py` — E2E Stripe test (10/10)
- `verify-stripe.py` — API verification (11/11)
- `rename-stripe-products.py` — API rename tool
- `verify-rename.py` — verify new name in checkout
- `audit-stripe.py` — 7-day audit
- `stripe-links.json` — 10 test payment links
- `SECURITY.md` — key rotation + incident response
- 10 landing pages + 10 thanks pages + 10 downloads
- 30 E2E screenshots (10 card-filled + 10 success + 10 landing)
- `e2e-screenshots/verify-07-checkout.png` — name fix proof
