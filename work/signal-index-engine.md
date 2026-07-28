# Signal-Index Engine

*The Workshop · 11 — Joel Martinez, pushtomain.xyz*

> A propensity engine that scores thousands of brands on composite health signals, paired with a crash-safe enrichment pipeline that picks up exactly where it died.

**Stack:** Python · Systems architecture · Resilient ETL

## Key numbers

- **3,400+** — decision-maker contacts verified across runs
- **~2,800** — brands per sourced universe (industry × headcount × geo)
- **0** — records lost to a crash — the pipeline resumes from where it stopped

## The problem

A client needed to score thousands of consumer brands on composite "health" signals — repeatably, in a way that could be re-pointed at future clients — and to source and verify decision-makers at scale without losing hours of work every time a long enrichment run crashed.

## What I built

A reusable orchestrator with per-signal data-agent modules on a shared interface, driven by a per-tenant config file, feeding a leaderboard. Alongside it, an enrichment pipeline built to survive the real world: retries on connection resets, incremental write-and-flush so partial progress is always saved, per-record isolation so one bad row can't sink the batch, and resume-from-file so a restart skips everything already processed.

## The result

- 3,400+ decision-maker contacts verified across live runs.
- Brand universes of roughly 2,800 sourced by industry, employee band, and geography.
- Architected for multiple tenants on one common interface (one instantiated to date).

---
HTML version: https://pushtomain.xyz/work/signal-index-engine/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
