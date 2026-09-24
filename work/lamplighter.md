# Lamplighter

*The Circus · 02. Joel Martinez, pushtomain.xyz*

> Type any company and see its go-to-market stack. What they run, who they buy from. Fingerprinted live from the edge, then read back to you as a plain-English take.

**Stack:** Cloudflare · Workers AI · Edge
**Live:** https://lamplighter.pushtomain.xyz

## The idea

Knowing what a company runs. Their CRM, their outbound tooling, their analytics. Tells you how to sell to them and who they already trust. That intelligence usually lives behind a paid tool. Lamplighter does it live, from a URL, for free.

## What I built

A Cloudflare Worker that fetches a company's public surface and fingerprints the go-to-market technology it exposes. Then Workers AI does a "field read". It takes the raw list of detected tools and summarizes it into a short GTM interpretation: what this stack implies about how they operate and where an opening might be.

All of it runs at the edge. No scraper farm, no external infrastructure. Just a request in and a read back.

---
HTML version: https://pushtomain.xyz/work/lamplighter/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
