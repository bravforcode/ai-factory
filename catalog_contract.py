#!/usr/bin/env python3
"""Validate the local public catalog and live Stripe-link contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


EXPECTED_PRODUCT_COUNT = 10
SATANG_PER_THB = 100
PRODUCTS_PATH = Path(__file__).with_name("products.json")
LIVE_LINKS_PATH = Path(__file__).with_name("stripe-links-live.json")

_MISSING = object()
_SECRET_KEY_RE = re.compile(
    r"(?:api[_-]?key|access[_-]?token|auth(?:entication)?[_-]?token|"
    r"client[_-]?secret|credential|private[_-]?key|password|passwd|"
    r"secret|token|authorization)",
    re.IGNORECASE,
)
_SECRET_VALUE_RE = re.compile(
    r"(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]+|whsec_[A-Za-z0-9]+|"
    r"(?:ghp|github_pat|xox[baprs]-|AIza)[A-Za-z0-9_-]+|"
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    re.IGNORECASE,
)
_TEST_LINK_RE = re.compile(r"(?:^|[/_.?=&-])test(?:[/_.?=&-]|$)", re.IGNORECASE)


class CatalogContractError(ValueError):
    """Validation failure with non-sensitive structural issue codes."""

    def __init__(self, issue_codes: set[str] | list[str] | tuple[str, ...]):
        self.issue_codes = tuple(sorted(set(issue_codes)))
        self.codes = self.issue_codes
        super().__init__("catalog contract validation failed")


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def load_json(path: Path | str) -> Any:
    """Load a public JSON document without accepting duplicate object keys."""

    with Path(path).open("r", encoding="utf-8-sig") as stream:
        return json.load(stream, object_pairs_hook=_unique_json_object)


def thb_to_satang(price_thb: Any) -> int:
    """Convert a positive whole-baht amount to satang."""

    if isinstance(price_thb, bool) or not isinstance(price_thb, int) or price_thb <= 0:
        raise ValueError("price_thb must be a positive integer")
    return price_thb * SATANG_PER_THB


def _has_secret_like_value(value: Any, key: str | None = None) -> bool:
    if key and _SECRET_KEY_RE.search(key) and value not in (None, "", [], {}):
        return True
    if isinstance(value, str) and _SECRET_VALUE_RE.search(value):
        return True
    if isinstance(value, dict):
        return any(
            _has_secret_like_value(item, str(item_key))
            for item_key, item in value.items()
        )
    if isinstance(value, list):
        return any(_has_secret_like_value(item) for item in value)
    return False


def _read_json(path: Path, issue_code: str, issues: set[str]) -> Any:
    try:
        return load_json(path)
    except (OSError, UnicodeError, ValueError):
        issues.add(issue_code)
        return _MISSING


def _validate_products(value: Any, issues: set[str]) -> tuple[list[str], list[int], int]:
    if value is _MISSING:
        return [], [], 0
    if not isinstance(value, dict):
        issues.add("products_shape")
        return [], [], 0
    if _has_secret_like_value(value):
        issues.add("public_secret_like_value")

    products = value.get("products")
    if not isinstance(products, list):
        issues.add("products_list")
        return [], [], 0
    if len(products) != EXPECTED_PRODUCT_COUNT:
        issues.add("product_count")

    slugs: list[str] = []
    prices_satang: list[int] = []
    for product in products:
        if not isinstance(product, dict):
            issues.add("product_shape")
            continue
        slug = product.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            issues.add("slug_invalid")
        else:
            slugs.append(slug)
        try:
            prices_satang.append(thb_to_satang(product.get("price_thb")))
        except ValueError:
            issues.add("price_thb_invalid")

    if len(slugs) != len(set(slugs)):
        issues.add("duplicate_slug")
    return slugs, prices_satang, len(products)


def _is_live_buy_link(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    if parsed.scheme != "https" or parsed.hostname != "buy.stripe.com":
        return False
    if parsed.username or parsed.password or not parsed.path.strip("/"):
        return False
    return _TEST_LINK_RE.search(value) is None


def _validate_links(value: Any, issues: set[str]) -> tuple[set[str], int]:
    if value is _MISSING:
        return set(), 0
    if not isinstance(value, dict):
        issues.add("links_shape")
        return set(), 0
    if _has_secret_like_value(value):
        issues.add("public_secret_like_value")

    link_slugs: set[str] = set()
    for slug, link in value.items():
        if not isinstance(slug, str) or not slug.strip():
            issues.add("link_key_invalid")
        else:
            link_slugs.add(slug)
        if not _is_live_buy_link(link):
            issues.add("live_link_invalid")
    return link_slugs, len(value)


def validate_catalog(
    products_path: Path = PRODUCTS_PATH,
    links_path: Path = LIVE_LINKS_PATH,
) -> dict[str, Any]:
    """Validate local catalog/link inputs and return a redacted structural report."""

    issues: set[str] = set()
    products_value = _read_json(Path(products_path), "products_read", issues)
    links_value = _read_json(Path(links_path), "links_read", issues)
    slugs, prices_satang, product_count = _validate_products(products_value, issues)
    link_slugs, link_count = _validate_links(links_value, issues)

    if set(slugs) != link_slugs:
        issues.add("link_key_coverage")
    if issues:
        raise CatalogContractError(issues)

    return {
        "status": "ok",
        "product_count": product_count,
        "link_count": link_count,
        "price_count": len(prices_satang),
        "currency": "THB",
        "amount_unit": "satang",
        "satang_per_thb": SATANG_PER_THB,
        "secret_like_values": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--products", type=Path, default=PRODUCTS_PATH)
    parser.add_argument("--links", type=Path, default=LIVE_LINKS_PATH)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = validate_catalog(args.products, args.links)
    except CatalogContractError as exc:
        print(json.dumps({"status": "fail", "issue_codes": exc.issue_codes}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
