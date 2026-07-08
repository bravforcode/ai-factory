# n8n SME Workflow Pack
**5 Production-Ready n8n Workflows สำหรับ SME ไทย — Import แล้วใช้ได้เลย**

> 📦 Pack นี้มาพร้อมกับ **AI Automation Workflow Cheatsheet** (product #5)  
> 🎯 เป้าหมาย: ลดงานซ้ำ ๆ 15+ ชั่วโมง/สัปดาห์ แทนการจ้าง VA 15,000 บาท/เดือน

---

## สารบัญ Workflow

| # | Workflow | ใช้กับ | เวลาที่ประหยัด/สัปดาห์ |
|---|---|---|---|
| 01 | [LINE OA Auto-Reply + Ticket Routing](#01-line) | ร้านค้า/ร้านอาหาร/คลินิก | 5-8 ชม. |
| 02 | [Invoice OCR → Google Sheets → LINE](#02-invoice) | บริษัท/ร้านค้า | 6-10 ชม. |
| 03 | [Daily Report (POS → AI → Email/Slack)](#03-report) | ร้านอาหาร/คาเฟ่/รีเทล | 2-3 ชม. |
| 04 | [Facebook Lead Enrichment + Scoring](#04-lead) | เอเจนซี่/ทีมขาย | 4-6 ชม. |
| 05 | [Blog to 30 Social Posts](#05-content) | Content creator/SME | 8-12 ชม. |

**รวม:** 25-39 ชั่วโมง/สัปดาห์ → ประหยัดเงิน 25,000-40,000 บาท/เดือน (คิดที่ 1,000 บาท/ชม.)

---

## Quick Start (5 นาที)

### Prerequisites
- n8n installed (self-hosted หรือ cloud)
  - Self-hosted: `docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n`
  - Cloud: https://app.n8n.cloud (free trial 14 วัน)
- Accounts: OpenAI (API key), Google (Sheets), LINE OA, Slack
- งบประมาณ: ~600-2,000 บาท/เดือน (ขึ้นกับ usage)

### Import Workflow (3 ขั้นตอน)

1. **เปิด n8n** → คลิก "Workflows" ที่ sidebar
2. **คลิก "Import from File"** (หรือ `Ctrl/Cmd + I`)
3. **เลือกไฟล์ .json** จาก folder นี้ → คลิก Import

✅ Workflow จะปรากฏในรายการ — ยังไม่ activate

### Configure Credentials (5 นาที)

ก่อน activate ต้องตั้ง credentials ที่จำเป็น:

| Workflow | Required Credentials |
|---|---|
| 01 LINE OA | LINE Channel Access Token, OpenAI API Key, Google Sheets OAuth, Slack Webhook |
| 02 Invoice OCR | Google Vision API Key, OpenAI API Key, Google Sheets, LINE |
| 03 Daily Report | POS API, OpenAI API Key, Email SMTP, Slack Webhook |
| 04 FB Lead | Facebook Page Token, Apollo API, OpenAI, HubSpot Token, Slack, Email |
| 05 Content | Blog RSS URL, OpenAI API Key, Airtable, Buffer |

**วิธีตั้ง credentials ใน n8n:**
1. ไปที่ Settings → Credentials
2. คลิก "Add Credential" → เลือก type
3. กรอก API key / token
4. คลิก "Test" → ถ้า OK → "Save"

**วิธีตั้ง Environment Variables (สำหรับ JSON references):**
1. ไปที่ Settings → Variables
2. เพิ่ม: `OPENAI_API_KEY`, `LINE_CHANNEL_ACCESS_TOKEN`, `SPREADSHEET_ID`, etc.
3. ใน workflow ใช้ `{{ $env.VARIABLE_NAME }}`

### Test & Activate (2 นาที)

1. เปิด workflow ที่ import มา
2. คลิก "Execute Workflow" (มุมขวาล่าง) เพื่อทดสอบ
3. ตรวจสอบ output ในแต่ละ node (คลิกที่ node)
4. ถ้า OK → toggle "Active" ที่มุมขวาบน → workflow จะทำงานอัตโนมัติ

---

<a id="01-line"></a>
## 01 - LINE OA Auto-Reply + Ticket Routing

### Flow Diagram
```
[LINE OA] → [Webhook] → [Has Events?] → [AI Classify] → [Switch] 
                                                            ├─ product → [Reply] → [Log Sheets]
                                                            ├─ order → [Reply] → [Log Sheets]
                                                            ├─ complaint → [Reply] → [Log] → [Slack Alert]
                                                            └─ other → [Reply] → [Log]
```

### Setup
- **LINE OA Channel:** สร้างที่ https://developers.line.biz/console/
- **Webhook URL:** copy จาก n8n webhook node → ใส่ใน LINE Console
- **OpenAI:** ใช้ gpt-4o-mini (ถูก + เร็ว)
- **Google Sheets:** สร้าง sheet "LINE_Logs" ใน Spreadsheet

### Customize
- เปลี่ยน AI prompt ใน node "AI Classify Intent" → เพิ่ม intent อื่น ๆ
- เปลี่ยน switch routing → เพิ่มเงื่อนไข
- เปลี่ยน Slack channel → แก้ `#urgent-customer`

### Cost
- LINE OA: free (official account) / 5,000 บาท/เดือน (verified)
- OpenAI gpt-4o-mini: ~600 บาท/เดือน (1,000 messages)
- Google Sheets: free
- n8n self-hosted: ~400 บาท/เดือน (VPS)

**Total: ~1,000 บาท/เดือน**

---

<a id="02-invoice"></a>
## 02 - Invoice OCR to Google Sheets

### Flow Diagram
```
[LINE/Webhook] → [Download Image] → [Google Vision OCR] → [GPT-4 Extract] 
                                                                ↓
                                                      [Save to Sheets] → [Notify LINE]
```

### Setup
- **Google Cloud Vision:** Enable API → สร้าง API Key
- **Google Sheets:** สร้าง sheet "Invoices" พร้อม columns
- **LINE:** ใช้ Push API แทน Reply (ส่งหา admin โดยตรง)

### Customize
- เพิ่ม validation (ถ้า total > X บาท → ต้องอนุมัติ)
- เพิ่ม OCR ภาษาอื่น (Google Vision รองรับ 50+ ภาษา)
- เปลี่ยน GPT-4 → ใช้ Claude หรือ Gemini ก็ได้

### Cost
- Google Vision: ~$1.50/1,000 images ≈ 50 บาท
- OpenAI GPT-4o: ~800 บาท/เดือน (500 invoices)
- Google Sheets: free
- LINE Push: free

**Total: ~1,200 บาท/เดือน** (ที่ 500 invoices/เดือน)

---

<a id="03-report"></a>
## 03 - Daily Report POS to Email & Slack

### Flow Diagram
```
[CRON 8am] → [Fetch POS] → [Aggregate] → [AI Summary] → [Email] 
                                                       └─ [Slack]
```

### Setup
- **POS API:** ต้องมี API endpoint ของระบบ POS (REST API)
- **Email SMTP:** Gmail App Password / SendGrid / Mailgun
- **Slack:** สร้าง Incoming Webhook

### Customize
- เปลี่ยนเวลา trigger → CRON expression
- เพิ่ม comparison (เทียบกับสัปดาห์ก่อน)
- เพิ่ม chart ใน email (PNG จาก QuickChart.io)

### Cost
- OpenAI gpt-4o-mini: ~200 บาท/เดือน
- Email: free (Gmail) / $15/เดือน (SendGrid)
- Slack: free tier

**Total: ~400 บาท/เดือน**

---

<a id="04-lead"></a>
## 04 - Facebook Lead Enrichment + Scoring

### Flow Diagram
```
[FB Lead Ad] → [Webhook] → [Get Lead] → [Apollo Enrich] → [AI Score] 
                                                            ↓
                                                       [Switch]
                                                            ├─ hot → [HubSpot] + [Slack]
                                                            ├─ warm → [Email Auto-Reply]
                                                            └─ cold → [Email Auto-Reply]
```

### Setup
- **Facebook Lead Ads:** เปิด Lead Ads ใน Ads Manager
- **Apollo.io:** API key + ตั้ง budget
- **HubSpot:** Free CRM + Private App Token
- **Slack:** Webhook สำหรับ #hot-leads

### Customize
- เปลี่ยน scoring criteria → ปรับ prompt
- เพิ่ม HubSpot workflow (assign sales rep)
- เพิ่ม SMS notification (Twilio)

### Cost
- Facebook Lead Ads: free (จ่ายแค่ค่า impression)
- Apollo.io: 49 USD/mo ≈ 1,700 บาท/เดือน (basic)
- OpenAI: ~200 บาท/เดือน
- HubSpot: free (basic CRM)

**Total: ~2,000 บาท/เดือน**

---

<a id="05-content"></a>
## 05 - Blog to 30 Social Posts

### Flow Diagram
```
[RSS Trigger] → [Fetch Article] → [GPT-4 Generate 30] → [Split by Platform] 
                                                              ↓
                                                    [Save Airtable] → [Schedule Buffer]
```

### Setup
- **Blog RSS:** ต้องมี RSS feed (`/feed` หรือ `/rss.xml`)
- **Airtable:** สร้าง base "Content Calendar"
- **Buffer:** Pro plan 6 USD/mo ≈ 200 บาท/เดือน

### Customize
- เปลี่ยนจำนวนโพสต์ (10/20/30/50)
- เปลี่ยน platforms เพิ่ม (TikTok, YouTube Shorts)
- เพิ่ม image generation (DALL-E 3 / Midjourney)

### Cost
- OpenAI GPT-4o: ~800 บาท/เดือน (3 articles)
- Buffer: 200 บาท/เดือน
- Airtable: free tier

**Total: ~1,000 บาท/เดือน** (ที่ 3 บทความ/เดือน)

---

## Deployment Options

### Option A: Self-Hosted (ถูกสุด)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Run n8n
docker run -d --restart unless-stopped \
  --name n8n \
  -p 5678:5678 \
  -e N8N_HOST=yourdomain.com \
  -e WEBHOOK_URL=https://yourdomain.com/ \
  -v n8n_data:/home/node/.n8n \
  n8nio/n8n

# Use reverse proxy (nginx/caddy)
# Add SSL with Let's Encrypt
```

**ค่าใช้จ่าย:** VPS 4GB RAM ≈ 400-600 บาท/เดือน (DigitalOcean, Hetzner, Vultr)

### Option B: n8n Cloud (ง่ายสุด)
- ไปที่ https://app.n8n.cloud
- สมัคร Starter plan 20 EUR/mo ≈ 800 บาท/เดือน
- ไม่ต้องจัดการ infrastructure
- ได้ 2,500 workflow executions/เดือน

### Option C: Railway (กลาง ๆ)
- ไปที่ https://railway.app
- Deploy จาก GitHub repo
- ใช้ n8n docker image
- เริ่มต้น $5/mo ≈ 175 บาท/เดือน

---

## Troubleshooting

### Workflow ไม่ทำงาน
1. ตรวจสอบ "Active" toggle (ต้องเปิด)
2. ดู Executions tab → มี error อะไร
3. ตรวจสอบ credentials (token หมดอายุ?)
4. ตรวจสอบ webhook URL (ตรงกับ LINE/FB ที่ตั้งไว้ไหม)

### AI ให้ผลผิดพลาด
1. ปรับ temperature ใน OpenAI node (0 = แม่น, 1 = สร้างสรรค์)
2. เพิ่ม few-shot examples ใน prompt
3. เปลี่ยน model (gpt-4o > gpt-4o-mini > gpt-3.5)
4. เพิ่ม JSON schema validation

### ค่าใช้จ่ายเกิน budget
1. ใช้ gpt-4o-mini แทน gpt-4o (ประหยัด 95%)
2. Cache results (ไม่เรียก AI ซ้ำถ้าข้อมูลเหมือนเดิม)
3. Self-host n8n แทนใช้ cloud
4. ลด trigger frequency (เช่น ทุก 2 ชม. แทนทุก 30 นาที)

### Performance ช้า
1. Self-host ใกล้ผู้ใช้ (Singapore region สำหรับ TH)
2. เพิ่ม RAM (อย่างน้อย 4GB)
3. ใช้ PostgreSQL แทน SQLite
4. ตั้ง worker mode (queue)

---

## Advanced: เพิ่ม Workflow เอง

### ใช้ AI ช่วยเขียน Workflow
Prompt ที่แนะนำ:
```
ฉันต้องการ n8n workflow ที่:
- Trigger: [เมื่อมี event อะไร]
- Process: [ทำอะไรกับข้อมูล]
- Output: [ส่งไปที่ไหน]

ช่วยสร้าง JSON สำหรับ n8n import พร้อม:
1. Node ที่จำเป็น
2. Credentials ที่ต้องตั้ง
3. Error handling
4. Logging
```

### เชื่อมต่อ Service อื่น ๆ
n8n มี 400+ integrations ให้เชื่อมต่อ:
- Notion, Airtable, Google Sheets, Excel
- LINE, Telegram, WhatsApp, Discord, Slack
- Salesforce, HubSpot, Pipedrive
- Stripe, PayPal, PromptPay
- MySQL, PostgreSQL, MongoDB
- AWS S3, Google Cloud Storage

ดูเพิ่ม: https://n8n.io/integrations/

---

## Support & Updates

📧 Email: support@aifactory.co  
💬 Facebook Group: "n8n Thailand"  
📚 Docs: https://docs.n8n.io  
🔄 Updates: ฟรีตลอดชีพ — subscribe email ของเรา

---

**License:** สำหรับผู้ซื้อ license 1 คน/1 บริษัท  
ห้าม redistribute / resell / เผยแพร่ต่อ

**Made with ❤️ for Thai SME community — มิถุนายน 2026**
