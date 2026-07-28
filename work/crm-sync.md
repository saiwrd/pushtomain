# CRM Sync Automations

*The Workshop · 12 — Joel Martinez, pushtomain.xyz*

> Idempotent cron jobs that push LinkedIn and cold-email activity into HubSpot — auto-creating contacts, notes, and tasks, and routing hot replies to a rep the moment they land.

**Stack:** Python · HubSpot API · Cron

## Key numbers

- **2,214** — leads synced into the CRM (plus 170 cold-call leads)
- **10** — live campaigns feeding the sync
- **0** — duplicate records — state-tracked and fully idempotent

## The problem

LinkedIn and cold-email activity lived in separate tools and never made it into the CRM with enough context for a rep to act on. The rule was strict: a task shouldn't fire until every field it depends on is actually populated — no half-formed records nagging the team.

## What I built

A set of idempotent, state-file-tracked cron jobs that sync activity into HubSpot over its REST API — auto-creating contacts, logging notes, creating tasks, and raising a high-priority task the instant a positive reply arrives. The state tracking is really governance over what reaches the CRM: because every run knows what it's already done, re-running is safe and never duplicates.

## The result

- 2,214 leads synced across 10 live campaigns, plus 170 cold-call leads.
- Counts come from machine-generated run records — not projections.
- Hot replies routed to the right rep automatically, with full context attached.

---
HTML version: https://pushtomain.xyz/work/crm-sync/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
