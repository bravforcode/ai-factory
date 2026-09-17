"""Route catalog product pages through Revenue OS checkout."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_TAG = '<script src="/checkout-config.js"></script>\n<script src="/revenue-os-checkout.js" defer></script>\n'
STRIPE_HREF = re.compile(r'href="https://buy\.stripe\.com/[^"]+"')


def main() -> int:
    products = json.loads((ROOT / "products.json").read_text(encoding="utf-8-sig"))["products"]
    changed = 0
    for product in products:
        slug = product["slug"]
        path = ROOT / f"{slug}.html"
        text = path.read_text(encoding="utf-8")
        routed = STRIPE_HREF.sub(
            f'href="#buy" data-revenue-product="{slug}"',
            text,
        )
        if "revenue-os-checkout.js" not in routed:
            routed = routed.replace("</body>", SCRIPT_TAG + "</body>")
        if routed != text:
            path.write_text(routed, encoding="utf-8", newline="")
            changed += 1
    print(json.dumps({"status": "ok", "pages_changed": changed, "product_count": len(products)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
