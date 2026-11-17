"""Pruebas unitarias básicas del flujo gratuito y de seguridad."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.script_generator import generate_script, validate_script
from core.product_finder import normalize_product
from core.analytics import calculate_product_metrics
from core.publishing_manager import publish_draft

class ScriptGeneratorTests(unittest.TestCase):
    def test_supported_durations_have_contiguous_scenes(self):
        product = {"product_id": "demo-1", "name": "Organizador plegable"}
        for duration in (15, 25, 30, 45):
            with self.subTest(duration=duration):
                script = generate_script(product, duration)
                self.assertTrue(validate_script(script, duration))
                self.assertEqual(script["scenes"][0]["start"], 0)
                self.assertEqual(script["scenes"][-1]["end"], duration)

    def test_invalid_product_is_rejected(self):
        with self.assertRaises(ValueError):
            generate_script({"name": "Sin identificador"})

class ProductValidationTests(unittest.TestCase):
    def test_manual_data_is_not_marked_verified(self):
        product = normalize_product({
            "name": "Producto de prueba",
            "category": "hogar",
            "price_mxn": 100,
            "commission_percent": 10,
            "product_url": "https://example.com/product",
            "affiliate_url": "https://example.com/affiliate",
        }, source_name="manual")
        self.assertIsNotNone(product)
        self.assertEqual(product["status"], "incomplete")
        self.assertEqual(product["verified_at"], "")

class AnalyticsTests(unittest.TestCase):
    def test_metrics_are_calculated_from_recorded_events(self):
        result = calculate_product_metrics([
            {"product_id": "p1", "event_type": "click", "quantity": 10, "amount_mxn": 0},
            {"product_id": "p1", "event_type": "sale", "quantity": 2, "amount_mxn": 0},
            {"product_id": "p1", "event_type": "commission", "quantity": 1, "amount_mxn": 25.5},
        ])[0]
        self.assertEqual(result["clicks"], 10)
        self.assertEqual(result["sales"], 2)
        self.assertEqual(result["click_to_sale_rate_percent"], 20.0)
        self.assertEqual(result["commissions_mxn"], 25.5)

class PublishingSafetyTests(unittest.TestCase):
    def test_automatic_publishing_is_blocked(self):
        with self.assertRaisesRegex(RuntimeError, "deshabilitada"):
            publish_draft("demo")

if __name__ == "__main__":
    unittest.main()
