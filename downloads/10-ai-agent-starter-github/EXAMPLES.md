# Examples — 3 ตัวอย่างการใช้งานจริง
**ดู AI Agent ทำงานจริง — expected output + เวลา + cost**

---

## Example 1: Thai Customer Service Bot (LINE OA)

**Scenario:** ร้านอาหารรับออเดอร์ผ่าน LINE — agent ตอบคำถาม + ตรวจสอบออเดอร์ + ส่งต่อเจ้าหน้าที่

### Setup
```bash
# 1. ใช้ system prompt สำหรับ Thai CS
python agent_loop.py --system prompts/system-prompt.md

# 2. ตั้ง provider
# ใน .env:
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
```

### Conversation Trace

```
You: สวัสดีค่ะ ร้านเปิดกี่โมงคะ

[Agent] === Iteration 1/10 ===
[Agent] Tool call: (none, final answer)
Agent: สวัสดีค่ะ ร้านเปิดทุกวัน 10:00-22:00 น. ค่ะ 😊 มีอะไรให้ช่วยไหมคะ?

You: อยากสั่งข้าวผัดกุ้ง 1 จาน ส่งที่ห้อง 305

[Agent] === Iteration 1/10 ===
[Agent] Tool call: (none, final answer)
Agent: รับทราบค่ะ ข้าวผัดกุ้ง 1 จาน ส่งห้อง 305 ราคา 120 บาท
รวมเป็นเงิน 120 บาท ชำระเงินสดปลายทางหรือโอนก่อนคะ?

You: โอนค่ะ เลขบัญชีอะไร

[Agent] === Iteration 1/10 ===
[Agent] Tool call: (none, final answer)
Agent: เลขบัญชี: 123-4-56789-0 ธนาคารกสิกรไทย
ชื่อบัญชี: บริษัท ABC จำกัด
เมื่อโอนแล้ว ส่งสลิปมาได้เลยค่ะ 🙏

You: ส่งสลิปแล้วค่ะ (รูปภาพแนบ)

[Agent] === Iteration 1/10 ===
[Agent] Tool call: (none, final answer)
Agent: ขอบคุณค่ะ ได้รับสลิปเรียบร้อย
ออเดอร์ #A-12345 กำลังเตรียมอาหารค่ะ คาดส่งถึง 12:30 น. ค่ะ 🚀
```

### Stats
- **Iterations:** 1 per message (no tools needed)
- **Tokens:** ~400 in + ~150 out = 550 tokens
- **Cost:** ~$0.0001 (0.004 บาท) per message
- **Latency:** 1-2 วินาที
- **Tools used:** 0

---

## Example 2: Research Assistant (Web Search + Calculator)

**Scenario:** นักลงทุนถามข้อมูลหุ้น + คำนวณผลตอบแทน

### Conversation Trace

```
You: ราคาหุ้น NVDA ตอนนี้เท่าไหร่ แล้วถ้าซื้อ 100 หุ้นเมื่อ 6 เดือนที่แล้วที่ราคา 400 ดอลลาร์ ตอนนี้กำไรเท่าไหร่เป็นเปอร์เซ็นต์

[Agent] === Iteration 1/10 ===
[Agent] Tool call: web_search({"query": "NVDA stock price today", "num_results": 3})
[Agent] Tool result: {"results": [{"title": "NVIDIA Corp (NVDA) - Yahoo Finance", "snippet": "NVDA current price: $924.79 +2.5%", "url": "..."}]}

[Agent] === Iteration 2/10 ===
[Agent] Tool call: calculator({"expression": "(924.79 - 400) / 400 * 100"})
[Agent] Tool result: 131.1975

[Agent] === Iteration 3/10 ===
[Agent] Tool call: (none, final answer)
Agent: ราคาหุ้น NVDA ตอนนี้: **$924.79** (ปรับขึ้น +2.5% วันนี้)

ถ้าซื้อ 100 หุ้นที่ $400 = ลงทุน $40,000
ปัจจุบันมูลค่า 100 × $924.79 = $92,479
กำไร = $52,479 หรือ **+131.2%** ใน 6 เดือน 🎉
```

### Stats
- **Iterations:** 3 (2 tool calls + 1 final)
- **Tokens:** ~1,200 in + ~250 out = 1,450 tokens
- **Cost:** ~$0.0003 (0.01 บาท)
- **Latency:** 4-6 วินาที
- **Tools used:** web_search, calculator

---

## Example 3: Multi-Step Data Pipeline (Production-grade)

**Scenario:** Marketing analyst ต้องการข้อมูลคู่แข่ง + บันทึกลงไฟล์

### Custom Tools เพิ่ม
```python
# tools.py (เพิ่ม)
def scrape_competitor_prices(url: str) -> str:
    """Scrape pricing page."""
    import requests
    from bs4 import BeautifulSoup
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")
    prices = []
    for elem in soup.select(".price, [data-price]"):
        text = elem.get_text(strip=True)
        if text:
            prices.append(text)
    return json.dumps({"url": url, "prices": prices[:20]}, ensure_ascii=False)

def write_markdown(path: str, content: str) -> str:
    """Write content to markdown file."""
    import os
    full_path = os.path.abspath(path)
    if not full_path.startswith(os.getcwd()):
        return "Error: Access denied"
    os.makedirs(os.path.dirname(full_path) or ".", exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"Wrote {len(content)} chars to {path}"
```

### Conversation Trace

```
You: ช่วย research ราคา SaaS 3 ตัวนี้ในตลาด CRM: Salesforce, HubSpot, Zoho
แล้วสรุปเป็นตารางเปรียบเทียบ บันทึกเป็นไฟล์ competitor-analysis.md

[Agent] === Iteration 1/10 ===
[Agent] Tool call: web_search({"query": "Salesforce pricing 2026 plans"})
[Agent] Tool result: {"results": [{"title": "Salesforce Pricing", "snippet": "Starter: $25/user/mo, Pro: $75/user/mo, Enterprise: $165/user/mo"}]}

[Agent] === Iteration 2/10 ===
[Agent] Tool call: web_search({"query": "HubSpot CRM pricing 2026"})
[Agent] Tool result: {"results": [{"title": "HubSpot Pricing", "snippet": "Free: $0, Starter: $20/mo, Pro: $890/mo"}]}

[Agent] === Iteration 3/10 ===
[Agent] Tool call: web_search({"query": "Zoho CRM pricing 2026"})
[Agent] Tool result: {"results": [{"title": "Zoho Pricing", "snippet": "Free: $0, Standard: $14/user/mo, Professional: $23/user/mo"}]}

[Agent] === Iteration 4/10 ===
[Agent] Tool call: write_markdown({"path": "competitor-analysis.md", "content": "# Competitor Analysis: SaaS CRM 2026\n\n## Pricing\n\n| Vendor | Free | Starter | Pro | Enterprise |\n|---|---|---|---|---|\n| Salesforce | ❌ | $25/user/mo | $75/user/mo | $165/user/mo |\n| HubSpot | ✅ | $20/mo | $890/mo | Custom |\n| Zoho | ✅ | $14/user/mo | $23/user/mo | $52/user/mo |\n\n## Key Insights\n- HubSpot มี free tier ที่แข็งแกร่ง\n- Salesforce แพงสุด แต่ feature ครบ\n- Zoho ถูกสุด, เหมาะ SME\n\n## Recommendations\n- Target: SME ขนาด 5-50 คน → แนะนำ Zoho\n- Target: Enterprise → แนะนำ Salesforce"})
[Agent] Tool result: "Wrote 543 chars to competitor-analysis.md"

[Agent] === Iteration 5/10 ===
[Agent] Tool call: (none, final answer)
Agent: เสร็จเรียบร้อยค่ะ ✅

ได้ข้อมูลราคา CRM 3 ตัวหลัก (Salesforce, HubSpot, Zoho) 
และบันทึกเป็น `competitor-analysis.md` แล้วค่ะ

**สรุป key insights:**
- **HubSpot** — free tier แข็งแกร่ง, Pro plan ขึ้นไปแพง
- **Salesforce** — แพงที่สุด ($25-$165/user/mo) แต่ feature ครบ
- **Zoho** — ถูกสุด, เหมาะ SME

ต้องการให้ทำ analysis เพิ่ม (เช่น feature comparison, market share) ไหมคะ?
```

### Stats
- **Iterations:** 5 (4 tool calls + 1 final)
- **Tokens:** ~3,500 in + ~600 out = 4,100 tokens
- **Cost:** ~$0.0008 (0.03 บาท)
- **Latency:** 15-20 วินาที
- **Tools used:** web_search × 3, write_markdown × 1

---

## Performance Comparison

| Example | Iterations | Tools | Tokens | Cost (THB) | Time |
|---|---|---|---|---|---|
| 1. CS Bot | 1 | 0 | 550 | 0.004 | 1-2s |
| 2. Research | 3 | 2 | 1,450 | 0.01 | 4-6s |
| 3. Pipeline | 5 | 4 | 4,100 | 0.03 | 15-20s |

**Insight:** แม้งานซับซ้อน cost ยังถูกมาก (ต่ำกว่า 0.05 บาท/ครั้ง)

---

## Cost Calculator (1 เดือน)

สมมติใช้งาน 1,000 messages/วัน:

| Scenario | Messages | Cost/Message | Daily | Monthly |
|---|---|---|---|---|
| Simple Q&A | 1,000 | 0.004 บาท | 4 บาท | 120 บาท |
| Research | 1,000 | 0.01 บาท | 10 บาท | 300 บาท |
| Multi-step | 1,000 | 0.03 บาท | 30 บาท | 900 บาท |
| **Mixed (70/20/10)** | 1,000 | ~0.01 บาท | **8.5 บาท** | **255 บาท** |

+ hosting $5/mo (~175 บาท) = **Total ~430 บาท/เดือน**

**เทียบกับ:** จ้าง VA ตอบ LINE = 15,000 บาท/เดือน  
**ประหยัด:** 14,570 บาท/เดือน (97%)

---

## Customization Tips

### เพิ่ม Domain-Specific Tool
```python
def check_order_status(order_id: str) -> str:
    """Check order in your database."""
    # Connect to your DB
    # Return order info
    ...

# Register ใน TOOL_REGISTRY
TOOL_REGISTRY["check_order_status"] = {
    "function": check_order_status,
    "schema": {...}
}
```

### ปรับ System Prompt
ดูตัวอย่างใน `prompts/system-prompt.md` — แก้ role/personality/rules

### เพิ่ม RAG (Memory ขั้นสูง)
```python
# memory.py - เพิ่ม vector memory
from sentence_transformers import SentenceTransformer
import faiss

class VectorMemory:
    def __init__(self):
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.index = faiss.IndexFlatL2(384)
        self.docs = []
    
    def add(self, text: str):
        emb = self.encoder.encode([text])
        self.index.add(emb)
        self.docs.append(text)
    
    def search(self, query: str, k: int = 3):
        emb = self.encoder.encode([query])
        _, idx = self.index.search(emb, k)
        return [self.docs[i] for i in idx[0]]
```

---

## Try It Yourself

```bash
# 1. Setup
git clone <repo>
cd code
pip install -r requirements.txt
cp .env.example .env
# ใส่ OPENAI_API_KEY

# 2. Run
python agent_loop.py

# 3. ลองพิมพ์
You: หาข้อมูลน้ำมันวันนี้
You: คำนวณ 100 * 1.07
You: อ่านไฟล์ requirements.txt
You: exit
```

---

**มีคำถาม? เปิด issue ที่ GitHub หรือติดต่อ support@aifactory.co 🚀**
