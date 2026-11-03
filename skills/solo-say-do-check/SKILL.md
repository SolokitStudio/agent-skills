---
name: solo-say-do-check
description: "Compares what was promised or claimed (by you, a contractor, or an AI agent: 'I sent it', 'done', 'refunded', 'posted') against evidence of what was actually done, and flags every gap. Use when the user asks 'did this actually happen?', wants to verify an agent's or contractor's report, reconcile a status update, or audit claims before reporting to a client or customer."
license: MIT
metadata:
  author: "Solokit Studio"
  version: "1.0.0"
  repository: "https://github.com/SolokitStudio/agent-skills"
---

# Say-Do Check

Compares what was promised or claimed (by you, a contractor, or an AI agent: 'I sent it', 'done', 'refunded', 'posted') against evidence of what was actually done, and flags every gap.

## When to use (trigger)

- "My agent says it posted and sent the emails, did it?"
- "Check this status report against what actually happened."
- "Before I tell the client it's done, verify everything."

## Inputs

Ask for any required input that is missing before you start. Do not fill gaps with guesses.

- The claims: a status report, agent output, chat log, or task list marked done (required).
- Evidence sources available: links, screenshots, sent folder, logs, files, dashboards, or tools you can query (required, at least one).
- Optional: the original request or promise (what was supposed to happen).

## Steps

1. Split the claims into atomic, checkable statements (one action each): 'sent proposal to Dana', 'refunded $45', 'posted on LinkedIn'.
2. For each claim, define the evidence that would prove it (sent email in Sent folder, refund line in payment dashboard, public post URL).
3. Check each claim against the evidence you can actually access. Record what you looked at.
4. Label each claim: **Verified** (evidence seen), **Contradicted** (evidence shows otherwise), **Unverified** (couldn't check), **Partial** (some of it done).
5. If the original request is given, also list **Promised but not claimed**: things that were supposed to happen and nobody reported.
6. Write a corrected status line the user can safely repeat to others, using only Verified items.

## Output format

```markdown
# Say-do check: <report/source> (<date>)
| # | Claim | Evidence needed | Checked | Result |
Verified: n | Contradicted: n | Unverified: n | Partial: n
## Promised but not claimed
## Safe status line
"<only verified facts>"
## Follow-ups
```

## Worked example

**Input:** Agent report: "Sent the proposal to Dana, refunded the $45 order, and posted the update on LinkedIn." User provides: Sent folder access, Stripe screenshot, LinkedIn profile URL.

**Output:**
```markdown
| 1 | Sent proposal to Dana | email in Sent | Sent folder | Contradicted: proposal is in Drafts, not Sent |
| 2 | Refunded $45 | refund in Stripe | screenshot | Partial: refund shows "pending" |
| 3 | Posted update on LinkedIn | public post URL | profile | Verified: <post URL> |
## Safe status line
"The LinkedIn update is live, the $45 refund is pending in Stripe, and the proposal to Dana is drafted but not sent yet."
```

## Honesty rules

- Nothing is Verified without evidence you actually looked at. The claim itself is not evidence.
- Say exactly what you checked; 'I couldn't access X' is a valid, required answer.
- Never invent numbers, quotes, names, testimonials, links, or results. Use only what the user gave you, what you computed from it (show the math), or what you opened and can link.
- Mark anything missing as `[[PLACEHOLDER: what's needed]]` and list all placeholders at the end of your output.
- Say what you could not see or check. "Not checked" is a valid answer; a guess presented as fact is not.
- Draft only: never send, post, publish, purchase, refund, or delete on the user's behalf from this skill. The user reviews and acts.
- No income, savings, or guaranteed-results claims in anything written for the public.
