# SatGate · BTCPay Greenfield integration

## Current development status

The public GitHub Pages demo is **a simulation**. It does not communicate with this adapter or with a payment processor.

The backend now includes `src/btcpay_client.py`, an optional BTCPay Server Greenfield API client. It can request an invoice in BTC (exact satoshi conversion), fetch invoice details, validate invoice-to-order bindings, reject off-host HTTP redirects, and verify signed webhook bodies. Its unit tests use mocked responses and **do not prove live BTC payments work**.

**Do not expose it as a payment service or deliver purchased goods until it has been tested in BTCPay testnet/regtest with full server-side status processing, proper authentication, rate limits, TLS, monitoring, webhook replay protection, and operational security.**

## Configure for local experiments

Use environment variables or a private `.env`:

- `BTCPAY_URL`: your own BTCPay Server HTTPS origin.
- `BTCPAY_STORE_ID`: the BTCPay store identifier.
- `BTCPAY_API_KEY`: a **least-privilege** Greenfield token; do not share or commit.
- `BTCPAY_WEBHOOK_SECRET`: randomly generated webhook secret; do not share or commit.

The adapter is imported by developers/tests; the current demo HTTP server continues to operate exclusively in simulation mode. Wiring the backend into a real checkout flow is the next implementation step.

Run locally:
```sh
python3 -m unittest discover -s tests -v
```

## Honest demonstration

Browser showcase: https://trelliz.github.io/satgate/

Repository: https://github.com/Trelliz/satgate

The website shows a local UI simulation. It does not produce a Lightning invoice, an LNURL, or a QR code for payment.
