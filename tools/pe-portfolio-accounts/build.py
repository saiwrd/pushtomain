#!/usr/bin/env python3
"""Build a GTM account universe from tech PE firms and their portfolio companies.

Seed list: Growth Equity Interview Guide's top 18 technology PE firms.
Primary source for companies: each firm's public portfolio page.
Fallback: Wikipedia categories + named investments from the article.

Usage:
    python3 tools/pe-portfolio-accounts/build.py
"""

from __future__ import annotations

import csv
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path

from firms import (
    ARTICLE_SELECT_INVESTMENTS,
    FIRMS,
    SEED_SOURCE_URL,
    VITRUVIAN_PUBLIC_HOLDINGS,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
WIKI_UA = "PEPortfolioAccounts/1.0 (GTM research; +https://pushtomain.xyz)"

SKIP_NAMES = {
    "",
    "our partner companies",
    "no companies matched that criteria.",
    "portfolio companies",
    "our portfolio",
    "our portfolio companies",
    "current investments",
    "prior investments",
    "see career opportunities across our portfolio.",
    "main navigation",
    "footer legal",
    "footer social",
    "footer cta 1",
    "footer cta 2",
    "san francisco",
    "london",
    "new york",
    "careers",
    "contact us",
    "reset filters",
}

OFFICES = {
    "chicago",
    "dallas",
    "london",
    "miami",
    "new york",
    "san francisco",
    "singapore",
    "hong kong",
    "austin",
}


def log(msg: str) -> None:
    print(msg, flush=True)


def fetch(url: str, *, wiki: bool = False, timeout: int = 40) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": WIKI_UA if wiki else UA,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_json(url: str, *, wiki: bool = False) -> object:
    return json.loads(fetch(url, wiki=wiki))


def strip_tags(blob: str) -> str:
    blob = re.sub(r"<script[\s\S]*?</script>", " ", blob, flags=re.I)
    blob = re.sub(r"<[^>]+>", " ", blob)
    blob = html.unescape(blob)
    return re.sub(r"\s+", " ", blob).strip()


def headings(html_text: str, tags: str = "234") -> list[str]:
    found = re.findall(rf"<h[{tags}][^>]*>(.*?)</h[{tags}]>", html_text, re.I | re.S)
    return [strip_tags(x) for x in found if strip_tags(x)]


def slug_to_name(slug: str) -> str:
    slug = urllib.parse.unquote(slug).replace("_", "-")
    parts = [p for p in slug.split("-") if p]
    small = {"and", "or", "of", "the", "in", "at", "for"}
    out = []
    for i, p in enumerate(parts):
        if i > 0 and p.lower() in small:
            out.append(p.lower())
        elif p.isupper() or (len(p) <= 3 and p.isalpha()):
            out.append(p.upper() if len(p) <= 3 else p.capitalize())
        else:
            out.append(p.capitalize())
    return " ".join(out)


def normalize_name(name: str) -> str:
    name = html.unescape(name or "")
    name = strip_tags(name)
    name = re.sub(r"\s+", " ", name).strip(" \t\n\r-–—|")
    name = re.sub(
        r"[\s,]*\((?:inc\.?|llc\.?|ltd\.?|corp\.?|co\.?|plc|formerly [^)]+)\)\s*$",
        "",
        name,
        flags=re.I,
    )
    name = re.sub(
        r",?\s+(?:inc\.?|llc\.?|ltd\.?|l\.p\.?|lp|corp\.?|co\.?|plc)\s*$",
        "",
        name,
        flags=re.I,
    )
    name = re.sub(r"\s+logo(?:\s.*)?$", "", name, flags=re.I)
    name = re.sub(r"\s+company$", "", name, flags=re.I)
    name = re.sub(r"^the\s+", "", name, flags=re.I)
    return name.strip()


def keep_name(name: str) -> bool:
    n = normalize_name(name)
    if len(n) < 2 or len(n) > 80:
        return False
    if n.lower() in SKIP_NAMES or n.lower() in OFFICES:
        return False
    if n.lower() in {"close", "twitter link", "linkedin link", "email icon"}:
        return False
    if "platinum equity" in n.lower():
        return False
    if n.lower().startswith("we ") or n.lower().startswith("for decades"):
        return False
    if "does not exist" in n.lower() or "page not found" in n.lower():
        return False
    if n.startswith("http"):
        return False
    return True


def record(name: str, *, source: str, source_url: str, status: str = "unknown",
           company_url: str = "") -> dict | None:
    cleaned = normalize_name(name)
    if not keep_name(cleaned):
        return None
    return {
        "account_name": cleaned,
        "investment_status": status,
        "source": source,
        "source_url": source_url,
        "company_url": company_url,
        "wikipedia_url": source_url if "wikipedia.org" in source_url else "",
    }


def wp_cpt(base: str, cpt: str, source: str) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while page <= 20:
        url = f"{base.rstrip('/')}/wp-json/wp/v2/{cpt}?per_page=100&page={page}"
        try:
            data = fetch_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code in (400, 404):
                break
            raise
        if not isinstance(data, list) or not data:
            break
        for item in data:
            title = item.get("title")
            if isinstance(title, dict):
                title = title.get("rendered", "")
            rec = record(
                str(title or ""),
                source=source,
                source_url=url.split("?")[0],
                status="current",
                company_url=str(item.get("link") or ""),
            )
            if rec:
                rows.append(rec)
        if len(data) < 100:
            break
        page += 1
        time.sleep(0.25)
    return rows


def wikipedia_category(category: str | None) -> list[dict]:
    if not category:
        return []
    rows: list[dict] = []
    cont: dict[str, str] = {}
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category}",
            "cmnamespace": "0",
            "cmlimit": "500",
            "format": "json",
        }
        params.update(cont)
        url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
        data = fetch_json(url, wiki=True)
        members = data.get("query", {}).get("categorymembers", [])
        for m in members:
            title = m.get("title") or ""
            if title.startswith("List of ") or title.startswith("Category:"):
                continue
            wiki = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_"))
            rec = record(title, source="wikipedia", source_url=wiki, status="unknown",
                         company_url=wiki)
            if rec:
                rec["wikipedia_url"] = wiki
                rows.append(rec)
        cont = data.get("continue") or {}
        if not cont:
            break
        time.sleep(0.2)
    return rows


def adapter_silver_lake() -> list[dict]:
    return wp_cpt("https://www.silverlake.com", "portfolio", "official_site")


def adapter_hellman_friedman() -> list[dict]:
    rows = wp_cpt("https://hf.com", "portfolio", "official_site")
    # H&F mixes thought-leadership tiles into the CPT; drop obvious non-companies.
    cleaned = []
    for r in rows:
        if r["account_name"].lower().startswith("ode with "):
            continue
        cleaned.append(r)
    return cleaned


def adapter_vista() -> list[dict]:
    return wp_cpt("https://www.vistaequitypartners.com", "company", "official_site")


def adapter_accel_kkr() -> list[dict]:
    html_text = fetch("https://www.accel-kkr.com/portfolio/")
    rows = []
    for name in headings(html_text, "23"):
        rec = record(name, source="official_site",
                     source_url="https://www.accel-kkr.com/portfolio/", status="unknown")
        if rec:
            rows.append(rec)
    return rows


def adapter_francisco() -> list[dict]:
    html_text = fetch("https://www.franciscopartners.com/investments")
    slugs = re.findall(r'href="/investments/([a-z0-9][a-z0-9\-]*)"', html_text)
    rows = []
    for slug in dict.fromkeys(slugs):
        rec = record(
            slug_to_name(slug),
            source="official_site",
            source_url="https://www.franciscopartners.com/investments",
            status="unknown",
            company_url=f"https://www.franciscopartners.com/investments/{slug}",
        )
        if rec:
            rows.append(rec)
    return rows


def adapter_genstar() -> list[dict]:
    html_text = fetch("https://www.gencap.com/companies/")
    rows = []
    for name in headings(html_text, "2"):
        rec = record(name, source="official_site",
                     source_url="https://www.gencap.com/companies/", status="current")
        if rec:
            rows.append(rec)
    return rows


def adapter_thoma_bravo() -> list[dict]:
    html_text = fetch("https://www.thomabravo.com/portfolio")
    payloads = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)', html_text)
    joined = "".join(payloads).encode("utf-8").decode("unicode_escape")
    names = re.findall(r'"name"\s*:\s*"([^"\\]{2,80})"', joined)
    ui = {
        "next.metadataoutlet", "next.metadata", "next-size-adjust", "viewport",
        "description", "twitter:card", "twitter:title", "twitter:description",
        "twitter:image", "status", "all", "current investments", "prior investments",
        "sector", "applications", "cybersecurity", "infrastructure", "location",
    }
    rows = []
    seen = set()
    for name in names:
        if name.lower() in ui or name.lower() in OFFICES:
            continue
        if name.lower() == name and " " not in name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        rec = record(name, source="official_site",
                     source_url="https://www.thomabravo.com/portfolio", status="unknown")
        if rec:
            rows.append(rec)
    return rows


def adapter_providence() -> list[dict]:
    html_text = fetch("https://www.provequity.com/portfolio")
    skip = {"main navigation", "portfolio companies", "footer legal", "footer social",
            "footer cta 1", "footer cta 2"}
    rows = []
    for name in headings(html_text, "2"):
        if name.lower() in skip:
            continue
        rec = record(name, source="official_site",
                     source_url="https://www.provequity.com/portfolio", status="current")
        if rec:
            rows.append(rec)
    return rows


def adapter_spectrum() -> list[dict]:
    html_text = fetch("https://www.spectrumequity.com/portfolio")
    alts = re.findall(r'<img[^>]+alt="([^"]+)"', html_text)
    rows = []
    for alt in alts:
        if not re.search(r"logo", alt, re.I):
            continue
        name = re.sub(r"\s+logo.*$", "", alt, flags=re.I)
        rec = record(name, source="official_site",
                     source_url="https://www.spectrumequity.com/portfolio", status="unknown")
        if rec:
            rows.append(rec)
    return rows


def adapter_warburg() -> list[dict]:
    html_text = fetch("https://www.warburgpincus.com/investments/")
    slugs = re.findall(
        r'href="https://warburgpincus.com/investments/([^"/]+)/?"', html_text
    )
    rows = []
    for slug in dict.fromkeys(slugs):
        rec = record(
            slug_to_name(slug),
            source="official_site",
            source_url="https://www.warburgpincus.com/investments/",
            status="unknown",
            company_url=f"https://warburgpincus.com/investments/{slug}/",
        )
        if rec:
            rows.append(rec)
    return rows


def adapter_wcas() -> list[dict]:
    url = "https://wcas.com/firm/investments/"
    html_text = fetch(url)
    names = headings(html_text, "2")
    rows = []
    for name in names:
        rec = record(name, source="official_site", source_url=url, status="unknown")
        if rec:
            rows.append(rec)
    return rows


def adapter_permira() -> list[dict]:
    html_text = fetch("https://www.permira.com/portfolio/our-portfolio")
    rows = []
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.S)
    names: list[str] = []
    if m:
        blob = m.group(1)
        names = re.findall(r'"name"\s*:\s*"([^"]{2,80})"', blob)
    if not names:
        names = headings(html_text, "3")
    for name in names:
        rec = record(name, source="official_site",
                     source_url="https://www.permira.com/portfolio/our-portfolio",
                     status="current")
        if rec:
            rows.append(rec)
    return rows


def adapter_hg() -> list[dict]:
    html_text = fetch("https://hgcapital.com/portfolio")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_text, re.S)
    rows = []
    if not m:
        return rows
    data = json.loads(m.group(1))
    items = (
        data.get("props", {})
        .get("pageProps", {})
        .get("data", {})
        .get("total", {})
        .get("items", [])
    )
    for item in items:
        rec = record(
            item.get("title") or "",
            source="official_site",
            source_url="https://hgcapital.com/portfolio",
            status="unknown",
        )
        if rec:
            rows.append(rec)
    return rows


def adapter_platinum() -> list[dict]:
    html_text = fetch("https://www.platinumequity.com/our-companies/")
    alts = re.findall(r'<img[^>]+alt="([^"]+)"', html_text)
    skip = {"platinum equity", "platinum equity logo"}
    rows = []
    for alt in alts:
        name = strip_tags(alt)
        if name.lower() in skip or "icon" in name.lower() or name.lower().startswith("image of"):
            continue
        rec = record(name, source="official_site",
                     source_url="https://www.platinumequity.com/our-companies/",
                     status="current")
        if rec:
            rows.append(rec)
    return rows


def adapter_vitruvian() -> list[dict]:
    # Public page is client-rendered; use repeatedly cited public holdings.
    rows = []
    for name in VITRUVIAN_PUBLIC_HOLDINGS:
        rec = record(
            name,
            source="public_reports",
            source_url="https://en.wikipedia.org/wiki/Vitruvian_Partners",
            status="unknown",
        )
        if rec:
            rows.append(rec)
    return rows


ADAPTERS = {
    "silver_lake": adapter_silver_lake,
    "accel_kkr": adapter_accel_kkr,
    "hellman_friedman": adapter_hellman_friedman,
    "francisco_partners": adapter_francisco,
    "genstar": adapter_genstar,
    "vista": adapter_vista,
    "thoma_bravo": adapter_thoma_bravo,
    "providence": adapter_providence,
    "spectrum": adapter_spectrum,
    "warburg": adapter_warburg,
    "wcas": adapter_wcas,
    "permira": adapter_permira,
    "hg": adapter_hg,
    "platinum": adapter_platinum,
    "vitruvian": adapter_vitruvian,
    "wikipedia_only": lambda: [],
}


def merge_rows(firm: dict, batches: list[list[dict]]) -> list[dict]:
    by_key: dict[str, dict] = {}
    for batch in batches:
        for row in batch:
            key = row["account_name"].lower()
            if key not in by_key:
                by_key[key] = {
                    "account_name": row["account_name"],
                    "pe_firm": firm["name"],
                    "pe_firm_id": firm["firm_id"],
                    "pe_hq_city": firm["hq_city"],
                    "pe_hq_region": firm["hq_region"],
                    "pe_list_role": firm["list_role"],
                    "pe_multi_sector": "yes" if firm["multi_sector"] else "no",
                    "investment_status": row["investment_status"],
                    "sources": [row["source"]],
                    "source_urls": [row["source_url"]] if row.get("source_url") else [],
                    "company_url": row.get("company_url") or "",
                    "wikipedia_url": row.get("wikipedia_url") or "",
                    "firm_portfolio_url": firm["portfolio_url"],
                }
                continue
            existing = by_key[key]
            if row["source"] not in existing["sources"]:
                existing["sources"].append(row["source"])
            if row.get("source_url") and row["source_url"] not in existing["source_urls"]:
                existing["source_urls"].append(row["source_url"])
            if row.get("company_url") and not existing["company_url"]:
                existing["company_url"] = row["company_url"]
            if row.get("wikipedia_url") and not existing["wikipedia_url"]:
                existing["wikipedia_url"] = row["wikipedia_url"]
            # Prefer current over unknown.
            rank = {"current": 3, "prior": 2, "unknown": 1}
            if rank.get(row["investment_status"], 0) > rank.get(existing["investment_status"], 0):
                existing["investment_status"] = row["investment_status"]
            # Prefer official-site spelling when Wikipedia comes first.
            if row["source"] == "official_site":
                existing["account_name"] = row["account_name"]
    out = []
    for item in by_key.values():
        item["sources"] = "|".join(item["sources"])
        item["source_urls"] = "|".join(item["source_urls"])
        out.append(item)
    out.sort(key=lambda r: r["account_name"].lower())
    return out


def unique_accounts(pairs: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in pairs:
        groups[row["account_name"].lower()].append(row)
    unique = []
    for rows in groups.values():
        firms = sorted({r["pe_firm"] for r in rows})
        unique.append({
            "account_name": rows[0]["account_name"],
            "pe_firm_count": len(firms),
            "pe_firms": " | ".join(firms),
            "pe_firm_ids": "|".join(sorted({r["pe_firm_id"] for r in rows})),
            "any_multi_sector_sponsor": "yes" if any(r["pe_multi_sector"] == "yes" for r in rows) else "no",
            "sources": "|".join(sorted({s for r in rows for s in r["sources"].split("|") if s})),
            "company_url": next((r["company_url"] for r in rows if r["company_url"]), ""),
            "wikipedia_url": next((r["wikipedia_url"] for r in rows if r["wikipedia_url"]), ""),
        })
    unique.sort(key=lambda r: (-int(r["pe_firm_count"]), r["account_name"].lower()))
    return unique


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build() -> None:
    firm_rows = []
    pair_rows: list[dict] = []
    failures: list[str] = []

    for firm in FIRMS:
        log(f"→ {firm['name']}")
        batches: list[list[dict]] = []
        adapter = ADAPTERS[firm["adapter"]]
        try:
            official = adapter()
            log(f"  official: {len(official)}")
            batches.append(official)
        except Exception as exc:  # noqa: BLE001 — keep going across firms
            msg = f"{firm['name']} official scrape failed: {exc}"
            log(f"  ! {msg}")
            failures.append(msg)
            batches.append([])

        try:
            wiki = wikipedia_category(firm.get("wiki_category"))
            log(f"  wikipedia: {len(wiki)}")
            batches.append(wiki)
        except Exception as exc:  # noqa: BLE001
            msg = f"{firm['name']} wikipedia failed: {exc}"
            log(f"  ! {msg}")
            failures.append(msg)
            batches.append([])

        article = []
        for name in ARTICLE_SELECT_INVESTMENTS.get(firm["firm_id"], []):
            rec = record(
                name,
                source="geig_article",
                source_url=SEED_SOURCE_URL,
                status="unknown",
            )
            if rec:
                article.append(rec)
        batches.append(article)

        merged = merge_rows(firm, batches)
        log(f"  merged unique: {len(merged)}")
        pair_rows.extend(merged)
        firm_rows.append({
            "firm_id": firm["firm_id"],
            "name": firm["name"],
            "hq_city": firm["hq_city"],
            "hq_region": firm["hq_region"],
            "list_role": firm["list_role"],
            "multi_sector": "yes" if firm["multi_sector"] else "no",
            "website": firm["website"],
            "portfolio_url": firm["portfolio_url"],
            "wiki_category": firm.get("wiki_category") or "",
            "seed_source_url": SEED_SOURCE_URL,
            "portfolio_company_count": len(merged),
        })
        time.sleep(0.3)

    unique = unique_accounts(pair_rows)
    write_csv(
        DATA / "pe_firms.csv",
        firm_rows,
        [
            "firm_id", "name", "hq_city", "hq_region", "list_role", "multi_sector",
            "website", "portfolio_url", "wiki_category", "seed_source_url",
            "portfolio_company_count",
        ],
    )
    write_csv(
        DATA / "portfolio_accounts.csv",
        pair_rows,
        [
            "account_name", "pe_firm", "pe_firm_id", "pe_hq_city", "pe_hq_region",
            "pe_list_role", "pe_multi_sector", "investment_status", "sources",
            "source_urls", "company_url", "wikipedia_url", "firm_portfolio_url",
        ],
    )
    write_csv(
        DATA / "unique_accounts.csv",
        unique,
        [
            "account_name", "pe_firm_count", "pe_firms", "pe_firm_ids",
            "any_multi_sector_sponsor", "sources", "company_url", "wikipedia_url",
        ],
    )
    (DATA / "run_log.txt").write_text(
        "\n".join(
            [
                f"seed: {SEED_SOURCE_URL}",
                f"firms: {len(firm_rows)}",
                f"firm-company pairs: {len(pair_rows)}",
                f"unique accounts: {len(unique)}",
                "failures:",
                *(failures or ["none"]),
                "",
            ]
        ),
        encoding="utf-8",
    )
    log(
        f"\nDone. {len(firm_rows)} firms, {len(pair_rows)} pairs, "
        f"{len(unique)} unique accounts → {DATA}"
    )
    if failures:
        log("Some sources failed; see data/run_log.txt")
        sys.exit(0)


if __name__ == "__main__":
    build()
