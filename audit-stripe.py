#!/usr/bin/env python3
"""Comprehensive Stripe audit — 7 days, test mode."""
import os, sys, json, time, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timedelta, timezone

key_file = Path(".stripe-test-key")
if not key_file.exists():
    print("ERROR: .stripe-test-key not found")
    sys.exit(1)
KEY = key_file.read_text().strip()

def api_get(path, params=""):
    url = f"https://api.stripe.com/v1/{path}?{params}" if params else f"https://api.stripe.com/v1/{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {KEY}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"{e.code} {e.reason}: {e.read().decode()[:200]}"}

# 7 days ago
since_ts = int((datetime.now(timezone.utc) - timedelta(days=7)).timestamp())

print("=" * 70)
print("STRIPE AUDIT (TEST MODE) — last 7 days")
print("=" * 70)
print(f"Account check...")
account = api_get("account")
if "error" in account:
    print(f"  ERROR: {account['error']}")
    sys.exit(1)
print(f"  ID: {account.get('id')}")
print(f"  Country: {account.get('country')}")
print(f"  Default currency: {account.get('default_currency')}")
print(f"  Test mode: {not account.get('livemode', True)}")
print(f"  Charges enabled: {account.get('charges_enabled')}")
print(f"  Payouts enabled: {account.get('payouts_enabled')}")
print()

# === Payments ===
print("[1] PAYMENT INTENTS (last 7d)")
pi = api_get("payment_intents", f"limit=100&created[gte]={since_ts}")
if "error" in pi:
    print(f"  ERROR: {pi['error']}")
else:
    intents = pi.get("data", [])
    print(f"  Total: {len(intents)}")
    by_status = {}
    for i in intents:
        s = i.get("status", "unknown")
        by_status[s] = by_status.get(s, 0) + 1
    for s, c in sorted(by_status.items()):
        print(f"    {s}: {c}")
    succeeded = [i for i in intents if i.get("status") == "succeeded"]
    if succeeded:
        total = sum(i.get("amount", 0) for i in succeeded) / 100
        print(f"  Total revenue (test): {total:.2f} THB")

# === Charges ===
print()
print("[2] CHARGES (last 7d)")
ch = api_get("charges", f"limit=100&created[gte]={since_ts}")
if "error" in ch:
    print(f"  ERROR: {ch['error']}")
else:
    charges = ch.get("data", [])
    print(f"  Total: {len(charges)}")
    paid = [c for c in charges if c.get("paid")]
    refunded = [c for c in charges if c.get("refunded")]
    print(f"  Paid: {len(paid)}")
    print(f"  Refunded: {len(refunded)}")
    if charges:
        # Check for unusual charges
        print(f"  Latest 5:")
        for c in charges[:5]:
            amt = c.get("amount", 0) / 100
            cur = c.get("currency", "").upper()
            paid_s = "paid" if c.get("paid") else "unpaid"
            ref = " [REFUNDED]" if c.get("refunded") else ""
            print(f"    {amt:>8.2f} {cur}  {paid_s}{ref}  {c.get('id')}")

# === Customers ===
print()
print("[3] CUSTOMERS (last 7d)")
cu = api_get("customers", f"limit=100&created[gte]={since_ts}")
if "error" in cu:
    print(f"  ERROR: {cu['error']}")
else:
    customers = cu.get("data", [])
    print(f"  Total: {len(customers)}")
    if customers:
        for c in customers[:5]:
            print(f"    {c.get('id')}  {c.get('email', '(no email)')}  {c.get('created')}")

# === Refunds ===
print()
print("[4] REFUNDS (last 7d)")
re = api_get("refunds", f"limit=100&created[gte]={since_ts}")
if "error" in re:
    print(f"  ERROR: {re['error']}")
else:
    refunds = re.get("data", [])
    print(f"  Total: {len(refunds)}")
    if refunds:
        for r in refunds:
            amt = r.get("amount", 0) / 100
            print(f"    {amt} {r.get('currency', '').upper()}  status={r.get('status')}  {r.get('id')}")

# === Disputes ===
print()
print("[5] DISPUTES (last 7d)")
dp = api_get("disputes", f"limit=100&created[gte]={since_ts}")
if "error" in dp:
    print(f"  ERROR: {dp['error']}")
else:
    disputes = dp.get("data", [])
    print(f"  Total: {len(disputes)}")

# === Balance ===
print()
print("[6] BALANCE (test mode)")
bal = api_get("balance")
if "error" in bal:
    print(f"  ERROR: {bal['error']}")
else:
    for b in bal.get("available", []):
        print(f"  Available: {b.get('amount', 0)/100:.2f} {b.get('currency', '').upper()}")
    for b in bal.get("pending", []):
        print(f"  Pending: {b.get('amount', 0)/100:.2f} {b.get('currency', '').upper()}")

# === Products / Prices ===
print()
print("[7] PRODUCTS")
pr = api_get("products", "limit=20")
if "error" in pr:
    print(f"  ERROR: {pr['error']}")
else:
    products = pr.get("data", [])
    print(f"  Total: {len(products)}")
    for p in products[:12]:
        print(f"    {p.get('id')[-12:]}  {p.get('name', '?')[:50]}  active={p.get('active')}")

# === API Keys (metadata only — not the keys themselves) ===
print()
print("[8] API KEY LAST USAGE")
# We can't list keys via API, but we can check by usage in events
print("  Note: API key usage is logged in Stripe events (api_version, etc.)")

# === Events (last hour, look for anything weird) ===
print()
print("[9] RECENT EVENTS (last 1h)")
ev_ts = int(time.time()) - 3600
ev = api_get("events", f"limit=50&created[gte]={ev_ts}&type[starts_with]=payment_")
if "error" in ev:
    print(f"  ERROR: {ev['error']}")
else:
    events = ev.get("data", [])
    print(f"  Payment events: {len(events)}")
    for e in events[:10]:
        etype = e.get("type", "")
        ts = time.strftime("%H:%M:%S", time.localtime(e.get("created", 0)))
        print(f"    {ts}  {etype}")

# === Suspicious activity check ===
print()
print("[10] SUSPICIOUS ACTIVITY CHECK")
# Look for:
# - Multiple charges to same email in short time (card testing)
# - Failed payment attempts
# - High-value charges
suspicious = []
all_pi = api_get("payment_intents", f"limit=100&created[gte]={since_ts}")
if "data" in all_pi:
    for i in all_pi["data"]:
        if i.get("status") == "requires_payment_method":
            suspicious.append(f"  - Failed PI: {i.get('id')} (amount={i.get('amount')/100})")
        amt = i.get("amount", 0)
        if amt > 50000:  # > 50,000 THB
            suspicious.append(f"  - High-value: {i.get('id')} ({amt/100} THB)")

if suspicious:
    print("  Found:")
    for s in suspicious:
        print(s)
else:
    print("  None found — clean")

print()
print("=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)
