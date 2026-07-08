# Stripe Update Guide — Ai Factory → Ai Factory

## 1. Change Account Name

1. Login to Stripe Dashboard → **Settings** (⚙️)
2. **Business settings** → **Business details**
3. Click **Edit** next to "Business name"
4. Change from **Ai Factory** to **Ai Factory**
5. Save

## 2. All 10 Products

| # | Slug | Name (TH) | Price |
|---|------|-----------|-------|
| 01 | `01-prompt-pack-th` | AI Prompt Pack ภาษาไทย | ฿299 |
| 02 | `02-obsidian-student-kit` | Obsidian Starter Kit นักศึกษา | ฿199 |
| 03 | `03-freelance-pricing-calculator` | Freelance Pricing Calculator | ฿149 |
| 04 | `04-cold-email-template-pack` | Cold Email Template Pack TH/EN | ฿399 |
| 05 | `05-ai-automation-workflow` | AI Automation Workflow Cheatsheet | ฿499 |
| 06 | `06-cv-international-template` | CV/Resume Template สมัครงานต่างประเทศ | ฿199 |
| 07 | `07-n8n-sme-workflow-pack` | N8N Workflow Pack SME | ฿799 |
| 08 | `08-content-calendar-90d` | Content Calendar 90 วัน | ฿599 |
| 09 | `09-finance-tracker-thb` | Personal Finance Tracker (THB) | ฿149 |
| 10 | `10-ai-agent-starter-github` | AI Agent Starter (GitHub) | ฿999 |

## 3. Create New Payment Links (Live Mode)

**⚠️ Switch to LIVE mode first** (top-right toggle in Stripe Dashboard)

For each product:

1. Go to **Payments** → **Payment Links**
2. Click **+ New**
3. Select the product (create new if it doesn't exist in live)
4. Set price to match table above
5. Enable **collect billing address**
6. Click **Create link**
7. Copy the `https://buy.stripe.com/...` URL

Repeat for all 10 products.

## 4. Update `stripe-links.json`

After creating live links, replace the test URLs:

```json
{
    "01-prompt-pack-th": "https://buy.stripe.com/LIVE_LINK_HERE",
    "02-obsidian-student-kit": "https://buy.stripe.com/LIVE_LINK_HERE",
    "03-freelance-pricing-calculator": "https://buy.stripe.com/LIVE_LINK_HERE",
    "04-cold-email-template-pack": "https://buy.stripe.com/LIVE_LINK_HERE",
    "05-ai-automation-workflow": "https://buy.stripe.com/LIVE_LINK_HERE",
    "06-cv-international-template": "https://buy.stripe.com/LIVE_LINK_HERE",
    "07-n8n-sme-workflow-pack": "https://buy.stripe.com/LIVE_LINK_HERE",
    "08-content-calendar-90d": "https://buy.stripe.com/LIVE_LINK_HERE",
    "09-finance-tracker-thb": "https://buy.stripe.com/LIVE_LINK_HERE",
    "10-ai-agent-starter-github": "https://buy.stripe.com/LIVE_LINK_HERE"
}
```

## 5. Run replace-stripe-links.ps1

After updating `stripe-links.json`, run:

```powershell
cd C:\Users\menum\sales_pages
.\replace-stripe-links.ps1
```

This will replace all `{{STRIPE_LINK}}` placeholders in the HTML files with the live URLs.

## 6. Verify

- Open any HTML file and confirm the link is `https://buy.stripe.com/...`
- Test with card `4242 4242 4242 4242` (if still in test mode)
- Deploy to Netlify
