#!/usr/bin/env python3
"""
Stripe Payment E2E Test — Playwright
Tests full purchase flow on all 10 products.

Flow per product:
  1. Open Vercel landing page
  2. Click "ซื้อเลย" button → Stripe Checkout
  3. Fill email + card 4242 (no 3DS)
  4. Submit → success page
  5. Screenshot + verify
"""

import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ===== Config =====
BASE_URL = "https://Ai Factory-sales-pages.vercel.app"
TEST_EMAIL = "test+e2e@Ai Factory.local"
TEST_CARD = "4242 4242 4242 4242"
TEST_EXP = "12 / 34"
TEST_CVC = "123"
TEST_ZIP = "10110"
TEST_NAME = "E2E Tester"

PRODUCTS = [
    ("01-prompt-pack-th", "https://buy.stripe.com/test_fZu4gtelqelIeJ6ghX1Fe00"),
    ("02-obsidian-student-kit", "https://buy.stripe.com/test_7sY14h9163H41WkfdT1Fe01"),
    ("03-freelance-pricing-calculator", "https://buy.stripe.com/test_eVqcMZ7X21yW0Sg4zf1Fe02"),
    ("04-cold-email-template-pack", "https://buy.stripe.com/test_9B614h2CI5Pc58w1n31Fe03"),
    ("05-ai-automation-workflow", "https://buy.stripe.com/test_aFaaERb9e7Xk0Sgc1H1Fe04"),
    ("06-cv-international-template", "https://buy.stripe.com/test_9B68wJelqgtQ6cAc1H1Fe05"),
    ("07-n8n-sme-workflow-pack", "https://buy.stripe.com/test_00w6oBcdi7Xk8kI9Tz1Fe06"),
    ("08-content-calendar-90d", "https://buy.stripe.com/test_aFa14h1yEdhE1Wk2r71Fe07"),
    ("09-finance-tracker-thb", "https://buy.stripe.com/test_bJebIVcdi91o1Wk1n31Fe08"),
    ("10-ai-agent-starter-github", "https://buy.stripe.com/test_cNiaERfpugtQasQ7Lr1Fe09"),
]

SCREENSHOTS = Path("e2e-screenshots")
SCREENSHOTS.mkdir(exist_ok=True)
RESULTS = []


def find_stripe_iframes(page, timeout_ms=30000):
    """Detect split or unified Stripe Payment Element iframes."""
    deadline = time.time() + (timeout_ms / 1000)
    while time.time() < deadline:
        # Split mode: distinct iframes
        split_num = page.frame_locator('iframe[title="Secure card number input"]')
        if split_num.count() if hasattr(split_num, 'count') else True:
            try:
                if split_num.locator('input[name="cardnumber"]').first.is_visible(timeout=500):
                    return ("split", {
                        "num": page.frame_locator('iframe[title="Secure card number input"]'),
                        "exp": page.frame_locator('iframe[title="Secure expiration date input"]'),
                        "cvc": page.frame_locator('iframe[title="Secure CVC input"]'),
                        "zip": page.frame_locator('iframe[title="Secure postal code input"]'),
                    })
            except Exception:
                pass

        # Unified mode: single iframe
        unified = page.frame_locator('iframe[title*="payment" i]')
        try:
            if unified.locator('input[name="cardnumber"]').first.is_visible(timeout=500):
                return ("unified", {"frame": unified})
        except Exception:
            pass

        # Fallback unified title
        unified2 = page.frame_locator('iframe[src*="elements-inner"]')
        try:
            if unified2.locator('input[name="cardnumber"]').first.is_visible(timeout=500):
                return ("unified", {"frame": unified2})
        except Exception:
            pass

        page.wait_for_timeout(500)
    return (None, None)


def fill_card(page, mode, frames):
    """Fill card details into Stripe iframe(s)."""
    if mode == "split":
        num = frames["num"].locator('input[name="cardnumber"]').first
        num.click()
        num.fill(TEST_CARD)
        page.wait_for_timeout(300)

        exp = frames["exp"].locator('input[name="exp-date"]').first
        exp.click()
        exp.fill(TEST_EXP)
        page.wait_for_timeout(300)

        cvc = frames["cvc"].locator('input[name="cvc"]').first
        cvc.click()
        cvc.fill(TEST_CVC)
        page.wait_for_timeout(300)

        try:
            zip_in = frames["zip"].locator('input[name="postal"]').first
            if zip_in.is_visible(timeout=1000):
                zip_in.click()
                zip_in.fill(TEST_ZIP)
        except Exception:
            pass
    else:  # unified
        f = frames["frame"]
        for sel, val in [
            ('input[name="cardnumber"]', TEST_CARD),
            ('input[name="exp-date"]', TEST_EXP),
            ('input[name="cvc"]', TEST_CVC),
        ]:
            inp = f.locator(sel).first
            inp.click()
            inp.fill(val)
            page.wait_for_timeout(300)
        try:
            zip_in = f.locator('input[name="postal"]').first
            if zip_in.is_visible(timeout=1000):
                zip_in.click()
                zip_in.fill(TEST_ZIP)
        except Exception:
            pass


def test_one_product(p, slug, stripe_link, headless=True):
    """Test one product end-to-end. Returns dict with result."""
    result = {
        "slug": slug,
        "stripe_link": stripe_link,
        "landing_ok": False,
        "checkout_ok": False,
        "card_filled": False,
        "pay_clicked": False,
        "success_url": None,
        "error": None,
    }

    # 1. Open landing page
    landing_url = f"{BASE_URL}/{slug}"
    print(f"\n[{slug}] Opening {landing_url}")
    try:
        p.goto(landing_url, wait_until="domcontentloaded", timeout=30000)
        p.wait_for_timeout(1500)  # let Stripe Buy Button inject
        p.screenshot(path=str(SCREENSHOTS / f"{slug}-01-landing.png"))
        result["landing_ok"] = True
    except Exception as e:
        result["error"] = f"landing: {e}"
        return result

    # 2. Click "ซื้อเลย" button — find anchor with stripe link
    try:
        # Look for the Stripe payment link anchor
        buy_btn = p.locator(f'a[href="{stripe_link}"]').first
        if not buy_btn.is_visible(timeout=5000):
            # Fallback: any "ซื้อ" anchor
            buy_btn = p.locator('a:has-text("ซื้อ")').first
        print(f"  Clicking buy button: {buy_btn.first.inner_text()[:30]}...")
        with p.context.expect_page(timeout=10000) as new_page_info:
            buy_btn.click()
        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded", timeout=30000)
    except Exception as e:
        # Maybe same-tab redirect
        try:
            p.wait_for_url("**/checkout.stripe.com/**", timeout=10000)
            new_page = p
        except Exception as e2:
            result["error"] = f"checkout: {e2}"
            return result

    print(f"  On Stripe Checkout: {new_page.url[:80]}...")
    new_page.wait_for_timeout(3000)  # let Payment Element render
    new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-02-checkout.png"))

    # 3. Fill email
    try:
        email_in = new_page.get_by_label("Email", exact=False).first
        if not email_in.is_visible(timeout=5000):
            email_in = new_page.get_by_role("textbox", name=/email/i).first
        email_in.click()
        email_in.fill(TEST_EMAIL)
        new_page.wait_for_timeout(500)
        # Trigger blur to render Payment Element fully
        new_page.keyboard.press("Tab")
        new_page.wait_for_timeout(1000)

        # 3b. Click "Pay with card" if shown (sometimes wallets appear first)
        for txt in ["Pay with card", "Card"]:
            btn = new_page.locator(f'button:has-text("{txt}")').first
            try:
                if btn.is_visible(timeout=1000):
                    btn.click()
                    new_page.wait_for_timeout(500)
                    break
            except Exception:
                pass
    except Exception as e:
        result["error"] = f"email: {e}"
        return result

    # 4. Find Stripe iframes
    mode, frames = find_stripe_iframes(new_page, timeout_ms=20000)
    if not mode:
        new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-03-no-iframe.png"))
        result["error"] = "no stripe iframes detected"
        return result
    result["checkout_ok"] = True
    print(f"  Found Stripe iframes: {mode}")

    # 5. Fill card
    try:
        fill_card(new_page, mode, frames)
        new_page.wait_for_timeout(500)
        new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-03-card-filled.png"))
        result["card_filled"] = True
    except Exception as e:
        new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-03-card-error.png"))
        result["error"] = f"card fill: {e}"
        return result

    # 6. Click Pay button
    try:
        pay_btn = new_page.locator('button[type="submit"]:has-text("Pay")').first
        # Sometimes it's "Pay 299.00" or "Pay $X"
        if not pay_btn.is_visible(timeout=3000):
            pay_btn = new_page.locator('button:has-text("Pay")').first
        pay_btn.click()
        result["pay_clicked"] = True
        print("  Pay clicked, waiting for success...")
    except Exception as e:
        result["error"] = f"pay click: {e}"
        return result

    # 7. Wait for success — URL changes away from checkout.stripe.com
    try:
        new_page.wait_for_url(
            lambda u: "checkout.stripe.com" not in u or "success" in u or "succeeded" in u,
            timeout=30000,
        )
        new_page.wait_for_timeout(2000)
        result["success_url"] = new_page.url
        print(f"  [OK] Final URL: {new_page.url[:100]}")
        new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-04-success.png"), full_page=True)
    except PWTimeout:
        new_page.screenshot(path=str(SCREENSHOTS / f"{slug}-04-stuck.png"), full_page=True)
        result["error"] = "timeout waiting for success redirect"
        result["success_url"] = new_page.url
    except Exception as e:
        result["error"] = f"wait success: {e}"
        result["success_url"] = new_page.url

    return result


def main():
    headless = "--headed" not in sys.argv

    print("=" * 60)
    print("E2E Test: 10 Products via Stripe Checkout (test mode)")
    print(f"Headless: {headless}")
    print("=" * 60)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Ai FactoryE2E/1.0",
        )

        for slug, link in PRODUCTS:
            page = context.new_page()
            try:
                r = test_one_product(page, slug, link, headless=headless)
            except Exception as e:
                r = {"slug": slug, "error": f"unhandled: {e}"}
            RESULTS.append(r)
            page.close()
            # Small delay between products
            time.sleep(1)

        browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in RESULTS if r.get("success_url") and not r.get("error"))
    failed = len(RESULTS) - passed
    for r in RESULTS:
        status = "PASS" if r.get("success_url") and not r.get("error") else "FAIL"
        err = f" — {r['error']}" if r.get("error") else ""
        url = f" → {r['success_url'][:60]}" if r.get("success_url") else ""
        print(f"  [{status}] {r['slug']}{url}{err}")

    print(f"\nPassed: {passed}/{len(RESULTS)}")
    print(f"Screenshots: {SCREENSHOTS.absolute_path()}")

    # Save JSON
    Path("e2e-results.json").write_text(json.dumps(RESULTS, indent=2, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
