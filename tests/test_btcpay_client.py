import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from btcpay_client import BTCPayClient, BTCPayError

ORDER = "a" * 32

class Fixture(BTCPayClient):
    def __init__(self):
        super().__init__("https://example.org", "store", "local-fixture", "local-fixture")
        self.payload = None
        self.invoice = {
            "id": "invoice_123", "status": "New", "currency": "BTC",
            "amount": "0.00002500", "metadata": {"orderId": ORDER}
        }
    def _api(self, endpoint, body=None):
        self.payload = body
        return dict(self.invoice)

class AdapterTests(unittest.TestCase):
    def test_satoshi_conversion(self):
        obj = Fixture()
        obj.create_invoice(ORDER, 2500)
        self.assertEqual(obj.payload["amount"], "0.00002500")
    def test_invoice_order_binding(self):
        obj = Fixture()
        obj.invoice["metadata"] = {"orderId": "b" * 32}
        with self.assertRaises(BTCPayError):
            obj.create_invoice(ORDER, 2500)
    def test_wrong_amount_rejected(self):
        obj = Fixture()
        obj.invoice["amount"] = "0.00003000"
        with self.assertRaises(BTCPayError):
            obj.create_invoice(ORDER, 2500)
    def test_settlement_is_read_only(self):
        obj = Fixture()
        obj.invoice["status"] = "Settled"
        self.assertEqual(obj.verified_status("invoice_123", ORDER, 2500), "Settled")
    def test_invalid_invoice(self):
        obj = Fixture()
        with self.assertRaises(ValueError):
            obj.get_invoice("../../../fake")
    def test_no_insecure_origin(self):
        with self.assertRaises(ValueError):
            BTCPayClient("http://localhost", "store", "fixture", "fixture")

if __name__ == "__main__":
    unittest.main()
