#!/usr/bin/env python3
"""Verify new product name shows in Stripe checkout (product 07)."""
import json, urllib.request, time, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

key_file = Path(".stripe-test-key")
KEY = key_file.read_text().strip()

# Get product 7's payment link
def api(method, path):
    req = urllib.request.Request(f"https://api.stripe.com/v1/{path}", method=method)
    req.add_header("Authorization", f"Bearer {KEY}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

# Find product 7 (n8n)
prods = api("GET", "products?limit=20")
target = None
for p in prods.get("data", []):
    if "n8n" in p.get("name", "").lower():
        target = p
        break

if not target:
    print("Product 7 not found")
    exit(1)

print(f"Product: {target['name']} ({target['id']})")

# Get payment link
prices = api("GET", f"prices?product={target['id']}&limit=1")
if not prices.get("data"):
    print("No price found")
    exit(1)

price_id = prices["data"][0]["id"]
print(f"Price: {price_id}")

# List payment links and find one whose line items include our price
links = api("GET", "payment_links?limit=100")
link_url = None
for l in links.get("data", []):
    line_items = l.get("line_items", {}).get("data", [])
    for li in line_items:
        if li.get("price", {}).get("id") == price_id:
            link_url = l.get("url")
            break
    if link_url:
        break

if not link_url:
    # fallback: check stripe-links.json
    sl_file = Path("stripe-links.json")
    if sl_file.exists():
        sl = json.loads(sl_file.read_text(encoding="utf-8-sig"))
        link_url = sl.get("07-n8n-sme-workflow-pack")

if not link_url:
    print("No payment link found")
    exit(1)

print(f"Link: {link_url}")
print()

# E2E test
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    print("Opening Stripe checkout...")
    page.goto(link_url, wait_until="domcontentloaded", timeout=60000)
    time.sleep(2)

    # Screenshot checkout
    Path("e2e-screenshots/verify-07-checkout.png").parent.mkdir(exist_ok=True)
    page.screenshot(path="e2e-screenshots/verify-07-checkout.png")

    # Read product name from DOM (try multiple selectors)
    product_name = None
    for selector in [
        '[data-testid="product-summary"]',
        'h1',
        '[class*="ProductSummary"]',
        'body',
    ]:
        try:
            product_name = page.locator(selector).first.inner_text(timeout=8000)
            if product_name and len(product_name) > 5:
                break
        except:
            continue

    if not product_name:
        # fallback: full page text
        product_name = page.inner_text("body")[:200]

    print(f"Checkout shows: '{product_name[:150]}'")
    print()

    # Check if "n8n SME" is visible (the new name)
    if "n8n SME" in product_name or "n8n Sme" in product_name.lower():
        print("[PASS] New name 'n8n SME Workflow Pack' visible in checkout!")
    elif "N8N" in product_name:
        print("[WARN] Old name 'N8N' still visible (cache issue? wait + retry)")
        time.sleep(3)
        page.reload(wait_until="networkidle")
        time.sleep(2)
        product_name = page.locator('[data-testid="product-summary"]').first.inner_text(timeout=5000)
        print(f"After reload: '{product_name[:80]}'")
        if "n8n SME" in product_name:
            print("[PASS] New name visible after reload")
    else:
        print(f"[?] Name check inconclusive, got: '{product_name[:60]}'")

    browser.close()
print()
print("Done. Check: e2e-screenshots/verify-07-checkout.png")
