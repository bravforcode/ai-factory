#!/usr/bin/env python3
"""Verify test payments via Stripe API."""
import os, sys, json, time, urllib.request, urllib.error
from pathlib import Path

# Load key from file
key_file = Path(".stripe-test-key")
if not key_file.exists():
    print("ERROR: .stripe-test-key file not found")
    sys.exit(1)
TEST_KEY = key_file.read_text().strip()

print("=" * 60)
print("Stripe API: Verify test payments")
print("=" * 60)

# PaymentIntents created in last 10 minutes
created_after = int(time.time()) - 600

url = f"https://api.stripe.com/v1/payment_intents?limit=20&created[gte]={created_after}"
req = urllib.request.Request(url)
req.add_header("Authorization", f"Bearer {TEST_KEY}")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
except urllib.error.HTTPError as e:
    print(f"ERROR: {e.code} {e.reason}")
    print(e.read().decode())
    sys.exit(1)

intents = data.get("data", [])
print(f"\nFound {len(intents)} PaymentIntents in last 10 min:\n")

succeeded = []
for intent in intents:
    amt = intent.get("amount", 0) / 100
    cur = intent.get("currency", "").upper()
    status = intent.get("status", "")
    desc = intent.get("description", "") or (intent.get("metadata", {}) or {}).get("product", "")
    pi_id = intent.get("id", "")
    created = time.strftime("%H:%M:%S", time.localtime(intent.get("created", 0)))
    pm = intent.get("payment_method", "")[-8:] if intent.get("payment_method") else ""
    print(f"  {created}  {pi_id}  {amt:>8.2f} {cur}  {status:15s}  {desc[:50]}")
    if status == "succeeded":
        succeeded.append(intent)

print()
print(f"Succeeded: {len(succeeded)}/{len(intents)}")
print(f"Total revenue (test): {sum(i.get('amount', 0) for i in succeeded) / 100:.2f} THB")

# Also list Charges for confirmation
url2 = f"https://api.stripe.com/v1/charges?limit=20&created[gte]={created_after}"
req2 = urllib.request.Request(url2)
req2.add_header("Authorization", f"Bearer {TEST_KEY}")
try:
    with urllib.request.urlopen(req2, timeout=30) as resp:
        charges = json.loads(resp.read())
    print(f"\nCharges (confirmation): {len(charges.get('data', []))}")
    for c in charges.get("data", [])[:15]:
        amt = c.get("amount", 0) / 100
        cur = c.get("currency", "").upper()
        paid = c.get("paid", False)
        print(f"  {amt:>8.2f} {cur}  paid={paid}  {c.get('id', '')}")
except Exception as e:
    print(f"Charges fetch error: {e}")

# Save raw
Path("stripe-intents.json").write_text(json.dumps(data, indent=2))
print("\nSaved: stripe-intents.json")
