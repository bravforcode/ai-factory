import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from catalog_contract import CatalogContractError, main, thb_to_satang, validate_catalog


ROOT = Path(__file__).resolve().parent


class CatalogContractTests(unittest.TestCase):
    def setUp(self):
        self.products = json.loads(
            (ROOT / "products.json").read_text(encoding="utf-8-sig")
        )
        self.links = json.loads(
            (ROOT / "stripe-links-live.json").read_text(encoding="utf-8-sig")
        )

    def write_inputs(self, directory, products=None, links=None):
        products_path = directory / "products.json"
        links_path = directory / "stripe-links-live.json"
        products_path.write_text(
            json.dumps(self.products if products is None else products),
            encoding="utf-8-sig",
        )
        links_path.write_text(
            json.dumps(self.links if links is None else links),
            encoding="utf-8-sig",
        )
        return products_path, links_path

    def assert_invalid(self, products=None, links=None, expected_code=""):
        with TemporaryDirectory() as temp:
            products_path, links_path = self.write_inputs(
                Path(temp), products=products, links=links
            )
            with self.assertRaises(CatalogContractError) as raised:
                validate_catalog(products_path, links_path)
        self.assertIn(expected_code, raised.exception.issue_codes)

    def test_valid_bom_catalog_reports_satang_contract(self):
        with TemporaryDirectory() as temp:
            products_path, links_path = self.write_inputs(Path(temp))
            report = validate_catalog(products_path, links_path)
        self.assertEqual(report["product_count"], 10)
        self.assertEqual(report["link_count"], 10)
        self.assertEqual(report["amount_unit"], "satang")
        self.assertEqual(thb_to_satang(299), 29900)

    def test_duplicate_slug_is_rejected(self):
        products = json.loads(json.dumps(self.products))
        products["products"][1]["slug"] = products["products"][0]["slug"]
        self.assert_invalid(products=products, expected_code="duplicate_slug")

    def test_non_positive_or_non_integer_price_is_rejected(self):
        for value in (0, -1, 1.5, True, "299"):
            products = json.loads(json.dumps(self.products))
            products["products"][0]["price_thb"] = value
            with self.subTest(value=value):
                self.assert_invalid(products=products, expected_code="price_thb_invalid")

    def test_link_keys_must_cover_catalog_exactly(self):
        links = dict(self.links)
        links.pop(next(iter(links)))
        links["unexpected-product"] = "https://buy.stripe.com/live_example"
        self.assert_invalid(links=links, expected_code="link_key_coverage")

    def test_test_or_non_https_links_are_rejected(self):
        for link in (
            "https://buy.stripe.com/test_example",
            "http://buy.stripe.com/live_example",
            "https://example.com/live_example",
        ):
            links = dict(self.links)
            links[next(iter(links))] = link
            with self.subTest(link=link):
                self.assert_invalid(links=links, expected_code="live_link_invalid")

    def test_secret_like_public_values_are_rejected(self):
        products = json.loads(json.dumps(self.products))
        products["public_api_key"] = "sk_live_not-for-public-use"
        self.assert_invalid(products=products, expected_code="public_secret_like_value")

    def test_cli_failure_is_nonzero_and_redacted(self):
        products = json.loads(json.dumps(self.products))
        products["private_key"] = "sk_live_do_not_print"
        with TemporaryDirectory() as temp:
            products_path, links_path = self.write_inputs(Path(temp), products=products)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = main(["--products", str(products_path), "--links", str(links_path)])
        self.assertNotEqual(exit_code, 0)
        self.assertNotIn("sk_live_do_not_print", output.getvalue())
        self.assertIn("public_secret_like_value", output.getvalue())


if __name__ == "__main__":
    unittest.main()
