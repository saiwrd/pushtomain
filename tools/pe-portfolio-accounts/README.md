# Tech PE portfolio account list

GTM account universe: portfolio companies of the [top 18 technology private equity firms](https://growthequityinterviewguide.com/private-equity/private-equity-primer/technology-private-equity-firms) on Growth Equity Interview Guide.

The article is a subjective city-by-city list, not an AUM ranking. Featured firms plus honorable mentions are all included.

## Refresh

```bash
python3 tools/pe-portfolio-accounts/build.py
```

Stdlib only. Writes three CSVs under `data/`.

## Outputs

| File | Grain |
|---|---|
| `data/pe_firms.csv` | The 18 seed firms (HQ, featured vs honorable mention, company count) |
| `data/portfolio_accounts.csv` | One row per firm × company |
| `data/unique_accounts.csv` | Deduped companies; `pe_firms` lists every sponsor that holds them |

`pe_multi_sector=yes` means the sponsor invests well beyond software (Blackstone, KKR, Carlyle, Warburg, Permira, Platinum, Genstar, Providence, WCAS). Filter those out if you want a software-weighted TAM.

## Sources

1. **Official portfolio pages** (preferred)
2. **Wikipedia `* companies` categories** (includes former holdings; useful when a site is Cloudflare-blocked)
3. **Named “select investments”** from the GEIG article
4. **Public deal coverage** for Vitruvian (their grid is JavaScript-only)

Blackstone, KKR, and Carlyle block automated fetches of their own sites, so those three are Wikipedia-heavy.

## Caveats

- Public portfolios mix current and exited names. Status is `current` only when the live page says so.
- Platinum’s site paginates in the browser; the scraper sees the first tile set.
- Vitruvian’s investments page is client-rendered; holdings come from public deal coverage, not a live portfolio scrape.
- Company websites are not enriched here. Next step is a Clay/Apollo waterfall on `unique_accounts.csv`.
