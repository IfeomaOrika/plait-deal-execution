# Deal Desk Policy — Design Notes

This document explains the reasoning behind the approval-routing logic in
`02_route_deal.py`. The code shows *what* the rules are; this explains *why*,
what alternatives were rejected, and where the model's limits are.

The routing logic is a from-scratch implementation of the deal-desk approval
layer that commercial CPQ (Configure, Price, Quote) platforms — Salesforce CPQ,
DealHub, and similar — provide as configurable rules. Production teams buy those
platforms; this project models the logic layer directly to make the design
reasoning visible, which is normally hidden inside a vendor's configuration UI.

## The product context

Plait is a self-serve analytics product with Free / Team / Business tiers.
Typical paid deals sit in the ~$3k–15k range. Deals are small and close fast,
which matters for how much approval friction the desk can tolerate: if every
routine discount needs a manager, the desk becomes the bottleneck and slows the
motion the product depends on.

## Discount tiers

The core design decision. Discount routing is **tiered**, not a single cutoff:

| Discount | Routes to |
|---|---|
| up to 15% | auto-approve |
| 15–30% | sales manager |
| above 30% | leadership |

**Why these lines sit where they do.** List price is not set at cost-plus-margin;
it is set above it, with discount headroom deliberately built in so there is room
to give ground in a negotiation. A discount *inside* that headroom is using room
the price was designed to give away — it is not eroding real margin. That is the
reasoning behind the three tiers, which map to three states of that headroom:

- **Up to 15% — inside the headroom.** The rep is operating within the cushion
  the price was built with. Requiring approval here adds friction without
  protecting anything, and on small fast deals that friction is expensive.
- **15–30% — eating into the headroom.** Past comfortable discretion but not yet
  into real margin. A manager sanity-checks; leadership isn't needed.
- **Above 30% — past the headroom, into real margin.** At this point the discount
  is consuming actual margin rather than built-in padding. That is a decision
  above a rep's or a manager's authority, so it escalates to leadership.

**Alternative rejected: a single cutoff.** The first version used one line —
any discount over 15% routed to a sales manager. This was the weakest part of
the policy: it treated a 16% discount and a 50% discount identically, sending
both to the same approver. But those are different events — one is routine
negotiation, the other is a margin emergency — and a policy whose entire purpose
is margin protection should distinguish them. Tiering is what makes the rule
actually govern the thing it exists to govern.

## Deal size

Deals at or above **$25k ACV** route to leadership regardless of discount.
The absolute number matters less than the ratio: at a typical deal of ~$8k,
$25k is roughly 3x a normal deal. A deal several times larger than usual carries
concentration risk and unusual commitments a founder or VP wants visibility into,
independent of how it was discounted. (If a deal is both large and deeply
discounted, it routes to leadership once, not twice.)

## Non-standard terms

Anything other than standard monthly or annual billing routes to **finance**.
The reason is specifically *not* size or discount — it is billing and
revenue-recognition risk. Custom payment schedules or non-standard terms can
change how and when revenue is recognized, which is a finance and compliance
question rather than a sales one. This is why the gate is finance, not a manager.

## Gates accumulate

A single deal can trip several conditions and require several sign-offs. The
logic collects every gate that applies rather than returning the first match, so
a large deal with non-standard terms correctly requires both leadership and
finance. Accumulation (rather than a highest-gate-wins model) reflects that these
are independent concerns — size risk and revenue-recognition risk are different
questions that different people own.

## What this model does and does not demonstrate

Stated plainly, because the boundary matters:

- The rules are validated for **execution** — the logic routes each deal to the
  correct gate, proven by the test cases in `02_route_deal.py`. Every branch is
  exercised.
- The rules are **not** validated for **outcome**. The thresholds are grounded in
  pricing structure and in how real CPQ desks set bands, but they are not tuned
  against Plait's actual won/lost or margin data, because Plait is synthetic and
  no such data exists. A production deal desk would set these lines against real
  margin analysis and revisit them as the business learned.
- What the project demonstrates is therefore **design judgment** — the ability to
  reason about approval structure under real constraints — not conversion
  efficacy. That is the deliberate scope. The logic layer is where the judgment
  lives; validating it against outcomes is a separate problem that requires real
  data.
