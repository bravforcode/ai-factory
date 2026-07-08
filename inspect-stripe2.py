#!/usr/bin/env python3
"""Inspect Stripe page AFTER card is selected to find input names."""
from playwright.sync_api import sync_playwright

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="en-US")
    page = ctx.new_page()
    page.goto("https://buy.stripe.com/test_fZu4gtelqelIeJ6ghX1Fe00", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(4000)

    # Click Card radio
    page.locator('#payment-method-accordion-item-title-card').first.click(force=True)
    page.wait_for_timeout(4000)

    # Dump all inputs
    info = page.evaluate("""() => {
        const inputs = Array.from(document.querySelectorAll('input, select, button'));
        return inputs.map(el => ({
            tag: el.tagName,
            type: el.type || '',
            name: el.name || '',
            id: el.id || '',
            placeholder: el.placeholder || '',
            autocomplete: el.autocomplete || '',
            value: el.value || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            dataTest: el.getAttribute('data-testid') || '',
            visible: el.offsetParent !== null,
        })).filter(e => e.visible);
    }""")
    print(f"=== {len(info)} visible inputs/buttons after Card click ===")
    for i, e in enumerate(info):
        print(f"{i:3d} {e['tag']:8s} type={e['type']:12s} name={e['name']:30s} id={e['id']:25s} ph={e['placeholder'][:25]:25s} auto={e['autocomplete']:20s} aria={e['ariaLabel'][:30]:30s} test={e['dataTest']:20s}")

    browser.close()
