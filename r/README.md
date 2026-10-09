# Client results

Unlisted, read-only weekly reports. No sign-in. Each client gets a folder. The page reads `data.json` next to it, so a new week is a JSON replace.

Do not link these from the nav, the sitemap, or `llms.txt`. The page sends `noindex,nofollow`.

## Demo

[r/demo/](demo/) is Acme Co. Every name and number is fake.

## New client

1. Pick a slug: `r/<client>-<token>/`. Example: `r/northwind-k7m2p9/`. The token is unguessable; the folder name is the only access control.
2. Copy `r/demo/index.html` into that folder. Do not edit it.
3. Add `data.json` beside it. Start from `r/demo/data.json`.
4. Set `"sample": false` and replace the numbers. Open `/r/<client>-<token>/` and check the three ranges.

Shared CSS lives at `r/report.css`. The HTML file is the template; copy it again if the template changes.

## Schema

`data.json`:

| Field | Type | Meaning |
| --- | --- | --- |
| `client` | string | Client name, shown in the header. |
| `sample` | boolean | `true` marks the page as fake. Real reports use `false`. |
| `updated` | string | ISO date (`YYYY-MM-DD`) the figures run through. |
| `defaultPeriod` | string | `id` of the period selected on load. |
| `note` | string | One sentence under the totals. Optional. |
| `weeklyCall` | object | Latest call. Not period-specific. |
| `weeklyCall.when` | string | Display date, e.g. `Friday, October 9`. |
| `weeklyCall.minutes` | number | Length of the call. |
| `weeklyCall.bullets` | string[] | 3–4 plain sentences. |
| `campaigns` | object[] | Active campaigns. Not period-specific. |
| `campaigns[].name` | string | Campaign name. |
| `campaigns[].channel` | string | `Email`, `Phone`, or `LinkedIn`. |
| `campaigns[].done` | number | Units completed. |
| `campaigns[].total` | number | Units planned. |
| `campaigns[].unit` | string | What `done` counts: `sent`, `dials`, `requests`. |
| `campaigns[].note` | string | Short result line. |
| `periods` | object[] | One entry per range button, in display order. |

Each period:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | URL hash and button value. Use `this-week`, `last-week`, `all-time`. |
| `label` | string | Button label. |
| `range` | string | Date range beside the buttons. |
| `deltaLabel` | string or null | Comparison phrase, e.g. `vs last week`. `null` hides deltas. |
| `summary` | string | The one-sentence headline. Write it to match `totals`. |
| `totals` | object[] | Four headline numbers, in order. |
| `totals[].key` | string | `reached`, `replies`, `positive`, or `meetings`. |
| `totals[].label` | string | Caption under the number. |
| `totals[].value` | number | The number. |
| `totals[].delta` | number or null | Change vs the previous period. `null` hides it. |
| `channels` | object[] | Cold calling, LinkedIn, then Email. |
| `channels[].id` | string | `calling`, `linkedin`, or `email`. |
| `channels[].label` | string | Section heading. |
| `channels[].meetings` | number | Meetings from this channel, if meetings is not already a step. Optional. |
| `channels[].steps` | object[] | Funnel, widest stage first. |
| `channels[].steps[].key` | string | Stage id. See below. |
| `channels[].steps[].label` | string | Stage label. |
| `channels[].steps[].value` | number or null | Count. `null` omits the stage (use this when opens are unavailable). |
| `activityCaption` | string | Line above the chart. |
| `activity` | object[] | Seven days. |
| `activity[].label` | string | Day abbreviation. |
| `activity[].date` | string | Display date, used in the table and tooltips. |
| `activity[].reached` | number | People reached that day. |
| `activity[].replies` | number | Replies that day. |
| `activity[].meetings` | number | Meetings booked that day. |
| `replies` | object[] | Latest replies in this range, newest first. |
| `replies[].name` | string | Person. |
| `replies[].title` | string | Job title. |
| `replies[].company` | string | Company. |
| `replies[].channel` | string | `Email` or `LinkedIn`. |
| `replies[].when` | string | Short date, e.g. `Fri`. |
| `replies[].positive` | boolean | Interested, or asked to meet. |
| `replies[].snippet` | string | One short quote. No extra quotation marks. |

### Steps

Cold calling: `dials`, `connects`, `conversations`, `meetings`.

LinkedIn: `requests`, `accepted`, `replies`, `positive`. Put meetings on `channels[].meetings`.

Email: `sent`, `opened`, `replies`, `positive`, `bounces`.

- Omit `opened`, or set it to `null`, when open tracking is off. `0` means nobody opened.
- `bounces` is drawn as a line under the funnel, not as a bar.

### Keeping the numbers consistent

The page does not recompute totals. Match them when you edit JSON.

- People reached = calling connects + LinkedIn requests + emails delivered (sent − bounces).
- Replies = LinkedIn replies + email replies.
- Positive replies = LinkedIn positive + email positive.
- Meetings = calling meetings step + LinkedIn `meetings` + email `meetings`.
- For a week, the seven `activity` days sum to that period’s reached, replies, and meetings.
- `delta` is this period’s value minus the previous period’s value.
- All time has no delta. Its chart is the last 7 days, and `activityCaption` says so.
- A campaign’s `done` should sit inside the all-time total for that unit.

### Headline

`summary` is shown as written. A week reads like: “This week we reached 269 people, 20 replied, 6 positively, and booked 4 meetings.”
