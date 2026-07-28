# Integrator's Exit

*The Workshop · 08 — Joel Martinez, pushtomain.xyz*

> A full custom pipeline built around an M&A / valuation-arbitrage thesis no one else was targeting — sourcing, AI qualification, a seven-dimension propensity model, and enrichment, all the way into the CRM.

**Stack:** Python · LLM scoring · HubSpot

## Key numbers

- **1,336** — companies sourced and AI-scored into the account universe
- **7** — scoring dimensions per company, each rated 0–100
- **778** — leadership contacts extracted and enriched

## The thesis

No competitor was targeting mid-market integration-services agencies as an M&A / valuation-arbitrage play, and the ideal profile wasn't something standard firmographic filters could capture. The opportunity was to define that universe from scratch and reach the owners before anyone else framed the pitch.

## What I built

An end-to-end pipeline: LinkedIn sourcing → a fast AI "gut-check" filter (a smaller model doing YES / MAYBE / NO triage) → a seven-dimension propensity model (a stronger model rating each company 0–100 with reasoning) → leadership extraction → a multi-provider enrichment waterfall → push scripts into HubSpot, with campaigns launched on top.

## The result

- 1,336-company scored account universe and 778 leadership contacts, assembled and pushed to the CRM.
- Outbound campaigns launched against the scored list.
- One sourcing cohort came in far below expectation — I root-caused it (LinkedIn keyword search misses ERP-channel partner directories) and documented the fix rather than papering over it.
I keep the honest miss in the story on purpose — the diagnosis is as much a part of the work as the build.

---
HTML version: https://pushtomain.xyz/work/integrators-exit/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
