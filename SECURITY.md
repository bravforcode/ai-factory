# 🔒 SECURITY.md — Key Handling & Incident Response

> **TL;DR:** ถ้า key หลุด → revoke ทันที, ตั้งใหม่, audit logs

---

## 🛑 Live Stripe Key Was Exposed — IMMEDIATE ACTION REQUIRED

**What happened:**
- ใน session นี้ ผู้ใช้ paste `sk_live_51Swp...XXXXX` key (full key redacted) ในแชท
- แชทอาจถูก log ใน:
  - Conversation history (เก็บใน model provider's database)
  - OpenCode telemetry
  - ทุก node ใน supply chain (LLM provider, hosting)
- **Key นี้ถือว่า public แล้ว — แม้ provider จะ claim "encrypted"**

**Action (ภายใน 5 นาที):**

1. **Revoke old live key:**
   - ไป https://dashboard.stripe.com/apikeys
   - คลิก "Roll" ที่ key ที่เพิ่ง paste (full key: `sk_live_51Swp...REDACTED`)
   - คลิก "Roll" ที่ publishable key ด้วย
   - **ห้าม reuse — สร้าง key ใหม่**

2. **ตรวจ Stripe logs:**
   - https://dashboard.stripe.com/logs
   - Filter: `last 7 days`
   - ดูว่ามี API call แปลกๆ ไหม (charge, refund, customer create)
   - ถ้าเจอ → contact Stripe support ทันที

3. **Audit GitHub (ถ้า key เคยถูก commit ใน repo เก่า):**
   ```bash
   cd C:\Users\menum\graxia-os-funnel
   git log --all -p | rg "sk_live|pk_live|whsec_" --color=always
   ```
   - ถ้าเจอ → ใช้ `git filter-repo` ลบ
   - **Rotate GitHub PAT** (key เก่าที่เคยหลุด: `ghp_HSC...REDACTED`)
   - https://github.com/settings/tokens → Revoke

4. **ตั้ง key ใหม่ใน env var (ไม่ paste ในแชท):**
   ```powershell
   # PowerShell
   $env:STRIPE_SECRET_KEY = "sk_live_NEW_KEY_HERE"
   $env:VERCEL_TOKEN = "NEW_TOKEN"
   ```
   ```bash
   # Bash
   export STRIPE_SECRET_KEY="sk_live_NEW_KEY"
   export VERCEL_TOKEN="NEW_TOKEN"
   ```

5. **Verify deployment:**
   - ใช้ deploy-and-test.ps1 — script ใช้ env var เท่านั้น
   - ดู log ว่า Stripe API call ใช้ key ใหม่

---

## 🎯 Best Practices — Going Forward

### ❌ ห้ามทำ
- Paste API key ในแชท/email/Slack/Discord
- Commit `.env` file (verify `.gitignore`)
- เก็บ key ใน code (frontend โดยเฉพาะ)
- Share key กับ contractor/freelancer (สร้าง restricted key แทน)
- ใช้ key เดียวกัน dev/staging/production

### ✅ ควรทำ
- ใช้ environment variable (env var)
- ใช้ secret manager (Vercel Encrypted Env, AWS Secrets Manager, 1Password CLI)
- Rotate keys ทุก 90 วัน
- ใช้ restricted key (read-only, write-only) ตาม use case
- Audit log ทุก key ที่มี

### 🔐 Vercel Encrypted Env (แนะนำ)
```powershell
# ตั้ง key ใน Vercel project (เข้ารหัส, ไม่ public)
vercel env add STRIPE_SECRET_KEY production
# paste key
# ตอน deploy, script อ่านจาก Vercel env แทน
```

### 🔑 Restricted Stripe Keys
- ไป https://dashboard.stripe.com/apikeys
- สร้าง key ใหม่
- Resource: "Payment Links: Write", "Products: Write", "Prices: Write"
- **ไม่ให้**: "All resources" (over-privileged)

---

## 📋 Incident Response Checklist

เมื่อ key หลุด (ทุกครั้ง):

- [ ] Revoke key ทันที (< 5 นาที)
- [ ] ตรวจ audit log (Stripe, GitHub, Vercel)
- [ ] ตรวจว่ามี unauthorized charge/customer ไหม
- [ ] สร้าง key ใหม่ + ตั้ง env var
- [ ] Verify ใหม่ทำงาน (test mode)
- [ ] Notify stakeholders (ถ้า production impact)
- [ ] ตั้ง calendar reminder rotate ทุก 90 วัน
- [ ] Postmortem: ทำไม key หลุด? ป้องกันยังไง?

---

## 🔍 Vercel Token Security

ถ้า Vercel token หลุด:
1. https://vercel.com/account/tokens → Revoke
2. สร้างใหม่ (scope: Full Account หรือ limited)
3. Audit deploy history (https://vercel.com/[team]/[project]/deployments)
4. ตั้ง env var ใหม่

---

## 🆘 Emergency Contacts

- **Stripe support:** https://support.stripe.com (chat 24/7)
- **GitHub support:** https://support.github.com
- **Vercel support:** https://vercel.com/support

ถ้าเจอ fraud/charge แปลกๆ:
- Stripe: dispute แจ้งใน 7 วัน
- Audit log: filter `payment_intent.succeeded` ดู pattern

---

**Last updated:** 2026-06-05 · **Maintained by:** Ai Factory
