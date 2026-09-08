# Tech PE portfolio accounts

Evergreen GTM list of PE firms and their portfolio companies. Seeded from the [GEIG top 18 technology PE firms](https://growthequityinterviewguide.com/private-equity/private-equity-primer/technology-private-equity-firms). Extra portfolio URLs (like [Accel-KKR](https://www.accel-kkr.com/portfolio/)) can be registered and re-scraped anytime.

## Refresh

```bash
python3 tools/pe-portfolio-accounts/build.py
```

Add another public portfolio page:

```bash
python3 tools/pe-portfolio-accounts/build.py \
  --add-url "https://example-pe.com/portfolio/" \
  --name "Example PE"
```

`--enrich` visits company pages on auto-added firms to guess websites (slow). Accel-KKR already does this on every refresh.

Stdlib only.

## What to send the team

| File | Use |
|---|---|
| `data/unique_current_accounts.csv` | Best working list — names currently marked current on a live portfolio page |
| `data/current_accounts.csv` | Same, but one row per sponsor |
| `data/unique_accounts.csv` | Full universe including prior / Wikipedia / article mentions |
| `data/portfolio_accounts.csv` | Firm × company, with status, description, region, website when we have it |
| `data/pe_firms.csv` | Sponsor roster and last refresh time |

Accel-KKR rows include **current vs prior**, a one-line description, region, and a guessed company website.

Filter `pe_multi_sector=no` if you want software-weighted names only.

## Sources

1. Official portfolio pages (preferred)
2. Wikipedia `* companies` categories (Blackstone / KKR / Carlyle block scrapes)
3. Named investments from the GEIG article
4. Public deal coverage for Vitruvian (JS-only grid)
5. Anything in `sources.json`

## Caveats

- “Current” is only as current as the firm’s public page.
- Platinum paginates in-browser; first tile set only.
- Re-run the script when someone drops a new URL — don’t hand-merge CSVs.
