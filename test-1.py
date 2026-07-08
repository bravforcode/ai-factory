#!/usr/bin/env python3
"""Full E2E test for 1 product with direct HTML input selectors."""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "https://Ai Factory-sales-pages.vercel.app"
TEST_EMAIL = "test+e2e@Ai Factory.local"
TEST_CARD = "4242 4242 4242 4242"
TEST_EXP = "12 / 34"
TEST_CVC = "123"
TEST_NAME = "E2E Tester"
SCREENS = Path("e2e-screenshots")
SCREENS.mkdir(exist_ok=True)

slug = "01-prompt-pack-th"
stripe_link = "https://buy.stripe.com/test_fZu4gtelqelIeJ6ghX1Fe00"

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="en-US")
    page = ctx.new_page()

    # 1. Open landing
    print(f"[1] Open landing: /{slug}")
    page.goto(f"{BASE_URL}/{slug}", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # 2. Click buy
    print(f"[2] Click buy")
    page.locator(f'a[href="{stripe_link}"]').first.click()

    # 3. Wait for Stripe page
    print(f"[3] Wait for Stripe")
    page.wait_for_url("**/buy.stripe.com/**", timeout=30000)
    print(f"    URL: {page.url[:80]}")
    page.wait_for_timeout(5000)
    page.screenshot(path=str(SCREENS / "01-checkout.png"))

    # 4. Fill email
    print(f"[4] Fill email")
    page.locator('input[name="email"]').first.fill(TEST_EMAIL)
    page.keyboard.press("Tab")
    page.wait_for_timeout(2000)

    # 5. Click Card radio
    print(f"[5] Select Card payment method")
    page.locator('#payment-method-accordion-item-title-card').first.click(force=True)
    page.wait_for_timeout(3000)
    page.screenshot(path=str(SCREENS / "02-card-selected.png"))

    # 6. Fill card (direct HTML inputs — no iframe)
    print(f"[6] Fill card details")
    page.locator('input[name="cardNumber"]').first.fill(TEST_CARD)
    page.wait_for_timeout(400)
    page.locator('input[name="cardExpiry"]').first.fill(TEST_EXP)
    page.wait_for_timeout(400)
    page.locator('input[name="cardCvc"]').first.fill(TEST_CVC)
    page.wait_for_timeout(400)
    page.locator('input[name="billingName"]').first.fill(TEST_NAME)
    page.wait_for_timeout(400)
    page.screenshot(path=str(SCREENS / "03-card-filled.png"))

    # 7. Click Pay
    print(f"[7] Click Pay")
    pay = page.locator('[data-testid="hosted-payment-submit-button"]').first
    pay.click()

    # 8. Wait for success
    print(f"[8] Wait for success (max 30s)")
    try:
        page.wait_for_url(
            lambda u: "buy.stripe.com" not in u or "success" in u,
            timeout=30000,
        )
        page.wait_for_timeout(2000)
        print(f"    FINAL URL: {page.url}")
        page.screenshot(path=str(SCREENS / "04-success.png"), full_page=True)
        print("    PASS")
    except Exception as e:
        page.screenshot(path=str(SCREENS / "04-stuck.png"), full_page=True)
        print(f"    FAIL: {e}")
        print(f"    current URL: {page.url}")

    browser.close()
