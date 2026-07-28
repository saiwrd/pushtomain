# Reply → Slack Relay

*The Workshop · 12 — Joel Martinez, pushtomain.xyz*

> A single Cloudflare Worker that turns cold-email replies into rich Slack alerts for any client — one deployment serving everyone, instead of a bespoke webhook each time.

**Stack:** Cloudflare Worker · Webhooks · Multi-tenant

## Key numbers

- **1** — Worker serving every client
- **~2 min** — to onboard a new client — one secret, one webhook
- **24/7** — always-on, serverless, no infrastructure to run

## The problem

Every new client wanted the same thing: a Slack ping the moment a prospect replied to a campaign. Building a one-off webhook integration per client meant repeating the same plumbing over and over and maintaining all of it forever.

## What I built

One Cloudflare Worker that accepts a per-client path, looks up that client's Slack webhook from Worker secrets, and transforms the incoming reply event into a formatted Slack message — a header, structured fields, the quoted reply, and a button that opens the lead straight in the campaign tool. Adding a client is a single secret plus one webhook configuration.

## The result

- Multiple client slugs live on a single deployment.
- A new client goes live in about two minutes.
- Always-on and serverless — nothing to provision, nothing to patch.

---
HTML version: https://pushtomain.xyz/work/reply-slack-relay/
Contact: joel@pushtomain.xyz · https://www.linkedin.com/in/joelrmartinez/
