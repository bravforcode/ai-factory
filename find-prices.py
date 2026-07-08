#!/usr/bin/env python3
"""Find prices in HTML files."""
import re
from pathlib import Path

files = [
    "01-prompt-pack-th.html", "02-obsidian-student-kit.html",
    "03-freelance-pricing-calculator.html", "04-cold-email-template-pack.html",
    "05-ai-automation-workflow.html", "06-cv-international-template.html",
    "07-n8n-sme-workflow-pack.html", "08-content-calendar-90d.html",
    "09-finance-tracker-thb.html", "10-ai-agent-starter-github.html",
]

print(f"{'file':<42s} {'prices found'}")
print("-" * 70)
for f in files:
    text = Path(f).read_text(encoding="utf-8")
    prices = re.findall(r"(\d{2,4})\s*(?:บาท|baht)", text)
    uniq = sorted(set(prices), key=int)
    print(f"{f:<42s} {uniq}")

# Same for thanks pages
print()
print("THANKS pages:")
for i in range(1, 11):
    slugs = {
        1: "01-prompt-pack-th", 2: "02-obsidian-student-kit",
        3: "03-freelance-pricing-calculator", 4: "04-cold-email-template-pack",
        5: "05-ai-automation-workflow", 6: "06-cv-international-template",
        7: "07-n8n-sme-workflow-pack", 8: "08-content-calendar-90d",
        9: "09-finance-tracker-thb", 10: "10-ai-agent-starter-github",
    }
    f = f"thanks-{slugs[i]}.html"
    text = Path(f).read_text(encoding="utf-8")
    prices = re.findall(r"(\d{2,4})\s*(?:บาท|baht)", text)
    uniq = sorted(set(prices), key=int)
    print(f"{f:<45s} {uniq}")
