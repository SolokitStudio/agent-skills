---
name: solo-product-page-audit
description: "Audits a product or sales page (Gumroad, Shopify, Notion Marketplace, landing page) for why visitors don't buy, and returns a prioritized fix list. Use when the user says they get views/visits but no sales, asks to review or roast a product page, or pastes a listing URL or text for feedback."
license: MIT
metadata:
  author: "Solokit Studio"
  version: "1.0.0"
  repository: "https://github.com/SolokitStudio/agent-skills"
---

# Product Page Audit

Audits a product or sales page (Gumroad, Shopify, Notion Marketplace, landing page) for why visitors don't buy, and returns a prioritized fix list.

## When to use (trigger)

- "People visit but nobody buys, what's wrong with my page?"
- "Audit / review / roast my product page."
- The user shares a listing URL, screenshot, or pasted copy and asks for feedback.

## Inputs

Ask for any required input that is missing before you start. Do not fill gaps with guesses.

- The page itself: URL (if you can browse), pasted text, or screenshots (required).
- Price and the audience the user is targeting.
- Optional: real traffic and sales numbers for the period (views, sales, conversion), and where traffic comes from.

## Steps

1. Confirm what you could actually see (full page, text only, screenshot of the top fold). Say what you couldn't see.
2. Score the page 0–2 on each of 10 checks: (1) clear in 5 seconds what it is; (2) who it's for; (3) outcome stated, not features only; (4) proof of contents (previews, screenshots, demo, sample); (5) price matches perceived effort/value; (6) objections answered (FAQ, compatibility, format); (7) refund/risk reversal visible; (8) one clear call to action; (9) maker credibility; (10) mobile readability (only if you saw a mobile view; otherwise mark `not checked`).
3. For each score below 2, quote the exact text or describe the exact element that caused it.
4. If the user gave numbers, compute conversion = sales ÷ views and show the arithmetic. If not, don't estimate.
5. Write a fix list ordered by impact ÷ effort: **Fix today** (≤ 30 min each), **This week**, **Later**. Each fix includes rewritten copy where applicable.
6. Flag anything that may be a store-policy or legal issue (income claims, fake scarcity, unlicensed images) separately.

## Output format

```markdown
# Page audit: <product>
Seen: <what you reviewed> | Not seen: <gaps>
| # | Check | Score (0-2) | Evidence |
Total: <n>/20 (of checks actually scored)
## Fix today
1. <fix> → Rewrite: "<new copy>"
## This week
## Later
## Policy flags
```

## Worked example

**Input:** pasted Gumroad text for "Ultimate Content OS ($49)". User says 212 views, 0 sales last 30 days, traffic from LinkedIn.

**Output (excerpt):**
```markdown
Seen: pasted description text only | Not seen: cover, previews, mobile layout
| 4 | Proof of contents | 0 | No screenshots or page list; text says "everything you need" |
| 7 | Refund visible | 0 | No refund line anywhere in the text |
Conversion: 0 sales ÷ 212 views = 0.0%
## Fix today
1. Add a "What's inside" list with page names and counts. Rewrite: "Inside: 9 linked Notion databases: Ideas, Drafts, Calendar, ..."
2. Add: "Not for you? Reply within 14 days for a full refund." (only if you offer this)
```

## Honesty rules

- Score only what you saw. Unseen checks are `not checked`, not 0 and not 2.
- Do not cite industry conversion benchmarks unless you have a source the user can open.
- Never invent numbers, quotes, names, testimonials, links, or results. Use only what the user gave you, what you computed from it (show the math), or what you opened and can link.
- Mark anything missing as `[[PLACEHOLDER: what's needed]]` and list all placeholders at the end of your output.
- Say what you could not see or check. "Not checked" is a valid answer; a guess presented as fact is not.
- Draft only: never send, post, publish, purchase, refund, or delete on the user's behalf from this skill. The user reviews and acts.
- No income, savings, or guaranteed-results claims in anything written for the public.
