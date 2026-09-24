# Connie

*The Circus · 03. Joel Martinez, pushtomain.xyz*

> An open-source Go engine that scans Ashby, Greenhouse, and Lever job boards concurrently. And remembers every posting she has ever seen. Job postings are hiring signals; Connie is the memory that makes them legible.

**Stack:** Go · SQLite · Concurrency · Open source
**Live:** https://github.com/saiwrd/connie

## Key numbers

- **3**. ATS platforms behind one adapter interface. More drop in at ~100 lines each
- **1**. Static binary, one direct dependency, cross-compiles anywhere
- **0**. Mutexes in the worker pool. Channel-owned state, proven by the race detector

## The idea

A job posting is a buying signal: it says what a company is about to invest in, the day they decide it. The public, unauthenticated APIs of the major applicant-tracking systems expose tens of thousands of boards. But a scraper that just fetches them tells you what exists, not what changed. The interesting tool is the one with memory.

Connie is named for Connie Sachs of Tinker Tailor Soldier Spy. The researcher whose head was the Registry. Ask her what's new, and she compares today against everything she has ever seen.

## What I built

A Go CLI with three faces: scan fetches thousands of boards through a bounded worker pool (a single aggregator goroutine owns all mutable state. No mutexes, proven under the race detector), filters by fuzzy title or description regex, and exports CSV/JSON. discover harvests board slugs from the Wayback Machine's CDX index, shape-filters the archive noise, and probes survivors against the live ATS. And the Registry. SQLite, one transaction per scan. Tracks first_seen, last_seen, and a deliberately conservative closed_at lifecycle: only a full unfiltered scan may declare a posting gone, scoped to the boards it actually covered, and a posting that reappears is reopened.

Built test-first throughout: fixtures recorded from one live session per API, ported semantics pinned table-for-table from the Python reference it grew out of, and a live smoke suite gated behind a build tag so CI never touches the network.

## The receipt

- On her second-ever run. 67 seed boards, three ATSes, zero errors. She surfaced a remote "AI GTM Architect (Revenue Operations)" posting that an Ashby-only sweep structurally could not see.
- Run her on a cron and the Registry diff becomes a feed: who started hiring for what, the day it opened.
- Open source at github.com/saiwrd/connie. The README's design notes are half the point.

---
HTML version: https://pushtomain.xyz/work/connie/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
