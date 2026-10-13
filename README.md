# SatGate ⚡

Open-source Bitcoin/Lightning checkout **prototype**, currently demonstrated without real payments.

🌐 **Interactive browser demo:** https://trelliz.github.io/satgate/  
📦 **Code:** https://github.com/Trelliz/satgate  
🧪 **CI:** https://github.com/Trelliz/satgate/actions

> **Important:** The hosted GitHub Pages demo simulates invoices and settlements in the browser. It neither requests nor receives cryptocurrency. A simulated success is never proof of payment.

## Implemented

- Python standard-library HTTP demo server with SQLite, server-controlled prices and idempotent orders.
- A simulated invoice workflow for the local app and static website.
- Optional **BTCPay Server Greenfield adapter** in `src/btcpay_client.py`, including exact satoshi-to-BTC conversion, invoice-to-order binding checks, server-side invoice status lookup, HMAC-SHA256 webhook signature validation, and disabled HTTP redirects.
- Automated unit tests via GitHub Actions.
- Open-source MIT license and Spanish pitch.

## Run locally

```bash
python3 -m unittest discover -s tests -v
python3 src/satgate.py
```

Open http://127.0.0.1:8765. The server starts in simulation mode, bound to localhost.

The BTCPay adapter has **isolated mocked tests**, but is **not yet wired into the demo HTTP application**. No real Bitcoin payment, testnet/regtest transaction, or end-to-end webhook workflow has been verified. Consult [integration notes](docs/INTEGRATION.md).

## To become production capable

We need a BTCPay testnet/regtest instance, checkout API wiring, authenticated merchant access, TLS, webhook replay resilience, rate limiting, proper handling of unsettled/expired invoices, monitoring, and security review.

Never deploy the included demo settlement endpoint publicly or use it to fulfill paid products.

## Hackathon status

La Crypta's 2026 GitHub site still describes an older October `INTEGRATION` event, while their current developer site advertises a forthcoming `LABITCONF` hackathon starting October 30. We have contacted the organizers to confirm the applicable competition, remote eligibility, permitted AI usage and prior-development rules. **We have not registered or submitted SatGate.**

## License

MIT — see [LICENSE](LICENSE).
