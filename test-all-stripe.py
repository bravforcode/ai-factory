#!/usr/bin/env python3
"""Full E2E test for all 10 products."""
import json
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


def test_product(browser, slug, stripe_link):
    """Test 1 product end-to-end. Returns result dict."""
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="en-US")
    page = ctx.new_page()
    result = {
        "slug": slug,
        "stripe_link": stripe_link,
        "landing_ok": False,
        "stripe_ok": False,
        "card_filled": False,
        "pay_clicked": False,
        "success_url": None,
        "thanks_ok": False,
        "error": None,
        "elapsed_sec": 0,
    }
    t0 = time.time()
    try:
        # 1. Landing
        page.goto(f"{BASE_URL}/{slug}", wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)
        result["landing_ok"] = True

        # 2. Click buy
        page.locator(f'a[href="{stripe_link}"]').first.click()

        # 3. Wait for Stripe
        page.wait_for_url("**/buy.stripe.com/**", timeout=30000)
        page.wait_for_timeout(5000)
        result["stripe_ok"] = True

        # 4. Email
        page.locator('input[name="email"]').first.fill(TEST_EMAIL)
        page.keyboard.press("Tab")
        page.wait_for_timeout(1500)

        # 5. Card radio
        page.locator('#payment-method-accordion-item-title-card').first.click(force=True)
        page.wait_for_timeout(3000)

        # 6. Card details
        page.locator('input[name="cardNumber"]').first.fill(TEST_CARD)
        page.wait_for_timeout(400)
        page.locator('input[name="cardExpiry"]').first.fill(TEST_EXP)
        page.wait_for_timeout(400)
        page.locator('input[name="cardCvc"]').first.fill(TEST_CVC)
        page.wait_for_timeout(400)
        page.locator('input[name="billingName"]').first.fill(TEST_NAME)
        page.wait_for_timeout(800)
        result["card_filled"] = True
        page.screenshot(path=str(SCREENS / f"{slug}-card.png"))

        # 7. Pay
        page.locator('[data-testid="hosted-payment-submit-button"]').first.click()
        result["pay_clicked"] = True

        # 8. Success
        page.wait_for_url(
            lambda u: "buy.stripe.com" not in u or "success" in u,
            timeout=30000,
        )
        page.wait_for_timeout(2500)
        result["success_url"] = page.url
        page.screenshot(path=str(SCREENS / f"{slug}-success.png"), full_page=True)

        # 9. Verify thanks page
        body_text = page.locator("body").inner_text()
        result["thanks_ok"] = "ขอบคุณ" in body_text or "thank" in body_text.lower()

    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"
        try:
            page.screenshot(path=str(SCREENS / f"{slug}-error.png"))
        except Exception:
            pass
    finally:
        result["elapsed_sec"] = round(time.time() - t0, 1)
        ctx.close()
    return result


def main():
    headless = "--headed" not in sys.argv
    print("=" * 60)
    print(f"E2E: 10 products via Stripe Checkout")
    print(f"Headless: {headless}")
    print("=" * 60)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        results = []
        for slug, link in PRODUCTS:
            print(f"\n>> {slug} ...", end="", flush=True)
            r = test_product(browser, slug, link)
            status = "PASS" if (r["success_url"] and r["thanks_ok"]) else "FAIL"
            print(f" [{status}] {r['elapsed_sec']}s")
            if r.get("error"):
                print(f"   ERR: {r['error']}")
            results.append(r)
        browser.close()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r["success_url"] and r["thanks_ok"])
    for r in results:
        ok = r["success_url"] and r["thanks_ok"]
        s = "PASS" if ok else "FAIL"
        url = (r["success_url"] or "(none)").replace("https://Ai Factory-sales-pages.vercel.app", "")
        err = f" — {r['error'][:50]}" if r.get("error") else ""
        print(f"  [{s}] {r['slug']:35s} -> {url:50s} {r['elapsed_sec']}s{err}")
    print(f"\n{passed}/10 PASSED")
    print(f"Screenshots: {SCREENS.absolute_path()}")

    Path("e2e-results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if passed == 10 else 1


if __name__ == "__main__":
    sys.exit(main())
