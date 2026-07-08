#!/usr/bin/env python3
"""Inspect Stripe Payment Link DOM to find card input elements."""
from playwright.sync_api import sync_playwright
from pathlib import Path

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1280, "height": 800}, locale="en-US")
    page = ctx.new_page()
    page.goto("https://buy.stripe.com/test_fZu4gtelqelIeJ6ghX1Fe00", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)
    page.screenshot(path="inspect-1.png", full_page=True)

    # Get all input/button elements
    info = page.evaluate("""() => {
        const inputs = Array.from(document.querySelectorAll('input, button, [role="radio"], select, iframe'));
        return inputs.map(el => ({
            tag: el.tagName,
            type: el.type || '',
            name: el.name || '',
            id: el.id || '',
            placeholder: el.placeholder || '',
            role: el.getAttribute('role') || '',
            ariaLabel: el.getAttribute('aria-label') || '',
            textContent: (el.textContent || '').trim().slice(0, 60),
            visible: el.offsetParent !== null,
        })).filter(e => e.visible);
    }""")
    print(f"=== {len(info)} visible interactive elements ===")
    for i, e in enumerate(info):
        print(f"{i:3d} {e['tag']:8s} type={e['type']:10s} name={e['name']:20s} id={e['id']:20s} role={e['role']:10s} aria={e['ariaLabel'][:30]:30s} text={e['textContent'][:40]!r}")

    # Specifically look for radios
    print("\n=== RADIO INPUTS ===")
    radios = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('input[type="radio"]')).map(r => ({
            name: r.name, value: r.value, id: r.id, checked: r.checked, visible: r.offsetParent !== null,
            parentText: r.closest('label, div')?.textContent?.trim().slice(0, 50) || ''
        }));
    }""")
    for r in radios:
        print(f"  {r}")

    # Save HTML
    html = page.content()
    Path("inspect-stripe.html").write_text(html)
    print(f"\nHTML saved: {Path('inspect-stripe.html').stat().st_size} bytes")

    browser.close()
