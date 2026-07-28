# Merlin

*The Circus · 01 — Joel Martinez, pushtomain.xyz*

> A signal engine that finds companies the moment they raise capital, scores each with an AI propensity model, and surfaces the ranked results live — running entirely on Cloudflare.

**Stack:** Cloudflare · Workflows · Workers AI · D1
**Live:** https://merlin.pushtomain.xyz

## Key numbers

- **100%** — Cloudflare-native — no external infrastructure
- **0** — external API keys required to run it
- **0–100** — AI-scored ICP fit for every company found

## The idea

Modern go-to-market is a pipeline: watch for a buying signal, enrich the company behind it, decide whether it's worth pursuing, and put the ranked answer in front of someone. Merlin is that whole loop built as a working demonstration — proof that an entire GTM signal engine can run on an edge platform with no servers and no external services to babysit.

The signal it watches: companies that just raised capital, pulled from public SEC EDGAR Form D filings. The "why now" is baked into every record.

## What I built

A cron trigger kicks off weekly discovery (or you hit "Run now" on the dashboard). A durable, auto-retrying Workflow orchestrates the steps; Workers fan out to enrich each company; Workers AI acts as a propensity model, scoring each company's fit 0–100 against a configurable ICP and writing out its reasoning. Results land in a D1 database and render on a public dashboard served from the same Worker.

The ICP is a swappable definition — point the same engine at a different buyer and it re-scores against the new target. The first instance scores companies against a developer-platform / edge-infrastructure ICP.

## Why it's interesting

Every piece — scheduling, durable orchestration, the LLM agent, the database, the dashboard — is a Cloudflare primitive. It's the clearest way I've found to show that the infrastructure a GTM team used to need a stack of vendors for now fits inside one deployment.

---
HTML version: https://pushtomain.xyz/work/merlin/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
