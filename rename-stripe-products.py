#!/usr/bin/env python3
"""Update Stripe product names to match HTML."""
import json, urllib.request, urllib.error, sys
from pathlib import Path

# Force UTF-8 output (Windows cp1252 can't print Thai)
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

key_file = Path(".stripe-test-key")
KEY = key_file.read_text().strip()

# HTML (canonical) → Stripe name to update
RENAMES = {
    "01-prompt-pack-th": "AI Prompt Pack (ภาษาไทย)",
    "02-obsidian-student-kit": "Obsidian Student Kit (นักศึกษา)",
    "03-freelance-pricing-calculator": "Freelance Pricing Calculator (THB)",
    "04-cold-email-template-pack": "Cold Email Template Pack",
    "05-ai-automation-workflow": "AI Automation Workflow Cheatsheet",
    "06-cv-international-template": "CV International Template",
    "07-n8n-sme-workflow-pack": "n8n SME Workflow Pack",
    "08-content-calendar-90d": "Content Calendar 90 วัน",
    "09-finance-tracker-thb": "Personal Finance Tracker (THB)",
    "10-ai-agent-starter-github": "AI Agent Starter (GitHub)",
}

def api(method, path, data=None):
    url = f"https://api.stripe.com/v1/{path}"
    if data:
        body = urllib.parse.urlencode(data).encode()
        req = urllib.request.Request(url, data=body, method=method)
    else:
        req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {KEY}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.read().decode()[:200]}

# List all products
print("=== Current Stripe products ===")
prods = api("GET", "products?limit=20")
if "error" in prods:
    print(f"ERROR: {prods['error']}")
    exit(1)

import urllib.parse

for p in prods.get("data", []):
    cur_name = p.get("name", "")
    pid = p.get("id")
    print(f"  {pid[-12:]}  '{cur_name}'")

print()
print("=== Renaming to match HTML ===")

# Match by current name (rough match)
target_for_current = {
    "AI Agent Starter (GitHub)": "AI Agent Starter (GitHub)",
    "Personal Finance Tracker (THB)": "Personal Finance Tracker (THB)",
    "Freelance Pricing Calculator (THB)": "Freelance Pricing Calculator (THB)",
    "Obsidian Starter Kit นักศึกษา": "Obsidian Student Kit (นักศึกษา)",
    "N8N Workflow Pack SME": "n8n SME Workflow Pack",
    "AI Automation Workflow Cheatsheet": "AI Automation Workflow Cheatsheet",
    "Content Calendar 90 วัน": "Content Calendar 90 วัน",
    "Cold Email Template Pack TH/EN": "Cold Email Template Pack",
    "Cold Email Template Pack": "Cold Email Template Pack",
    "AI Prompt Pack ภาษาไทย": "AI Prompt Pack (ภาษาไทย)",
    "CV International Template": "CV International Template",
    "CV/Resume Template สมัครงานต่างประเทศ": "CV International Template",
}

for p in prods.get("data", []):
    cur = p.get("name", "")
    new = target_for_current.get(cur)
    if new and new != cur:
        result = api("POST", f"products/{p['id']}", {"name": new})
        if "error" in result:
            print(f"  [FAIL] {p['id']}: {result['error']}")
        else:
            print(f"  [OK] {p['id']}: '{cur}' -> '{result.get('name')}'")
    else:
        print(f"  [SKIP] {p['id']}: '{cur}' (no rename needed)")

print()
print("=== After rename ===")
prods2 = api("GET", "products?limit=20")
for p in prods2.get("data", []):
    print(f"  {p.get('id')[-12:]}  '{p.get('name', '')}'")
