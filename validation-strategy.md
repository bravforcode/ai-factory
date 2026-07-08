# Validation Strategy: Product #9 (Personal Finance Tracker THB)

**Goal:** prove there's paying demand before building the product
**Time:** 3-5 days
**Cost:** 100 THB total
**For:** Thai first-time entrepreneur, limited time/money, wants signal not vibes

---

## Why Validate First

**Sunk cost is the enemy.** You will spend 5-10 hours building a Google Sheet template. That is not "free time" — that is one weekend you will never get back. If the market does not want this product, those hours are gone. Worse, you will keep polishing it for another 10 hours because "it just needs one more tweak." Validation first kills this loop.

**"Sounds good" is not "people will pay."** You think 149 THB is cheap. You would buy it. Your friend said "น่าสนใจ." None of this matters. The only thing that matters: did a stranger give you money or email after seeing a real ad? Thai consumers say yes politely in DMs and never open their wallet. Test the wallet, not the conversation.

**Cheap failure is the whole game.** 100 THB and 3-5 days. That is the price of learning whether Product #9 has legs. If yes — you build with confidence and a waiting list. If no — you move to Product #4 or Product #7 in the same week. You are not validating one product, you are validating the *system* of picking winners from a list of 10.

---

## 3 Validation Methods (pick one, do it well)

**Pick ONE method. Do not run all three. Doing one well beats doing three half-assed.**

Recommendation: **Method A** for first-timers (easiest, lowest risk). **Method B** if you already have Stripe and want the strongest signal. **Method C** if you have zero ad budget and active FB accounts.

---

### Method A: Waitlist Landing Page (FREE, 1 day)

**Concept:** Create a 1-page website describing the product with a "Get notified when it launches" email signup. Drive 100-200 targeted visitors from a 50 THB FB ad. Measure signup rate.

**Why this works:** Email signup is the cheapest commitment you can ask for. It filters out "ก็น่าสนใจนะ" people. If 5%+ of real ad visitors leave their email, you have demand. If under 2%, you do not.

**Steps:**

1. Copy `C:\Users\menum\sales_pages\09-finance-tracker-thb.html` → save as `waitlist-finance.html`
2. Change the CTA button from "ซื้อ 149 บาท" to "แจ้งเตือนเมื่อเปิดขาย"
3. Add a simple email signup form:
   - Option 1: **Tally.so** (free, no signup wall, embed via iframe — recommended)
   - Option 2: **Mailchimp** free tier (500 contacts, embed form, more setup)
   - Option 3: **Google Forms** (ugly but works, link out instead of embed)
4. Deploy to **Netlify**: drag the HTML file onto netlify.com/drop, get a `*.netlify.app` URL in 2 minutes. No Git, no build, no domain needed.
5. Create Facebook ad (copy below) in **Meta Ads Manager**
6. Run 3 days, 50 THB total budget (≈16-17 THB/day)
7. Measure: page views (Netlify analytics or UTM) / email signups (Tally/Mailchimp dashboard)

**Pass criteria:** >5% email signup rate AND >20 signups
**Kill criteria:** <2% signup rate OR <10 signups after spending full 50 THB

**Ad copy (use this verbatim, do not rewrite):**
> คนไทย 80% ไม่เคย track การเงิน — กำลังทำ Google Sheet ฟรี/ถูก ที่รองรับภาษีไทย (หัก ณ ที่จ่าย, ประกันสังคม) — สนใจไหม? กดแจ้งเตือน

**Targeting:**
- Location: Thailand
- Age: 25-45
- Interests: "การเงินส่วนบุคคล", "เงินเดือน", "ภาษี", "Personal finance"
- Placements: Facebook + Instagram feed (let Meta auto-optimize)
- Schedule: 3 days, daily budget 16-17 THB

**Creative:** Use a screenshot of the product HTML page itself. Do not design anything. Real > polished for validation.

---

### Method B: Pre-order with Fake Door (100 THB, 3 days)

**Concept:** Run the actual product landing page with Stripe in test mode. Charge 1 THB for pre-order. If 10+ people pay 1 THB → strong signal of real demand.

**Why this is the strongest signal:** People paying ANY amount (even 1 THB) is 10x stronger than an email signup. Money talks. Email is a promise, payment is proof.

**Steps:**

1. Use existing `09-finance-tracker-thb.html` as-is (the buy button is already there)
2. Setup Stripe account (Thailand supported, ~15 min):
   - Create product: "Personal Finance Tracker THB"
   - Price: 1 THB (yes, one baht)
   - Enable "Test mode" first to verify the flow
   - Switch to live mode when ready
   - Use **Stripe Payment Link** (no coding needed, just a URL)
3. Replace the "ซื้อ 149 บาท" button href with the Payment Link URL
4. Drive 200 visitors via 100 THB FB ad (≈33 THB/day for 3 days)
5. Measure conversion: visits → 1 THB payments (Stripe dashboard)

**Pass criteria:** >3% pre-order conversion (6+ paying customers from 200 visitors)
**Kill criteria:** <1% conversion (under 2 paying customers)

**Ad copy (use this verbatim):**
> Pre-order 1 บาท — Personal Finance Tracker THB (Google Sheet รองรับภาษีไทย) — เปิดขายจริงเร็วๆ นี้

**Targeting:** Same as Method A

**Warning:** Stripe Thailand has a 2-3 day account review for live payments. If you need results in 3 days, use Method A or pre-apply for Stripe now.

---

### Method C: Community Survey (0 THB, 2 days)

**Concept:** Post in 5 Thai Facebook groups asking: "Would you buy X for 149 THB? How much would you actually pay?" Count "yes" responses. DM the "yes" people.

**Why this is weakest but cheapest:** Zero ad spend, but high false-positive rate. Thai FB group replies are noisy. People say "สนใจ" out of politeness. Use this only if you have no ad budget and want qualitative color on pain points.

**Steps:**

1. Write the post (copy below)
2. Post in these 5 groups (one post per group, do not spam):
   - "การเงินส่วนบุคคล" (100k+ members)
   - "Freelance Thailand" (50k+)
   - "คนทำงานออฟฟิศ" (search Thai office worker groups, 20k+)
   - "นักเรียน/นักศึกษา การเงิน" (student finance groups)
   - "Excel/Google Sheet ขั้นสูง" (template/spreadsheet users)
3. Wait 48 hours. Do not engage in arguments. Count "yes," "ซื้อ," "สนใจ," "น่าสนใจ" type replies.
4. DM everyone who said yes (max 30 DMs/day or FB rate-limits you). Ask: "ถ้าเปิดขายจริง 149 บาท จะจ่ายเลยไหมคะ/ครับ?"
5. Count how many say "จ่าย" vs "รอดูก่อน"

**Post copy (use this verbatim):**
> กำลังทำ Google Sheet สำหรับ track การเงินคนไทย — รองรับหัก ณ ที่จ่าย, ประกันสังคม, ภาษี, เงินออม
>
> ถ้าขาย 149 บาท คุณจะซื้อไหม? เหตุผลอะไร?
>
> (ไม่ใช่โฆษณา อยากรู้ pain point จริง)

**Pass criteria:** >50 "yes" type responses across 5 groups, AND >10 of those DMs say "จ่ายแน่นอน"
**Kill criteria:** <10 "yes" responses, OR all DMs say "รอดูก่อน" / "ฟรีดีกว่า"

**Ad copy is not needed for this method.** Distribution is manual via group posting.

---

## Decision Framework: Build vs Kill

After running your chosen method, look at the result and act. No deliberation, no "let me run it one more week."

| Result | Action |
|---|---|
| 50+ email signups (Method A) | **Build it.** You have demand. |
| 20-49 email signups, 3-5% rate (Method A) | **Build it** but keep ad on for 2 more days with 30 THB top-up to confirm. |
| 3%+ pre-order rate (Method B) | **Build it.** Strongest possible signal. |
| 1-3% pre-order rate (Method B) | **Improve copy and re-test** once with fresh ad creative. |
| 50+ "yes" responses AND 10+ DM confirms (Method C) | **Build it.** Qualitative validation passed. |
| 20-49 "yes" responses, mixed DMs (Method C) | **Re-run with Method A** (Method C alone is too noisy). |
| Mixed results (10-30 signups, 1-2% conversion) | **Improve copy and re-test.** Do not build yet. |
| <10 signups OR <1% conversion after full spend | **Kill it.** Pivot to another product. |
| 0 signups / 0 responses / ad rejected | **Kill it.** Even worse signal. |

**Critical mindset:** Killing is winning. You saved 20 hours of building and learned the market does not want THIS product. You have 9 others to test. Every kill is information, not failure.

**Hard rule:** Do not "rebuild" a killed product with different positioning twice. One kill = move on. The market is telling you something.

---

## Budget Breakdown (Method A: most cost-effective)

| Item | Cost |
|---|---|
| Netlify hosting (free tier) | 0 THB |
| Domain (use *.netlify.app subdomain) | 0 THB |
| Tally.so free tier (unlimited forms, 100 submissions/mo) | 0 THB |
| Mailchimp free tier (500 contacts, backup option) | 0 THB |
| Stripe account (no monthly fee, pay-per-transaction) | 0 THB |
| Facebook ad — 3 days, daily 16-17 THB | 50 THB |
| Reserve for top-up if first test is borderline | 50 THB |
| **Total** | **100 THB** |

**Realistic reach:** 50 THB over 3 days in Thailand = ~1,500-3,000 impressions, ~100-250 link clicks, ~80-200 landing page views (after ~20% bounce). That is enough for statistical signal. Do not expect 10,000 views.

**If ad gets rejected:** FB often rejects Thai-language finance ads. Appeal within 24 hours. If still rejected, switch to Instagram-only placement or use a softer landing page (no money mentions in headline).

---

## What Success Looks Like (Day 5)

- 50+ email signups waiting for launch (or 6+ 1-THB pre-orders, or 50+ qualified yes-replies)
- You have a list to sell to on Day 1 of launch — this is your unfair advantage over building blind
- Confidence to spend 5-10 hours building the actual Google Sheet
- Zero regret if you kill it (you spent 100 THB, not 100 hours)

**You are NOT done at Day 5.** Day 5 is the gate. After that you build the product, then you email the list, then you have customers on Day 1 instead of Day 14. That is the whole point of validating first.

---

## What to Do AFTER Validation Passes

Do these in order. Do not skip steps.

1. **Build the Google Sheet (1-2 days)** using `product-09-build-spec.md` if it exists. Keep it simple. MVP = the 4 main tabs: รายรับ, รายจ่าย, ภาษี/หัก ณ ที่จ่าย, สรุปรายเดือน. No fancy dashboards yet.
2. **Update landing page** `09-finance-tracker-thb.html`: change "แจ้งเตือน" CTA back to "ซื้อ 149 บาท"
3. **Setup Stripe Payment Link** (1 hour):
   - Product name: "Personal Finance Tracker THB"
   - Price: 149 THB
   - Copy the Payment Link URL
   - Update the buy button `href` in the HTML
   - Redeploy to Netlify (drag the updated file)
4. **Email the waitlist** (Day 1 of launch): subject "ของมาส่งแล้ว — Personal Finance Tracker THB" + purchase link. This is your first revenue.
5. **Run conversion ads** starting Day 1: target a lookalike audience of your email list (Meta auto-generates from 100+ contacts) or retarget the link-clickers from validation. Budget: 100 THB/day if you have cash, 30 THB/day if you are tight.
6. **Reinvest first 1,000 THB revenue** into more ads. Do not withdraw. Compound.
7. **Repeat with next product from the 10.** Products #4, #5, #7 are the next-best candidates based on typical Thai demand. Validate one while Product #9 is selling.

**Time-to-first-sale target:** Day 7-10 from today.

---

## What to Do AFTER Validation Fails

**This is the section most guides skip. Do not skip it. Failure is the expected outcome ~50% of the time.**

1. **Do not rebuild the same product.** One kill = move on. The market gave you an answer. Respect it.
2. **Check the other 9 products** in `C:\Users\menum\sales_pages\`. List them in a spreadsheet: name, price, target audience, your gut confidence (1-5).
3. **Pick the next 2 candidates** (highest gut confidence + audience size). Run the same validation method (recommend Method A for speed) for each.
4. **Time-box hard:** maximum 2 weeks total validating. If 3 products in a row fail validation, pause and reassess:
   - Is your audience reachable on FB at 50 THB/day?
   - Is your ad copy the problem or the product idea the problem?
   - Are you picking products the market does not care about?
5. **Do not fall in love with any one idea.** The 10 products are experiments, not commitments. You are looking for 2-3 winners, not 1 perfect one.
6. **Track results in a single table:**

| Product | Method | Spend | Signups/Orders | Result | Action |
|---|---|---|---|---|---|
| #9 Finance Tracker | A | 50 THB | X | Pass/Kill | Build/Pivot |
| #? Next | A | 50 THB | X | Pass/Kill | Build/Pivot |
| #? Next | A | 50 THB | X | Pass/Kill | Build/Pivot |

7. **If 3+ products fail:** the common factor is YOU (audience, copy, offer), not the products. Either:
   - Switch platform (TikTok, Line OA, Pantip, YouTube Shorts)
   - Switch audience (B2B freelancers instead of B2C office workers)
   - Switch price point (try 49 THB or 499 THB instead of 149)
   - Or take a 2-week break and study what IS selling in the Thai market right now.

**The real lesson:** 100 THB and 5 days per test × 10 products = 1,000 THB and 50 days to find your first winner. That is a reasonable price for a business that can make 10,000+ THB/month passive. Do not shortcut this.

---

## Quick-Start Checklist (Method A, 1 day)

Print this and tick boxes:

- [ ] Copy `09-finance-tracker-thb.html` → `waitlist-finance.html`
- [ ] Change CTA button text to "แจ้งเตือนเมื่อเปิดขาย"
- [ ] Create Tally.so form (fields: email, optional name)
- [ ] Embed Tally form in HTML (or link button to Tally URL)
- [ ] Drag HTML file to netlify.com/drop → get URL
- [ ] Test on phone: open URL, submit email, confirm Tally received it
- [ ] Open Meta Ads Manager → create campaign → traffic objective
- [ ] Paste ad copy verbatim (do not rewrite)
- [ ] Targeting: Thailand, 25-45, interests listed above
- [ ] Budget: 50 THB total, 3 days
- [ ] Publish ad
- [ ] Day 4: check signups in Tally
- [ ] Day 5: apply decision framework → Build or Kill

**Done. No excuses. Total time: 2-3 hours of actual work spread across 1 day.**

---

## Final Note

You have 10 products. You have 100 THB. You have 5 days. The math is simple: test fast, kill fast, build only winners. The entrepreneur who validates 5 products in a month will beat the one who perfects 1 product in a month, every time.

Start tonight. Deploy the waitlist page before you sleep. Launch the ad tomorrow morning. Read the results on Day 5. Build or pivot. Then go again.
