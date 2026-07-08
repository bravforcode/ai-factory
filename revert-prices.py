#!/usr/bin/env python3
"""Revert price fixes — original HTML was correct, match Stripe actual charges."""
import json
import re
from pathlib import Path

# Actual Stripe charges (from latest audit)
# Order: 01, 02, 03, 04, 05, 06, 07, 08, 09, 10
STRIPE = {
    "01-prompt-pack-th": 299,
    "02-obsidian-student-kit": 199,
    "03-freelance-pricing-calculator": 149,
    "04-cold-email-template-pack": 399,   # was changed 399->199, revert
    "05-ai-automation-workflow": 499,     # was changed 499->599, revert
    "06-cv-international-template": 199,  # was changed 199->149, revert
    "07-n8n-sme-workflow-pack": 799,      # was changed 799->999, revert
    "08-content-calendar-90d": 599,       # was changed 599->199, revert
    "09-finance-tracker-thb": 149,        # was changed 149->399, revert
    "10-ai-agent-starter-github": 999,    # was changed 999->799, revert
}

# Revert: change new_p -> old_p
REVERTS = {
    "04-cold-email-template-pack": (199, 399),
    "05-ai-automation-workflow": (599, 499),
    "06-cv-international-template": (149, 199),
    "07-n8n-sme-workflow-pack": (999, 799),
    "08-content-calendar-90d": (199, 599),
    "09-finance-tracker-thb": (399, 149),
    "10-ai-agent-starter-github": (799, 999),
}

def fix_file(slug, new_p, old_p):
    for prefix in [slug, f"thanks-{slug}"]:
        f = f"{prefix}.html"
        if not Path(f).exists():
            continue
        text = Path(f).read_text(encoding="utf-8")
        original = text
        text = re.sub(rf"\b{new_p}\s*บาท", f"{old_p} บาท", text)
        if text != original:
            Path(f).write_text(text, encoding="utf-8")
            print(f"  [OK] {f}: {new_p} -> {old_p}")

def fix_json(slug, new_p, old_p):
    p = Path("products.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    for product in data["products"]:
        if product["slug"] == slug:
            if product["price_thb"] != old_p:
                product["price_thb"] = old_p
                print(f"  [JSON] {slug}: {new_p} -> {old_p}")
            break
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

print("=" * 60)
print("REVERT prices to match Stripe (original was correct)")
print("=" * 60)
for slug, (new, old) in REVERTS.items():
    print(f"\n>> {slug} ({new} -> {old})")
    fix_file(slug, new, old)
    fix_json(slug, new, old)

print()
print("=" * 60)
print("Verify")
print("=" * 60)
import subprocess
subprocess.run(["python", "find-prices.py"], check=False)
