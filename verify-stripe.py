#!/usr/bin/env python3
"""Read-only Stripe test-mode aggregate check.

The key is accepted only from STRIPE_SECRET_KEY. The response is never written
to disk and no customer, card, raw provider payload, or full identifier is
printed. This script does not prove production readiness or live fulfillment.
"""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter


def fetch(path: str, key: str) -> dict:
    request = urllib.request.Request(
        "https://api.stripe.com/v1/" + path,
        headers={"Authorization": "Bearer " + key},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            value = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Stripe API returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Stripe API request failed: {type(exc).__name__}") from None
    if not isinstance(value, dict):
        raise RuntimeError("Stripe API returned an invalid object")
    return value


def main() -> int:
    key = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not key:
        print("ERROR: STRIPE_SECRET_KEY is not set")
        return 1
    if not key.startswith("sk_test_"):
        print("ERROR: this verifier accepts test-mode keys only")
        return 1

    created_after = int(time.time()) - 600
    query = urllib.parse.urlencode({"limit": 100, "created[gte]": created_after})
    try:
        intents = fetch("payment_intents?" + query, key).get("data", [])
        charges = fetch("charges?" + query, key).get("data", [])
    except RuntimeError as exc:
        print("ERROR: " + str(exc))
        return 1

    if not isinstance(intents, list) or not isinstance(charges, list):
        print("ERROR: Stripe API returned invalid list fields")
        return 1

    intent_statuses = Counter(
        item.get("status", "unknown")
        for item in intents
        if isinstance(item, dict)
    )
    currencies = Counter(
        str(item.get("currency", "unknown")).upper()
        for item in intents
        if isinstance(item, dict)
    )
    succeeded_amount = sum(
        int(item.get("amount_received") or item.get("amount") or 0)
        for item in intents
        if isinstance(item, dict) and item.get("status") == "succeeded"
    )

    print("Stripe test-mode aggregate (last 10 minutes)")
    print(f"payment_intents={len(intents)}")
    print(f"charges={len(charges)}")
    print(f"succeeded_amount_minor_units={succeeded_amount}")
    print("intent_statuses=" + json.dumps(dict(sorted(intent_statuses.items())), sort_keys=True))
    print("currencies=" + json.dumps(dict(sorted(currencies.items())), sort_keys=True))
    print("raw_response_saved=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
