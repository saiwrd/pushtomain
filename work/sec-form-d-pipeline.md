# SEC Form D Pipeline

*The Workshop · 10 — Joel Martinez, pushtomain.xyz*

> Pulls newly-funded companies straight from SEC EDGAR and qualifies each with a two-tier AI agent — going to the source instead of a brittle third-party tracker.

**Stack:** Python · SEC EDGAR · LLM scoring

## Key numbers

- **14,749** — qualifying companies filtered
- **~99K** — raw SEC filings processed across 7 fiscal quarters
- **~24s** — end-to-end backfill runtime

## The problem

Outbound and content needed a dependable stream of B2B companies that had just raised a Series A/B — the freshest possible "why now." The off-the-shelf funding tracker a predecessor had relied on quietly stopped working, and the prompts around it were too narrow to trust.

## What I built

A Python pipeline that pulls Form D filings directly from SEC EDGAR — bulk mode for backfills, daily mode for fresh filers — then parses, filters to a fundraising sweet spot, and runs each surviving company through a two-tier AI qualification agent. Going straight to the government source sidestepped the brittle vendor tracker entirely.

## The result

- 14,749 qualifying companies filtered from ~99,086 raw issuer filings across seven fiscal quarters.
- The full backfill ran end-to-end in about 24 seconds.
- Daily mode surfaces newly-funded companies within a day of filing.
The claim here is the pipeline and its verified run counts — not a polished, always-on data product.

---
HTML version: https://pushtomain.xyz/work/sec-form-d-pipeline/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
