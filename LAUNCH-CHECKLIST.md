# LAUNCH CHECKLIST — aifactory.co

> 10 steps from "code is done" to "first paying customer".
> Check off as you go. Total estimated time: **1 day of focused work**.

---

## ✅ COMPLETED

### Pre-Launch

- [x] **Brand Change → Ai Factory** — All pages rebranded
- [x] **Homepage Optimized** — Product grid, hero, CTAs ready
- [x] **Email Templates Created** — Launch email + reminder templates in `email-templates.md`
- [x] **Facebook Ads Created** — 3 creatives ready (single image, carousel, video)

### Deploy

- [x] **Deployed to Vercel** — Live and accessible
- [x] **Thanks Pages Updated** — All 10 product thank-you pages functional

---

## ⏳ REMAINING — Do This Now

### 🔴 CRITICAL (Day 0 — Today)

- [ ] **1. Stripe LIVE Mode Setup**
  - [ ] Log in to Stripe Dashboard → Switch from Test to **Live** mode
  - [ ] Create 10 Payment Links in LIVE mode:
    - [ ] 01 — `prompt-pack-th` — ฿299
    - [ ] 02 — `obsidian-student-kit` — ฿199
    - [ ] 03 — `freelance-pricing-calculator` — ฿149
    - [ ] 04 — `cold-email-template-pack` — ฿399
    - [ ] 05 — `ai-automation-workflow` — ฿499
    - [ ] 06 — `cv-international-template` — ฿199
    - [ ] 07 — `n8n-sme-workflow-pack` — ฿799
    - [ ] 08 — `content-calendar-90d` — ฿599
    - [ ] 09 — `finance-tracker-thb` — ฿149
    - [ ] 10 — `ai-agent-starter-github` — ฿999
  - [ ] Set success redirect URL to `https://aifactory.co/thanks-<NN>-<slug>.html`
  - [ ] Enable "Collect billing address" = ON
  - [ ] Enable "Send Stripe email receipts" = ON
  - [ ] Run `replace-stripe-links.ps1` with live URLs
  - [ ] Test 1 purchase end-to-end with real card (small amount)
  - [ ] Verify redirect + receipt email

- [ ] **2. Domain Purchase**
  - [ ] Buy `aifactory.co` (Namecheap / Cloudflare Registrar — ฿300–500/yr)
  - [ ] Connect domain to Vercel
  - [ ] Wait for DNS propagation (5–60 min)
  - [ ] Enable HTTPS (auto via Vercel)
  - [ ] Test: `http://aifactory.co` → redirects to `https://aifactory.co`

- [ ] **3. OG Image Creation**
  - [ ] Design OG image for social sharing (1200×630px)
  - [ ] Upload to `sales_pages/images/og-image.png`
  - [ ] Add to `<head>` in all HTML files: `<meta property="og:image" content="https://aifactory.co/images/og-image.png">`

---

### 🟡 IMPORTANT (Day 1)

- [ ] **4. Netlify Backup Deploy**
  - [ ] Drag `sales_pages/` folder to https://app.netlify.com/drop
  - [ ] Verify all pages load correctly on Netlify
  - [ ] This is your backup if Vercel has issues

- [ ] **5. Email Launch (~100 emails)**
  - [ ] Send launch email at **10:00 Thailand time** (Tuesday/Wednesday best)
  - [ ] Subject line A/B: 2 variants
  - [ ] Include: hero product + 3-product grid + "buy now" CTA
  - [ ] Wait 24h, check open rate (target > 30%) and click rate (target > 5%)
  - [ ] Send "24h reminder" to non-clickers

- [ ] **6. Facebook Ads Launch**
  - [ ] Launch campaign in Meta Ads Manager
  - [ ] Budget: ฿300/day, lifetime ฿1,500
  - [ ] Audience: Thailand, 22–45, interests = ChatGPT/Freelance/Marketing
  - [ ] UTM tag every ad URL: `?utm_source=fb&utm_medium=cpc&utm_campaign=launch&utm_content=ad1`

---

### 🟢 MONITOR (Day 2–5)

- [ ] **7. Daily Monitoring**
  - [ ] Check Stripe Dashboard for new sales
  - [ ] Check email open/click rates
  - [ ] Check Facebook ad performance (CPC, CTR, ROAS)
  - [ ] Respond to support emails within 24h

---

### 🔵 ANALYZE (Day 6–7)

- [ ] **8. Week 1 Review**
  - [ ] Total revenue
  - [ ] Total orders
  - [ ] Top selling product → make it homepage hero
  - [ ] Best ad creative → scale it
  - [ ] Kill bottom 50% of Facebook creatives
  - [ ] Email open/click rate summary
  - [ ] Refund rate (target < 5%)

---

## 🗓️ DAY-BY-DAY LAUNCH PLAN

| Day | Focus | Tasks | Time |
|-----|-------|-------|------|
| **Day 0** (Today) | 🔴 Setup | Stripe LIVE + Domain purchase + OG image | 2–3 hrs |
| **Day 1** | 🟡 Launch | Netlify backup + Email send + FB ads launch | 2–3 hrs |
| **Day 2** | 🟢 Monitor | Check sales, emails, ads. Respond to support | 30 min |
| **Day 3** | 🟢 Optimize | Review top product → update homepage hero | 30 min |
| **Day 4** | 🟢 Optimize | Review FB data → kill bad creatives | 30 min |
| **Day 5** | 🟢 Optimize | Send reminder email to non-openers | 30 min |
| **Day 6** | 🔵 Analyze | Full review: revenue, orders, ads, emails | 1 hr |
| **Day 7** | 🔵 Decide | Scale winners, kill losers, plan next week | 1 hr |

---

## 🔁 Recurring Tasks

- [ ] **Daily:** check Stripe Dashboard for new sales + Stripe email notifications
- [ ] **Weekly:** respond to support emails within 24h, check refund requests
- [ ] **Monthly:** back up `downloads/` folder to cloud storage, review ad spend
- [ ] **Quarterly:** rotate API keys, review product-market fit, refresh top-of-funnel creative

---

## 🚨 Emergency Rollback

If something goes wrong on Day 1:

1. **Vercel:** go to Deployments → click previous successful deploy → "Promote to Production" (30s rollback)
2. **Netlify:** fallback deploy ready (see Step 4)
3. **Stripe:** disable Payment Link in Dashboard (instant)
4. **Email:** send apology email via your ESP, offer refund
5. **Facebook Ads:** pause all ad sets (1 click)

---

**Status:** ✅ Completed · ⏳ Remaining · 🔴 Critical · 🟡 Important · 🟢 Monitor · 🔵 Analyze

Last updated: 2026-06-10
