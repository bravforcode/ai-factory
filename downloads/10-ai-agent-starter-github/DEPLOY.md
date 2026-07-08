# Deployment Guide
**Deploy AI Agent ของคุณบน Cloud — ฟรี/ถูก พร้อม scale**

> 🚀 คู่มือ deploy บน 3 platforms: Railway, Render, Fly.io  
> 💰 เปรียบเทียบราคา + ข้อดีข้อเสีย

---

## Quick Decision Tree

```
ต้องการอะไร?
│
├─ ง่ายสุด + เร็วสุด → Railway (deploy ใน 5 นาที)
│
├─ ฟรี 100% → Render Free Tier (sleep หลัง 15 นาที idle)
│
├─ Control เต็มที่ + Multi-region → Fly.io
│
└─ Self-host → VPS (DigitalOcean, Hetzner, AWS EC2)
```

---

## Option 1: Railway (แนะนำ — ง่ายสุด)

**เวลา deploy: 5 นาที**  
**ราคา: $5/mo (~175 บาท) — Starter plan**

### Step 1: เตรียม GitHub Repo
```bash
cd ai-agent-starter
git init
git add .
git commit -m "Initial commit"
gh repo create ai-agent-starter --public --source=. --push
```

### Step 2: Deploy บน Railway
1. ไปที่ https://railway.app → Sign up with GitHub
2. คลิก "New Project" → "Deploy from GitHub repo"
3. เลือก `ai-agent-starter`
4. Railway จะ detect Python อัตโนมัติ

### Step 3: ตั้งค่า Environment
ใน Railway dashboard → Variables:
```
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
PORT=8000
```

### Step 4: เพิ่ม Procfile
สร้างไฟล์ `Procfile`:
```
web: cd code && python app.py
```

### Step 5: Deploy
Railway จะ deploy อัตโนมัติ → ได้ URL: `https://your-app.railway.app`

**ทดสอบ:**
```bash
curl https://your-app.railway.app/health
# {"status": "ok"}
```

**Cost:**
- Starter: $5/mo + usage (~175 บาท/เดือน)
- Light traffic (1,000 requests/day) = ~$5-10/mo
- Heavy traffic (10,000 requests/day) = ~$20-50/mo

---

## Option 2: Render (ฟรี tier)

**เวลา deploy: 10 นาที**  
**ราคา: $0 (free) / $7/mo (paid)**

### Step 1: สร้าง `render.yaml`
```yaml
services:
  - type: web
    name: ai-agent
    env: python
    plan: free
    buildCommand: "cd code && pip install -r requirements.txt"
    startCommand: "cd code && python app.py"
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: LLM_PROVIDER
        value: openai
      - key: LLM_MODEL
        value: gpt-4o-mini
```

### Step 2: Deploy
1. ไปที่ https://render.com → Sign up
2. New → Blueprint
3. Connect GitHub repo
4. Render จะ deploy ตาม `render.yaml`

**ข้อจำกัด Free tier:**
- Sleep หลัง idle 15 นาที
- Cold start ~30 วินาที
- 750 ชม./เดือน (พอใช้)

**ถ้าต้องการไม่ sleep:** Plan $7/mo

---

## Option 3: Fly.io (Multi-region)

**เวลา deploy: 15 นาที**  
**ราคา: Free tier + $1.94/mo สำหรับ 1 VM**

### Step 1: Install flyctl
```bash
# macOS
brew install flyctl

# Windows
iwr https://fly.io/install.ps1 -useb | iex

# Linux
curl -L https://fly.io/install.sh | sh
```

### Step 2: สร้าง Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY code/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY code/ .
COPY prompts/ ./prompts/

EXPOSE 8000
CMD ["python", "app.py"]
```

### Step 3: Deploy
```bash
fly auth signup
fly launch
fly secrets set OPENAI_API_KEY=sk-...
fly deploy
```

**ได้ URL:** `https://ai-agent.fly.dev`

**ข้อดี:**
- Multi-region (Singapore, Tokyo, US)
- Auto-scaling
- Free TLS cert

---

## Option 4: VPS (Self-host) — ถูกสุด

**เวลา deploy: 30 นาที**  
**ราคา: 300-500 บาท/เดือน**

### Provider แนะนำ
- **Hetzner** — €4/mo (160 บาท) — EU
- **DigitalOcean** — $4/mo (140 บาท) — Singapore available
- **Vultr** — $2.50/mo (87 บาท) — Tokyo available
- **AWS Lightsail** — $3.50/mo (122 บาท) — Bangkok region (2024+)

### Setup (Ubuntu 22.04)

#### 1. SSH & Update
```bash
ssh root@your-server-ip
apt update && apt upgrade -y
```

#### 2. Install Docker
```bash
curl -fsSL https://get.docker.com | sh
```

#### 3. Deploy
```bash
mkdir /opt/ai-agent
cd /opt/ai-agent

# Clone repo
git clone https://github.com/yourname/ai-agent-starter.git .

# Create .env
cp code/.env.example code/.env
nano code/.env  # ใส่ API keys

# Build & run
cd code
docker build -t ai-agent .
docker run -d --restart unless-stopped \
  --name ai-agent \
  -p 8000:8000 \
  --env-file .env \
  ai-agent
```

#### 4. Reverse proxy + SSL (Caddy)
```bash
# Install Caddy
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/gpg.key" | gpg --dearmor > /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf "https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt" | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install caddy

# Configure
cat > /etc/caddy/Caddyfile <<EOF
yourdomain.com {
    reverse_proxy localhost:8000
}
EOF

systemctl reload caddy
```

**ได้:** `https://yourdomain.com`

---

## การสร้าง Web API (app.py)

เพิ่มไฟล์ `app.py` ใน folder `code/`:

```python
"""
app.py — REST API wrapper for AI Agent
========================================

Exposes the agent via HTTP endpoints:
- POST /chat
- GET /health
- POST /clear
- GET /tools
"""

import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

from agent_loop import Agent
from tools import TOOL_REGISTRY
from memory import Memory

app = Flask(__name__)
CORS(app)

# Singleton agent
agent = Agent(
    provider=os.getenv("LLM_PROVIDER", "openai"),
    model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
    memory=Memory(persist_path="./memory.json")
)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model": agent.model,
        "tools": list(TOOL_REGISTRY.keys())
    })


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' field"}), 400

    user_id = data.get("user_id", "default")
    message = data["message"]

    try:
        response = agent.run(message, user_id=user_id)
        return jsonify({
            "response": response,
            "user_id": user_id,
            "tokens": agent.total_tokens
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/clear", methods=["POST"])
def clear():
    data = request.json or {}
    user_id = data.get("user_id", "default")
    agent.memory.clear()
    return jsonify({"status": "cleared", "user_id": user_id})


@app.route("/tools", methods=["GET"])
def tools():
    return jsonify({
        "tools": [
            {
                "name": name,
                "description": data["schema"].get("description", "")
            }
            for name, data in TOOL_REGISTRY.items()
        ]
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=False)
```

**Test locally:**
```bash
python app.py
# ใน terminal อื่น:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "สวัสดี", "user_id": "test"}'
```

---

## การเพิ่ม Telegram / LINE Bot Interface

### Telegram Bot
```python
# telegram_bot.py
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from agent_loop import Agent
from memory import Memory

logging.basicConfig(level=logging.INFO)
agent = Agent(memory=Memory(persist_path="./memory_telegram.json"))


async def start(update: Update, context):
    await update.message.reply_text("สวัสดีครับ! ถามอะไรก็ได้ครับ 🤖")


async def handle_message(update: Update, context):
    user_id = f"tg_{update.effective_user.id}"
    response = agent.run(update.message.text, user_id=user_id)
    await update.message.reply_text(response)


if __name__ == "__main__":
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.run_polling()
```

### LINE Bot (ใช้ line-bot-sdk)
```python
# line_bot.py
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from agent_loop import Agent
from memory import Memory
import os

app = Flask(__name__)
agent = Agent(memory=Memory(persist_path="./memory_line.json"))

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = f"line_{event.source.user_id}"
    response = agent.run(event.message.text, user_id=user_id)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))


if __name__ == "__main__":
    app.run(port=8000)
```

---

## Monitoring (สำคัญสำหรับ Production)

### 1. Health check
ทุก platform มี built-in health check ที่ `/health` endpoint

### 2. Logging
```python
import logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    filename=os.getenv("LOG_FILE")  # or stdout
)
```

### 3. Error tracking (Sentry)
```bash
pip install sentry-sdk
```
```python
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
```

### 4. Analytics
Track usage:
```python
# ใน app.py
from datetime import datetime

USAGE_LOG = "usage.jsonl"

def log_usage(user_id, message, response, tokens):
    with open(USAGE_LOG, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "message_length": len(message),
            "response_length": len(response),
            "tokens": tokens
        }) + "\n")
```

---

## Cost Optimization Tips

### ใช้ Model ถูกลง
- gpt-4o-mini: $0.15/1M input tokens
- gpt-4o: $5/1M input tokens (33 เท่า)
- **คำแนะนำ:** ใช้ gpt-4o-mini 80%, gpt-4o 20%

### Cache results
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_search(query):
    return web_search(query)
```

### Rate limiting
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.json.get("user_id", "anon"))

@app.route("/chat", methods=["POST"])
@limiter.limit("10 per minute")
def chat():
    ...
```

### Set max tokens per request
```python
# Cap LLM output
response = openai_client.chat.completions.create(
    model=model,
    max_tokens=500,  # cap at 500
    messages=messages
)
```

---

## Checklist ก่อน Go-Live

- [ ] API keys ตั้งใน env vars (ไม่ hardcode)
- [ ] HTTPS enabled (Caddy/Certbot/Cloudflare)
- [ ] Health check endpoint working
- [ ] Error handling ครอบคลุม
- [ ] Rate limiting
- [ ] Logging
- [ ] Monitoring (Sentry/UptimeRobot)
- [ ] Backup memory file (cron)
- [ ] Documentation updated
- [ ] Privacy policy + ToS

---

## Rollback Plan

ถ้า deploy ใหม่พัง:

**Railway:**
- Dashboard → Deployments → เลือก version เก่า → Redeploy

**Render:**
- Dashboard → Manual Deploy → เลือก commit เก่า

**Docker:**
```bash
docker stop ai-agent
docker run -d --name ai-agent ai-agent:previous-tag
```

**VPS:**
```bash
cd /opt/ai-agent
git checkout previous-tag
docker compose up -d --build
```

---

## Support

- 📧 Email: support@aifactory.co
- 🐛 GitHub Issues: https://github.com/yourname/ai-agent-starter/issues
- 💬 Discord: "AI Builders Thailand"

---

**Happy deploying! 🚀**
