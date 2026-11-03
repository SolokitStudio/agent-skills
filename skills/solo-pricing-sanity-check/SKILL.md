---
name: solo-pricing-sanity-check
description: "Checks whether a digital product's price makes sense against comparable products, the buyer's alternative, and the user's own catalog, and recommends a price and launch discount with reasoning. Use when the user asks what to charge, whether a price is too high or low, or how to price a bundle or launch code."
license: MIT
metadata:
  author: "Solokit Studio"
  version: "1.0.0"
  repository: "https://github.com/SolokitStudio/agent-skills"
---

# Pricing Sanity Check

Checks whether a digital product's price makes sense against comparable products, the buyer's alternative, and the user's own catalog, and recommends a price and launch discount with reasoning.

## When to use (trigger)

- "What should I charge for this?" / "Is $49 too much?"
- "How should I price the bundle / tiers / launch discount?"
- The user has views but no sales and suspects price.

## Inputs

Ask for any required input that is missing before you start. Do not fill gaps with guesses.

- Product contents and format (required).
- Current or proposed price (required for a check; optional for a recommendation).
- Target buyer and what they'd do without this product (their alternative).
- Comparable products with prices and links, if the user has them. If you can browse, you may look them up and must link each one.
- The user's other products and prices (to avoid cannibalizing).

## Steps

1. Write the buyer's alternative in one line (DIY time, a free tool, hiring someone) and what it costs them. Use the user's numbers; if none, label the estimate `assumption` and show it.
2. List comparables in a table with price, what's included, and source link. Mark any without a source `unverified`. Do not fabricate comparables; if you have none, say so.
3. Check catalog fit: does this price undercut or overlap the user's own products? Flag bundles priced above the sum of parts or below the cheapest item.
4. Run three sanity tests: (a) **effort test**: does the contents list look worth the price at a glance? (b) **impulse test**: is it under the buyer's no-approval threshold (state the threshold as an assumption); (c) **regret test**: would a buyer who skims the files feel short-changed?
5. Recommend one price, an optional launch code (price and end date), and the single change that would most justify a higher price.
6. List what data would change the recommendation (e.g. 'if 20+ visits convert at 0% at $19, test $12').

## Output format

```markdown
# Pricing check: <product>
Current: <price> | Recommendation: <price> (launch code <code> → <price> until <date>)
## Buyer's alternative
## Comparables
| Product | Price | Includes | Source |
## Catalog fit
## Tests
- Effort: pass/fail: <why>
- Impulse: pass/fail: <why, threshold assumption>
- Regret: pass/fail: <why>
## What would change this
```

## Worked example

**Input:** "Notion client portal template, 7 pages, $59. My other products are $15–$29."

**Output (excerpt):**
```markdown
Current: $59 | Recommendation: $29 (code LAUNCH → $24 until <date>)
## Catalog fit
$59 is 2x your next-highest product with fewer pages than your $29 CRM; buyers browsing your store will compare them.
## Comparables
No comparables provided and none looked up. [[PLACEHOLDER: add 3 competing listings with links]]
## Tests
- Effort: fail at $59: 7 pages reads as an afternoon's work
```

## Honesty rules

- Never present a guessed competitor price as fact. Every comparable needs a link or the label `unverified`.
- Do not promise that a price change will increase sales.
- Never invent numbers, quotes, names, testimonials, links, or results. Use only what the user gave you, what you computed from it (show the math), or what you opened and can link.
- Mark anything missing as `[[PLACEHOLDER: what's needed]]` and list all placeholders at the end of your output.
- Say what you could not see or check. "Not checked" is a valid answer; a guess presented as fact is not.
- Draft only: never send, post, publish, purchase, refund, or delete on the user's behalf from this skill. The user reviews and acts.
- No income, savings, or guaranteed-results claims in anything written for the public.
