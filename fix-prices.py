#!/usr/bin/env python3
"""Fix price mismatches: HTML + thanks + products.json → match Stripe."""
import json
import re
from pathlib import Path

# Stripe actual charges (verified from API)
PRICES = {
    "01-prompt-pack-th": 299,
    "02-obsidian-student-kit": 199,
    "03-freelance-pricing-calculator": 149,
    "04-cold-email-template-pack": 199,
    "05-ai-automation-workflow": 599,
    "06-cv-international-template": 149,
    "07-n8n-sme-workflow-pack": 999,
    "08-content-calendar-90d": 199,
    "09-finance-tracker-thb": 399,
    "10-ai-agent-starter-github": 799,
}

# For each file, expected old price -> new price
# Only fixing files where mismatch exists
FIXES = {
    "04-cold-email-template-pack.html": (399, 199),
    "04-cold-email-template-pack": (399, 199),  # placeholder, real is thanks-
    "05-ai-automation-workflow.html": (499, 599),
    "06-cv-international-template.html": (199, 149),
    "07-n8n-sme-workflow-pack.html": (799, 999),
    "08-content-calendar-90d.html": (599, 199),
    "09-finance-tracker-thb.html": (149, 399),
    "10-ai-agent-starter-github.html": (999, 799),
}

# Process landing pages
def fix_landing(slug, old_p, new_p):
    """Fix a landing page: replace all instances of old_p with new_p in price contexts."""
    f = f"{slug}.html"
    if not Path(f).exists():
        print(f"  [SKIP] {f} not found")
        return False
    text = Path(f).read_text(encoding="utf-8")
    original = text

    # Pattern: replace "XXX บาท" with "YYY บาท" — but only where XXX matches old_p
    # Use word boundary to avoid replacing parts of larger numbers
    text = re.sub(
        rf"\b{old_p}\s*บาท",
        f"{new_p} บาท",
        text
    )

    if text == original:
        print(f"  [NO CHANGE] {f}")
        return False
    Path(f).write_text(text, encoding="utf-8")
    return True

# Process thanks pages
def fix_thanks(slug, old_p, new_p):
    f = f"thanks-{slug}.html"
    if not Path(f).exists():
        print(f"  [SKIP] {f} not found")
        return False
    text = Path(f).read_text(encoding="utf-8")
    original = text

    text = re.sub(rf"\b{old_p}\s*บาท", f"{new_p} บาท", text)

    if text == original:
        print(f"  [NO CHANGE] {f}")
        return False
    Path(f).write_text(text, encoding="utf-8")
    return True

# Process products.json
def fix_products_json(slug, new_p):
    """Update products.json price for this slug."""
    p = Path("products.json")
    data = json.loads(p.read_text(encoding="utf-8"))
    changed = False
    for product in data["products"]:
        if product["slug"] == slug:
            if product["price_thb"] != new_p:
                old = product["price_thb"]
                product["price_thb"] = new_p
                changed = True
                print(f"  [JSON] {slug}: {old} -> {new_p}")
            break
    if changed:
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return changed


# Mismatches to fix (from check-prices.py output)
MISMATCH = {
    "04-cold-email-template-pack": (399, 199),
    "05-ai-automation-workflow": (499, 599),
    "06-cv-international-template": (199, 149),
    "07-n8n-sme-workflow-pack": (799, 999),
    "08-content-calendar-90d": (599, 199),
    "09-finance-tracker-thb": (149, 399),
    "10-ai-agent-starter-github": (999, 799),
}

print("=" * 60)
print("PRICE FIX: HTML + thanks + products.json")
print("=" * 60)

for slug, (old, new) in MISMATCH.items():
    print(f"\n>> {slug} ({old} -> {new})")
    fix_landing(slug, old, new)
    fix_thanks(slug, old, new)
    fix_products_json(slug, new)

print()
print("=" * 60)
print("Verify prices after fix")
print("=" * 60)
import subprocess
subprocess.run(["python", "find-prices.py"], check=False)
