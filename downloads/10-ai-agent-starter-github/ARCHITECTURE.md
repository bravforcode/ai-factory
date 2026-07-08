# Architecture Deep Dive
**เบื้องหลัง AI Agent — ทำไมถึงทำงานได้**

> 📐 เอกสารนี้สำหรับคนอยากเข้าใจ **ทำไม** ไม่ใช่แค่ **ทำอย่างไร**  
> 🎯 หลังอ่านจบ คุณจะสามารถแก้ไข/ขยาย agent ได้อย่างมั่นใจ

---

## สารบัญ

- [1. Agent Loop (ReAct Pattern)](#1-react)
- [2. Tool Use](#2-tools)
- [3. Memory Architecture](#3-memory)
- [4. Planning & Reasoning](#4-planning)
- [5. Multi-Provider Support](#5-providers)
- [6. Error Handling & Retry](#6-errors)
- [7. Performance & Cost](#7-perf)

---

<a id="1-react"></a>
## 1. Agent Loop (ReAct Pattern)

**ReAct** = **Rea**soning + **Act**ing — สลับกันไปเรื่อย ๆ จนกว่าจะได้คำตอบสุดท้าย

### 1.1 Pseudocode

```python
def agent_loop(user_message, max_iter=10):
    memory.append({"role": "user", "content": user_message})
    
    for iteration in range(max_iter):
        # 1. Reasoning — ให้ LLM คิด
        response = llm.complete(memory + tools_schema)
        
        # 2. Decision — LLM ตอบ: ใช้ tool หรือตอบตรง
        if response.has_tool_call():
            tool_name = response.tool_call.name
            tool_args = response.tool_call.args
            
            # 3. Acting — เรียก tool จริง
            tool_result = tools[tool_name](**tool_args)
            
            # 4. Observation — บันทึกผลลัพธ์
            memory.append({
                "role": "tool",
                "name": tool_name,
                "content": tool_result
            })
        else:
            # 5. Final answer — จบ loop
            memory.append({"role": "assistant", "content": response.text})
            return response.text
    
    # ถ้าเกิน max_iter → force answer
    return "หมดเวลา กรุณาถามใหม่"
```

### 1.2 ตัวอย่างจริง

**Input:** "อากาศวันนี้ที่กรุงเทพเป็นยังไง?"

**Iteration 1:**
```
[Reasoning]
- ผู้ใช้ถามอากาศ → ต้องใช้ web_search
[Action]
- Tool: web_search(query="weather Bangkok today")
[Observation]
- "กรุงเทพ 32°C ฝนตก 60%"
```

**Iteration 2:**
```
[Reasoning]
- ได้ข้อมูลแล้ว → ตอบได้เลย
[Final Answer]
- "วันนี้กรุงเทพอากาศร้อน 32°C มีฝนตก 60% ควรพกร่มด้วยนะครับ"
```

### 1.3 ทำไมต้อง ReAct ไม่ใช่แค่ Chain-of-Thought?

| Pattern | ข้อดี | ข้อเสีย |
|---|---|---|
| **Zero-shot** | เร็ว, ถูก | ตอบผิดบ่อย (fact hallucination) |
| **Chain-of-Thought** | คิดดีขึ้น | ยัง hallucinate ได้ |
| **ReAct** | คิดดี + ใช้ข้อมูลจริง | แพงกว่า (multiple LLM calls) |
| **Reflexion** | เรียนรู้จาก error | ซับซ้อน, ช้ามาก |

**ReAct เป็น sweet spot** — คุณภาพสูง + ราคาสมเหตุสมผล

### 1.4 Max Iterations — ตั้งเท่าไหร่?

- **1-3:** งานง่าย (Q&A, lookup)
- **5-10:** งานกลาง (research, multi-step)
- **10-20:** งานซับซ้อน (planning, multi-tool)
- **>20:** อันตราย — agent อาจ loop ไม่จบ

**ค่า default ของเรา: 10** (ปรับได้ใน `.env`)

---

<a id="2-tools"></a>
## 2. Tool Use

### 2.1 Tool Schema (OpenAI format)

LLM ต้องรู้ว่ามี tool อะไรบ้าง → เราส่ง schema ไปแบบนี้:

```json
{
  "type": "function",
  "function": {
    "name": "web_search",
    "description": "ค้นหาข้อมูลจาก Google — ใช้เมื่อต้องการข้อมูลล่าสุด",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "คำค้นหา (ภาษาไทยหรืออังกฤษก็ได้)"
        },
        "num_results": {
          "type": "integer",
          "description": "จำนวนผลลัพธ์ (default 5)",
          "default": 5
        }
      },
      "required": ["query"]
    }
  }
}
```

**Key points:**
- `description` ต้องชัดเจน — LLM ใช้ตัดสินใจว่าจะเรียก tool นี้เมื่อไหร่
- `parameters` ต้องมี `type` + `description` ครบ
- `required` ระบุว่าตัวไหนจำเป็น

### 2.2 Tool Execution Flow

```python
# 1. LLM ตอบกลับมา
response = {
  "tool_calls": [{
    "id": "call_abc",
    "function": {
      "name": "web_search",
      "arguments": '{"query": "weather Bangkok"}'
    }
  }]
}

# 2. Parse
tool_name = response.tool_calls[0].function.name
tool_args = json.loads(response.tool_calls[0].function.arguments)

# 3. Execute
if tool_name in TOOL_REGISTRY:
    result = TOOL_REGISTRY[tool_name](**tool_args)
else:
    result = f"Error: Tool {tool_name} not found"

# 4. Send back to LLM
messages.append({
    "role": "tool",
    "tool_call_id": "call_abc",
    "content": str(result)
})
```

### 2.3 เพิ่ม Tool ใหม่ — Template

```python
def my_custom_tool(param1: str, param2: int = 10) -> str:
    """
    คำอธิบายสั้น ๆ ว่า tool นี้ทำอะไร
    
    Args:
        param1: คำอธิบาย param 1
        param2: คำอธิบาย param 2 (default 10)
    
    Returns:
        ผลลัพธ์เป็น string
    """
    # Logic here
    result = do_something(param1, param2)
    return f"Result: {result}"

# Register
TOOL_REGISTRY["my_custom_tool"] = {
    "function": my_custom_tool,
    "schema": {
        "type": "function",
        "function": {
            "name": "my_custom_tool",
            "description": "คำอธิบายสำหรับ LLM",
            "parameters": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string", "description": "..."},
                    "param2": {"type": "integer", "description": "...", "default": 10}
                },
                "required": ["param1"]
            }
        }
    }
}
```

**Best practices:**
- ✅ Return `str` เสมอ (LLM อ่าน string ได้ดีที่สุด)
- ✅ Handle errors → return error message เป็น string
- ✅ เขียน description ให้ LLM เข้าใจ → ไม่งั้น LLM ไม่รู้จะเรียกเมื่อไหร่
- ✅ Test ทุก tool ก่อน production

### 2.4 Tool Safety

**⚠️ อันตราย:**
- Tool ที่ลบไฟล์ → ต้องมี confirmation
- Tool ที่ส่งอีเมล → ต้อง rate limit
- Tool ที่เรียก API เสียเงิน → ต้อง cap cost

**Pattern: Sandbox**

```python
def dangerous_tool(path: str) -> str:
    # Whitelist directory
    allowed_dir = "/Users/agent/sandbox/"
    if not path.startswith(allowed_dir):
        return f"Error: Access denied. Only {allowed_dir} allowed"
    
    # Cap file size
    if os.path.getsize(path) > 10_000_000:  # 10MB
        return "Error: File too large"
    
    # Proceed
    with open(path) as f:
        return f.read()
```

---

<a id="3-memory"></a>
## 3. Memory Architecture

### 3.1 Two-Tier Memory

```
┌──────────────────────────────────────┐
│ Short-term (in-RAM, current session) │ ← message list
│ - System prompt                      │
│ - User messages                      │
│ - Assistant messages                 │
│ - Tool calls + results               │
└──────────────────────────────────────┘
              ↕ flush
┌──────────────────────────────────────┐
│ Long-term (disk, persistent)         │ ← memory.json
│ - Conversation history (per user)    │
│ - User preferences                   │
│ - Past tool results                  │
└──────────────────────────────────────┘
```

### 3.2 Short-term (Context Window)

```python
class Memory:
    def __init__(self, system_prompt: str, max_tokens: int = 8000):
        self.messages = [{"role": "system", "content": system_prompt}]
        self.max_tokens = max_tokens
    
    def add(self, role: str, content: str, **kwargs):
        self.messages.append({"role": role, "content": content, **kwargs})
        self._trim()
    
    def _trim(self):
        # ถ้า context ยาวเกิน → ลบข้อความเก่าสุด (ยกเว้น system)
        while self._estimate_tokens() > self.max_tokens:
            if len(self.messages) <= 2:  # system + last user
                break
            self.messages.pop(1)  # remove oldest (after system)
```

**ทำไมต้อง trim?**
- GPT-4o context = 128K tokens
- แต่ input แพง (~$5/1M tokens)
- และ LLM อาจ "ลืม" ข้อความตรงกลาง (Lost-in-the-Middle)

**Token estimation:**
```python
def estimate_tokens(text: str) -> int:
    # Approximate: 1 token ≈ 4 chars (English), 1.5 chars (Thai)
    thai_chars = sum(1 for c in text if 'ก' <= c <= '๛')
    other_chars = len(text) - thai_chars
    return int(thai_chars / 1.5 + other_chars / 4)
```

### 3.3 Long-term (Persistence)

```python
{
  "users": {
    "user_123": {
      "preferences": {
        "language": "th",
        "tone": "casual"
      },
      "history": [
        {"timestamp": "...", "user": "...", "assistant": "..."},
        ...
      ]
    }
  }
}
```

**When to save:**
- ทุกครั้งที่จบ conversation
- หรือทุก ๆ 10 messages (batch save)

**When to load:**
- ตอน user ใหม่เริ่ม session
- หรือทุก ๆ 5 minutes

### 3.4 Vector Memory (RAG — Optional)

สำหรับ agent ที่ต้อง **จำข้อมูลจำนวนมาก**:

```python
# ใช้ FAISS / ChromaDB
from sentence_transformers import SentenceTransformer
import faiss

class VectorMemory:
    def __init__(self):
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.index = faiss.IndexFlatL2(384)
        self.documents = []
    
    def add(self, doc: str):
        embedding = self.encoder.encode([doc])
        self.index.add(embedding)
        self.documents.append(doc)
    
    def search(self, query: str, k: int = 3) -> list[str]:
        embedding = self.encoder.encode([query])
        distances, indices = self.index.search(embedding, k)
        return [self.documents[i] for i in indices[0]]
```

**ตัวอย่างการใช้:**
- User: "เมื่อวานเราคุยเรื่องอะไร"
- Vector search → "คุยเรื่อง..."

---

<a id="4-planning"></a>
## 4. Planning & Reasoning

### 4.1 Chain-of-Thought Prompting

```python
SYSTEM_PROMPT = """คุณเป็น AI agent อัจฉริยะ
เมื่อได้รับคำถาม ให้คิดเป็นขั้นตอน:

Thought: [คิดว่าต้องทำอะไร]
Action: [เลือก tool ที่จะใช้ หรือ "Final Answer" ถ้าพอใจแล้ว]
Action Input: [arguments สำหรับ tool]
Observation: [ผลลัพธ์ที่ได้]
... (ทำซ้ำ)
Final Answer: [คำตอบสุดท้าย]
"""
```

### 4.2 Plan-and-Execute Pattern

แทนที่จะให้ agent ทำทีละขั้น → ให้คิดแผนก่อน:

```python
# Step 1: Plan
plan = llm.complete(f"""
สร้างแผน 5 ขั้นตอนเพื่อตอบ: {user_message}
Output JSON array
""")

# Step 2: Execute each step
for step in plan:
    result = execute_step(step)
    
# Step 3: Synthesize
final = llm.complete(f"สรุปผลจาก: {results}")
```

**เปรียบเทียบ:**

| Pattern | เหมาะกับ | ข้อเสีย |
|---|---|---|
| ReAct | งานไม่แน่นอน, ต้องปรับตัว | ใช้ token เยอะ |
| Plan-and-Execute | งานชัดเจน, เป็นขั้นเป็นตอน | ถ้าแผนผิด → ทำใหม่หมด |
| Hybrid (default) | ใช้ได้ทั่วไป | ซับซ้อนกว่า |

---

<a id="5-providers"></a>
## 5. Multi-Provider Support

### 5.1 Why Multi-Provider?

- **Cost optimization** — ใช้ gpt-4o-mini สำหรับงานง่าย, gpt-4o สำหรับงานยาก
- **Fallback** — ถ้า OpenAI down → ใช้ Anthropic
- **Best-of-breed** — GPT-4o ดีที่ vision, Claude ดีที่ reasoning

### 5.2 Unified Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    def complete(self, messages: list, tools: list = None) -> Response:
        pass

class OpenAIProvider(LLMProvider):
    def complete(self, messages, tools=None):
        # Call OpenAI API
        ...

class AnthropicProvider(LLMProvider):
    def complete(self, messages, tools=None):
        # Call Anthropic API
        ...

class GeminiProvider(LLMProvider):
    def complete(self, messages, tools=None):
        # Call Gemini API
        ...
```

### 5.3 Switching in Code

```python
provider = "openai"  # or "anthropic" or "google"
model = "gpt-4o-mini"

if provider == "openai":
    llm = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"), model=model)
elif provider == "anthropic":
    llm = AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"), model=model)
elif provider == "google":
    llm = GeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"), model=model)
```

### 5.4 Provider Quirks

| Feature | OpenAI | Anthropic | Google |
|---|---|---|---|
| Function calling | ✅ | ✅ (tools) | ✅ |
| Vision | ✅ | ✅ | ✅ |
| Streaming | ✅ | ✅ | ✅ |
| JSON mode | ✅ | ✅ (via prompt) | ✅ |
| Max context | 128K | 200K | 1M |
| Thai support | ดี | ดีมาก | ดี |

**คำแนะนำ:**
- เริ่มต้น: **OpenAI gpt-4o-mini** (ถูก, เร็ว, work well)
- Reasoning หนัก ๆ: **Anthropic Claude 3.5 Sonnet** (เก่ง reasoning, Thai ดี)
- ฟรี: **Google Gemini 1.5 Flash** (ฟรี 1M token/วัน, Thai OK)

---

<a id="6-errors"></a>
## 6. Error Handling & Retry

### 6.1 Failure Modes

| Error | สาเหตุ | แก้ |
|---|---|---|
| LLM timeout | API ช้า | Retry with backoff |
| Rate limit | เรียกเยอะเกินไป | Queue + delay |
| Invalid JSON | LLM ตอบผิด format | Retry with stronger prompt |
| Tool not found | LLM เรียก tool ที่ไม่มี | Return error to LLM |
| Tool timeout | Tool ใช้เวลานาน | Cap timeout 30s |
| Max iterations | Loop ไม่จบ | Force final answer |

### 6.2 Retry Decorator

```python
import time
from functools import wraps

def retry(max_attempts=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff ** attempt
                    print(f"Retry {attempt+1}/{max_attempts} after {wait}s: {e}")
                    time.sleep(wait)
        return wrapper
    return decorator

@retry(max_attempts=3, backoff=2)
def call_llm(messages):
    return openai_client.chat.completions.create(...)
```

### 6.3 Graceful Degradation

```python
def safe_tool_execution(tool_func, **kwargs):
    try:
        result = tool_func(**kwargs)
        return {"success": True, "result": result}
    except TimeoutError:
        return {"success": False, "error": "Tool took too long"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

<a id="7-perf"></a>
## 7. Performance & Cost

### 7.1 Cost Estimate (gpt-4o-mini)

| Scenario | Tokens (in + out) | Cost (USD) | Cost (THB) |
|---|---|---|---|
| Simple Q&A | 500 + 100 | $0.0001 | ~0.004 บาท |
| With 1 tool call | 1,500 + 200 | $0.0003 | ~0.01 บาท |
| Multi-step (5 iter) | 5,000 + 500 | $0.001 | ~0.04 บาท |
| Heavy use (100/day) | - | $0.10/day | ~3.5 บาท/วัน |
| Heavy use (3000/mo) | - | $3/mo | ~105 บาท/เดือน |

**คำแนะนำ:**
- ใช้ gpt-4o-mini สำหรับ 80% ของงาน
- ใช้ gpt-4o เฉพาะงานที่ต้อง reasoning หนัก
- Cache results (ถ้าถามเหมือนเดิม ไม่ต้องเรียก LLM)

### 7.2 Latency

| Operation | Time |
|---|---|
| LLM call (gpt-4o-mini) | 0.5-2s |
| Tool execution | 0.1-5s |
| Token estimation | <10ms |
| JSON parsing | <10ms |
| **Total per iteration** | **1-7s** |
| **Full conversation (5 iter)** | **5-35s** |

### 7.3 Optimization Tips

1. **Stream responses** — user เห็นคำตอบทีละคำ เร็วขึ้น
2. **Parallel tool calls** — ถ้า agent เรียก 2 tools ที่ไม่ depend กัน
3. **Cache** — `lru_cache` สำหรับ tool results
4. **Smaller models** — ใช้ gpt-4o-mini แทน gpt-4o ถ้าไม่จำเป็น
5. **Context compression** — สรุป context เก่าแทนการเก็บทั้งหมด

---

## 🎓 เรียนรู้เพิ่ม

- [ReAct Paper](https://arxiv.org/abs/2210.03629) — ต้นฉบับ paper
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Anthropic Tool Use](https://docs.anthropic.com/claude/docs/tool-use)
- [LangChain Agents](https://python.langchain.com/docs/modules/agents/) — สำหรับคนอยากใช้ framework
- [Haystack](https://haystack.deepset.ai/) — alternative

---

**อ่านจบแล้ว? ลองแก้ code ใน `code/agent_loop.py` แล้วรันดู! 🚀**
