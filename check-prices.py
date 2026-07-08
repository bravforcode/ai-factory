#!/usr/bin/env python3
import json
d = json.load(open("products.json", encoding="utf-8"))
print(f"{'slug':<40s} {'products.json':>12s}")
print("-" * 60)
for p in d["products"]:
    print(f"{p['slug']:<40s} {p['price_thb']:>10d} THB")

# Cross-check with Stripe actual charges
print()
print("Actual Stripe charges (from earlier audit):")
stripe = {
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
print(f"{'slug':<40s} {'products.json':>12s} {'Stripe':>8s} {'OK?':>5s}")
print("-" * 70)
for p in d["products"]:
    slug = p["slug"]
    expected = p["price_thb"]
    actual = stripe.get(slug, 0)
    ok = "OK" if expected == actual else "MISMATCH"
    print(f"{slug:<40s} {expected:>10d}    {actual:>5d}   {ok}")
