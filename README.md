# SatGate ⚡ — Bitcoin checkout proof of concept

**Status:** Public, open-source, **simulation-only** checkout demo. No Bitcoin or Lightning payment is performed. This repository is **not** a production payment processor, and it is **not yet registered** in any hackathon.

## What it does

- Python standard-library HTTP server and SQLite persistence.
- Server-controlled prices: Supporter (2,500 sat) and Builder (10,000 sat).
- Idempotent demo invoice creation, random order identifiers and a browser storefront.
- Explicitly simulated settlement, for a demo without funds.
- MIT license and GitHub Actions tests.

## Run locally

```bash
python3 -m unittest discover -s tests -v
python3 src/satgate.py
```

Then open http://127.0.0.1:8765 and create a demo invoice.

**Safety:** The `/api/demo/settle` route simulates completion and cannot be used as evidence of a real payment. Run it only locally; do not publicly expose it. There is no login, rate limiting, payment gateway, webhook verification, merchant administration, or live settlement in **this GitHub version**.

## Upcoming work

The extended SatGate v2 candidate package includes a separate BTCPay API adapter and additional tests, but **those files are not yet mirrored in this GitHub repository**. The GitHub version should not be described as BTCPay-integrated until the extended package has been added and reviewed.

**Hackathon:** La Crypta has published conflicting October 2026 listings: a historical INTEGRATION page and a newer LABITCONF event. Registration, eligibility and deadlines must be confirmed before submission.

## License

MIT — see [LICENSE](LICENSE).
