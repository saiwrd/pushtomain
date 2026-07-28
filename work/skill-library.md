# GTM Skill Library

*The Workshop · 13 — Joel Martinez, pushtomain.xyz*

> A reusable harness that packages recurring go-to-market operations — enrichment, campaign setup, reply classification, domain provisioning — as parameterized skills invoked by trigger phrase.

**Stack:** CLI · Reusable tooling · API docs

## Key numbers

- **80%** — verified enrichment hit rate on a real cohort (56 of 70)
- **6+** — packaged operations: enrichment, campaigns, replies, domains…
- **0** — pipelines rebuilt from scratch per new client

## The problem

Rebuilding the same go-to-market pipelines for every new client was the bottleneck. The work was recurring — enrich a list, set up a campaign, classify replies, provision domains — but each rebuild relearned the same API quirks and lost the same hours.

## What I built

A library of documented, parameterized skills with uniform interfaces, invoked by trigger phrase — governance over work that's usually ad hoc, so recurring operations run the same way every time. Each one carries a reference file capturing the hard-won details — the header a certain provider silently requires, the field that has to be an array not a string, the auth scheme that isn't what the docs imply — so the next run doesn't rediscover them the hard way.

## The result

- Enrichment verified at an 80% hit rate on a real cohort (56 of 70).
- Spinning up a new client's execution became cheap — reuse instead of rebuild.
- The captured API quirks turned recurring pain into a one-time cost.

---
HTML version: https://pushtomain.xyz/work/skill-library/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
