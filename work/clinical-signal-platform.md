# Clinical Signal Platform

*The Workshop · 08 — Joel Martinez, pushtomain.xyz*

> An eight-stage data platform for a chronic-care company — practice intelligence, billing, care-team, and compliance signals pulled from many sources into one pipeline.

**Stack:** Python · Postgres · LLM extraction · Data governance

## Key numbers

- **4,948** — practices loaded from vendor + public sources
- **0** — exclusion misses across 4,561 providers screened against a live federal dataset
- **8** — data blocks in one pipeline: intelligence, billing, care-team, compliance

## The problem

A chronic-care-management company needed one signal-driven data platform pulling practice intelligence, billing behavior, care-team makeup, and compliance status from a mix of public and vendor sources — instead of stitching spreadsheets together by hand every time they wanted to target.

## What I built

An eight-stage pipeline, Postgres-backed, that flows from foundation data through site classification, job-posting signals, care-team mapping, billing signals, federal exclusion screening, competitive density, and contact enrichment. An LLM extraction step pulls structured facts off scraped practice sites; a governance layer — run, event, and sync audit logs — tracks every stage, so every signal has provenance and full data lineage. It syncs to the CRM on a schedule.

## The result

- 4,948 practices and 8,110 contacts loaded, with 100% of contacts linked to a practice by a stable identifier — no fuzzy matching.
- 2,569 care-team members mapped across 1,434 practices.
- 0 federal exclusion matches across 4,561 providers screened against a live ~80,000-record government dataset.
- Competitive density computed for every practice in the set.
Built and run end-to-end — I frame this as a platform I built and operated, not a hands-off production service.

---
HTML version: https://pushtomain.xyz/work/clinical-signal-platform/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
