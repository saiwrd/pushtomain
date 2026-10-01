# Stripe catalog

Edit `catalog.json`, then push it into Stripe. Test and live do not share products, so the same file is the recipe for both.

```bash
cd stripe
cp .env.example .env
# put sk_test_... in .env
python3 deploy.py --dry-run
python3 deploy.py
```

Live (real money) needs the live secret key and an explicit flag:

```bash
# put sk_live_... in .env
python3 deploy.py --live
```

Amounts in the catalog are cents. Changing a price archives the old Stripe price and creates a new one with the same lookup key. Customers and invoices stay in the environment that created them.

The GTM retainer has two prices: $7,000 per month, or $15,666 prepaid for 3 months (25.4% off). Prepaid is a one-time invoice, not an auto-renewing subscription. Steer prepaid to ACH.
