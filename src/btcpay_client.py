"""BTCPay Server Greenfield invoice adapter for SatGate.

Prototype integration. Do not use for financial fulfillment until it has been
validated against your own BTCPay testnet/regtest instance and security-reviewed.
No API keys or wallets are bundled. Read-only status is verified server-side.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import re
import urllib.error
import urllib.request
from decimal import Decimal
from urllib.parse import urlsplit


class BTCPayError(RuntimeError):
    """A safe public-facing error; don't include authorization headers."""


class BTCPayClient:
    def __init__(self, origin: str, store_id: str, api_key: str, webhook_secret: str):
        parts = urlsplit(origin)
        if (
            parts.scheme != "https"
            or not parts.netloc
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or parts.path not in ("", "/")
            or parts.query
            or parts.fragment
        ):
            raise ValueError("BTCPay origin must be an HTTPS URL without a path or credentials")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", store_id):
            raise ValueError("Invalid store ID")
        if not all((api_key, webhook_secret)):
            raise ValueError("BTCPay API key and webhook secret are required")
        self.origin = origin.rstrip("/")
        self.store_id = store_id
        self._api_key = api_key
        self._webhook_secret = webhook_secret

    def _api(self, endpoint: str, body: dict | None = None) -> dict:
        url = f"{self.origin}/api/v1/stores/{self.store_id}/invoices{endpoint}"
        content = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(
            url,
            data=content,
            headers={
                "Authorization": "token " + self._api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST" if content is not None else "GET",
        )

        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, headers, newurl):
                return None

        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=12) as response:
                if int(response.headers.get("Content-Length", "0")) > 65536:
                    raise BTCPayError("Oversized provider response")
                result = json.load(response)
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            raise BTCPayError("BTCPay service unavailable or returned invalid data") from exc
        if not isinstance(result, dict):
            raise BTCPayError("Invalid provider response")
        return result

    def create_invoice(self, order_id: str, sats: int) -> dict:
        if not isinstance(order_id, str) or not re.fullmatch(r"[0-9a-f]{32}", order_id):
            raise ValueError("Invalid order ID")
        if isinstance(sats, bool) or not isinstance(sats, int) or not (1 <= sats <= 2_100_000_000_000_000):
            raise ValueError("Invalid satoshi amount")
        btc_amount = format(Decimal(sats) / Decimal(100_000_000), ".8f")
        invoice = self._api("", {
            "amount": btc_amount,
            "currency": "BTC",
            "metadata": {"orderId": order_id},
        })
        self.verify_binding(invoice, order_id, sats)
        return invoice

    def get_invoice(self, invoice_id: str) -> dict:
        if not isinstance(invoice_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", invoice_id):
            raise ValueError("Invalid invoice ID")
        invoice = self._api("/" + invoice_id)
        if invoice.get("id") != invoice_id:
            raise BTCPayError("Invoice identifier mismatch")
        return invoice

    @staticmethod
    def verify_binding(invoice: dict, order_id: str, sats: int) -> None:
        """Never mark an order paid using an invoice for a different amount or order."""
        try:
            metadata = invoice["metadata"]
            verified = (
                bool(invoice["id"])
                and isinstance(metadata, dict)
                and metadata.get("orderId") == order_id
                and invoice["currency"] == "BTC"
                and Decimal(str(invoice["amount"])) == Decimal(sats) / Decimal(100_000_000)
            )
        except (TypeError, KeyError, ValueError, ArithmeticError):
            verified = False
        if not verified:
            raise BTCPayError("Invoice price or order binding mismatch")

    def verified_status(self, invoice_id: str, order_id: str, sats: int) -> str:
        invoice = self.get_invoice(invoice_id)
        self.verify_binding(invoice, order_id, sats)
        status = invoice.get("status")
        if status not in ("New", "Processing", "Settled", "Expired", "Invalid"):
            raise BTCPayError("Unknown payment status")
        return status

    def verify_webhook(self, raw_body: bytes, signature: str | None) -> bool:
        """BTCPAY-SIG uses HMAC-SHA256, computed on the exact raw HTTP body."""
        if not isinstance(raw_body, bytes) or not signature or not re.fullmatch(r"sha256=[0-9A-Fa-f]{64}", signature):
            return False
        expected = "sha256=" + hmac.new(
            self._webhook_secret.encode("utf-8"), raw_body, hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature.lower())
