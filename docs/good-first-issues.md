# Good first issues

Drafts of the starter issues opened on GitHub at launch. Each one is self-contained and needs no knowledge of the rest of the codebase.

---

## 1. Add a reproducible example for `solo-product-page-audit`

**Labels:** good first issue, documentation

`examples/say-do-check/` shows the inputs, the prompt and the output for one skill, so anyone can rerun it. `solo-product-page-audit` has no example yet.

**What to do**

- Create `examples/product-page-audit/` with a fictional product listing (`listing.md`, 150 to 300 words, with a price and some traffic numbers), a `prompt.md`, and the `output.md` your agent produced.
- Add a short `README.md` in the folder, following `examples/say-do-check/README.md`.
- Name the agent and version you used in the pull request.

**Done when** the folder exists, all data is fictional, and the output follows the skill's `Output format` section.

---

## 2. Add a reproducible example for `solo-pricing-sanity-check`

**Labels:** good first issue, documentation

Same as the issue above, for the pricing skill.

**What to do**

- Create `examples/pricing-sanity-check/` with a fictional product description, a proposed price, the seller's other products and prices, a `prompt.md`, and the `output.md` your agent produced.
- Comparables must be fictional and labeled `unverified`, or real and linked.

**Done when** the output includes the buyer's alternative, the comparables table, the catalog-fit check and all three tests.

---

## 3. Add `install.ps1` for Windows without WSL

**Labels:** good first issue, enhancement

Windows users without WSL have to copy folders by hand today.

**What to do**

- Add `install.ps1` that copies each folder in `skills/` to `$HOME\.claude\skills` and `$HOME\.agents\skills` by default.
- Support `-Tool` (all, claude, cursor, codex, gemini), `-Force` and `-DryRun`, matching `install.sh`.
- Do not overwrite an existing folder unless `-Force` is passed.
- Document it in the README's Manual install section.

**Done when** the script runs on Windows PowerShell 5.1 and PowerShell 7. Bonus: a `windows-latest` CI job that runs it in a temporary profile folder.

---

## 4. Validator: check section order and add unit tests

**Labels:** good first issue, enhancement

`scripts/validate.py` checks that every required section exists, but not that the sections are in the documented order or that the file has a `# Title` line.

**What to do**

- Fail when the required `##` sections are out of order, or when there is no `# ` title after the frontmatter.
- Add `tests/test_validate.py` (standard-library `unittest`) with small fixture skills that pass and fail each rule.
- Run the new tests in the `validate` CI job.

**Done when** the existing skills still pass and every rule has a failing fixture.

---

## 5. Document more agents that read Agent Skills

**Labels:** good first issue, documentation

The README covers Claude Code, Cursor, Codex and Gemini CLI. Other agents also read the Agent Skills format.

**What to do**

- Pick one agent that documents support for `SKILL.md` skills.
- Add a row to the Manual install table with its user and project folders and a link to its documentation.
- If its folder differs from the ones `install.sh` already writes, open a follow-up issue rather than changing the installer in the same pull request.

**Done when** the row links to the agent's official documentation and you have confirmed the skills appear in that agent.
