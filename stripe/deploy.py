#!/usr/bin/env python3
"""Sync stripe/catalog.json into the Stripe account for the current secret key.

Test and live are separate Stripe environments. Point STRIPE_SECRET_KEY at
sk_test_... to build in the sandbox, then the same catalog at sk_live_...
to deploy live. Live deploys require --live.
"""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_PATH = ROOT / ".env"
CATALOG_PATH = ROOT / "catalog.json"
RECIPE_META = "recipe_id"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


def stripe_request(secret: str, method: str, path: str, fields: dict | None = None) -> dict:
    url = f"https://api.stripe.com/v1{path}"
    data = None
    headers = {"Authorization": f"Bearer {secret}"}
    if fields is not None:
        data = urllib.parse.urlencode(flatten(fields)).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=ssl.create_default_context()) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        body = err.read().decode()
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"error": {"message": body}}
        message = payload.get("error", {}).get("message", body)
        raise SystemExit(f"Stripe {method} {path} failed ({err.code}): {message}") from err


def flatten(value, prefix: str = "") -> dict[str, str]:
    items: dict[str, str] = {}
    if isinstance(value, dict):
        for key, inner in value.items():
            next_prefix = f"{prefix}[{key}]" if prefix else str(key)
            items.update(flatten(inner, next_prefix))
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            next_prefix = f"{prefix}[{index}]"
            items.update(flatten(inner, next_prefix))
    elif value is None:
        pass
    elif isinstance(value, bool):
        items[prefix] = "true" if value else "false"
    else:
        items[prefix] = str(value)
    return items


def list_all(secret: str, path: str, extra: dict | None = None) -> list[dict]:
    records: list[dict] = []
    params = {"limit": "100"}
    if extra:
        params.update(extra)
    starting_after = None
    while True:
        query = dict(params)
        if starting_after:
            query["starting_after"] = starting_after
        qs = urllib.parse.urlencode(query, doseq=True)
        page = stripe_request(secret, "GET", f"{path}?{qs}")
        records.extend(page.get("data", []))
        if not page.get("has_more"):
            break
        starting_after = records[-1]["id"]
    return records


def key_mode(secret: str) -> str:
    if secret.startswith("sk_test_"):
        return "test"
    if secret.startswith("sk_live_"):
        return "live"
    raise SystemExit("STRIPE_SECRET_KEY must start with sk_test_ or sk_live_")


def find_product(existing: list[dict], recipe_id: str, name: str) -> dict | None:
    for product in existing:
        if product.get("metadata", {}).get(RECIPE_META) == recipe_id:
            return product
    matches = [p for p in existing if p.get("name") == name]
    if len(matches) == 1:
        return matches[0]
    return None


def price_matches(price: dict, spec: dict) -> bool:
    interval = spec.get("interval")
    recurring = price.get("recurring") or {}
    return (
        price.get("unit_amount") == spec["unit_amount"]
        and price.get("currency") == spec["currency"]
        and price.get("nickname") == spec.get("nickname")
        and (recurring.get("interval") if recurring else None) == interval
        and price.get("active", True)
    )


def sync_product(secret: str, spec: dict, existing: list[dict], dry_run: bool) -> dict:
    recipe_id = spec["recipe_id"]
    found = find_product(existing, recipe_id, spec["name"])
    payload = {
        "name": spec["name"],
        "description": spec.get("description") or "",
        "active": spec.get("active", True),
        "metadata": {RECIPE_META: recipe_id},
    }
    if found is None:
        print(f"  create product {recipe_id!r} ({spec['name']})")
        if dry_run:
            return {"id": f"dry_{recipe_id}", "dry_run": True}
        created = stripe_request(secret, "POST", "/products", payload)
        existing.append(created)
        return created

    print(f"  update product {recipe_id!r} -> {found['id']}")
    if dry_run:
        return found
    updated = stripe_request(secret, "POST", f"/products/{found['id']}", payload)
    found.update(updated)
    return updated


def sync_price(secret: str, product_id: str, spec: dict, dry_run: bool) -> None:
    lookup_key = spec["lookup_key"]
    listed = stripe_request(
        secret,
        "GET",
        "/prices?" + urllib.parse.urlencode({"lookup_keys[]": lookup_key, "limit": "1"}),
    )
    current = listed["data"][0] if listed.get("data") else None

    create_fields = {
        "product": product_id,
        "unit_amount": spec["unit_amount"],
        "currency": spec["currency"],
        "nickname": spec.get("nickname") or "",
        "lookup_key": lookup_key,
        "transfer_lookup_key": True,
        "metadata": {RECIPE_META: lookup_key},
    }
    if spec.get("interval"):
        create_fields["recurring"] = {"interval": spec["interval"]}

    if current is None:
        print(f"    create price {lookup_key!r} ${spec['unit_amount'] / 100:.2f}")
        if not dry_run:
            stripe_request(secret, "POST", "/prices", create_fields)
        return

    if price_matches(current, spec) and current.get("product") == product_id:
        print(f"    unchanged price {lookup_key!r} ({current['id']})")
        return

    print(f"    replace price {lookup_key!r} ({current['id']} -> new)")
    if dry_run:
        return
    stripe_request(secret, "POST", f"/prices/{current['id']}", {"active": False})
    stripe_request(secret, "POST", "/prices", create_fields)


def sync_payment_method_preferences(
    secret: str, enabled: list[str], disabled: list[str], dry_run: bool
) -> None:
    if not enabled and not disabled:
        return
    if dry_run:
        if enabled:
            print(f"  would enable payment methods: {', '.join(enabled)}")
        if disabled:
            print(f"  would disable payment methods: {', '.join(disabled)}")
        return
    configs = list_all(secret, "/payment_method_configurations")
    if not configs:
        print("  no payment method configurations found")
        return
    overlap = set(enabled) & set(disabled)
    if overlap:
        raise SystemExit(f"Payment methods listed as both enabled and disabled: {', '.join(sorted(overlap))}")
    for config in configs:
        if config.get("active") is False:
            continue
        fields: dict = {}
        changes: list[str] = []
        unchanged: list[str] = []
        missing: list[str] = []

        def apply(method: str, preference: str) -> None:
            details = config.get(method)
            if not isinstance(details, dict):
                missing.append(method)
                return
            current = (details.get("display_preference") or {}).get("preference")
            if current == preference:
                unchanged.append(f"{method}={preference}")
                return
            fields[method] = {"display_preference": {"preference": preference}}
            changes.append(f"{method}->{preference}")

        for method in enabled:
            apply(method, "on")
        for method in disabled:
            apply(method, "off")
        label = config.get("name") or config["id"]
        if missing:
            print(f"  {label}: not on this account ({', '.join(missing)})")
        if unchanged and not changes:
            print(f"  {label}: already set ({', '.join(unchanged)})")
        if changes:
            print(f"  {label}: {', '.join(changes)}")
            stripe_request(secret, "POST", f"/payment_method_configurations/{config['id']}", fields)


def archive_extra_prices(secret: str, product_id: str, keep_lookup_keys: set[str], dry_run: bool) -> None:
    extras = list_all(secret, "/prices", {"product": product_id, "active": "true"})
    for price in extras:
        lookup = price.get("lookup_key")
        if lookup in keep_lookup_keys:
            continue
        print(f"    archive extra price {price['id']} (lookup_key={lookup or 'none'})")
        if not dry_run:
            stripe_request(secret, "POST", f"/prices/{price['id']}", {"active": False})


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy stripe/catalog.json to Stripe")
    parser.add_argument("--catalog", default=str(CATALOG_PATH), help="Path to catalog.json")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without calling Stripe writes")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Required when STRIPE_SECRET_KEY is a live key",
    )
    args = parser.parse_args()
    load_env(ENV_PATH)

    secret = os.environ.get("STRIPE_SECRET_KEY", "").strip()
    if not secret:
        raise SystemExit(
            "Set STRIPE_SECRET_KEY (sk_test_... or sk_live_...) in the environment or stripe/.env"
        )

    mode = key_mode(secret)
    if mode == "live" and not args.live:
        raise SystemExit("Refusing to write to live Stripe. Re-run with --live")
    if mode == "test" and args.live:
        raise SystemExit("STRIPE_SECRET_KEY is a test key; omit --live")

    catalog = json.loads(Path(args.catalog).read_text())
    products = catalog.get("products") or []
    print(f"Stripe mode: {mode}{' (dry-run)' if args.dry_run else ''}")
    print(f"Catalog: {args.catalog} ({len(products)} products)")

    existing = [] if args.dry_run else list_all(secret, "/products")
    for spec in products:
        product = sync_product(secret, spec, existing, args.dry_run)
        if args.dry_run:
            for price in spec.get("prices") or []:
                print(f"    would sync price {price['lookup_key']!r}")
            continue
        lookup_keys = {price["lookup_key"] for price in spec.get("prices") or []}
        for price in spec.get("prices") or []:
            sync_price(secret, product["id"], price, args.dry_run)
        archive_extra_prices(secret, product["id"], lookup_keys, args.dry_run)

    payment_methods = catalog.get("payment_methods") or {}
    enabled = payment_methods.get("enabled") or []
    disabled = payment_methods.get("disabled") or []
    if enabled or disabled:
        print("Payment methods:")
        sync_payment_method_preferences(secret, enabled, disabled, args.dry_run)

    defaults = catalog.get("invoice_defaults") or {}
    if defaults:
        methods = defaults.get("payment_method_types") or []
        method_note = f", methods {', '.join(methods)}" if methods else ""
        print(
            "Invoice defaults (used when you create invoices, not copied as account branding): "
            f"{defaults.get('collection_method')}, due in {defaults.get('days_until_due')} days"
            f"{method_note}"
        )
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
