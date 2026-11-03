# Contributing

Thanks for helping improve these skills. Small, focused pull requests are easiest to review.

## Good contributions

- **Skill fixes:** a step that produces wrong or vague output, a missing input the skill should ask for, or an honesty rule the skill breaks in practice. Include the prompt you used and what the agent returned.
- **New install paths:** another agent that reads Agent Skills. Link the tool's documentation for the folder it reads.
- **Examples:** a reproducible input and output under `examples/<skill>/`, with fictional data only.
- **Installer and CI fixes.**

New skills are out of scope for this repo for now. Open an issue first if you have one in mind.

## Development

Requirements: Bash 3.2 or later, Python 3.9 or later with PyYAML, and optionally [ShellCheck](https://www.shellcheck.net/).

```bash
git clone https://github.com/SolokitStudio/agent-skills.git
cd agent-skills
pip install pyyaml
python3 scripts/validate.py      # checks every skills/*/SKILL.md
bash tests/test_install.sh       # installer tests in a throwaway HOME
shellcheck install.sh tests/test_install.sh
```

CI runs the same three checks on every pull request, on Linux and macOS.

## Skill rules

Every `SKILL.md` must:

1. Start with YAML frontmatter that uses only the spec keys: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
2. Use a `name` that matches its folder, in kebab-case, starting with `solo-`.
3. Keep `description` under 1024 characters and say both what the skill does and when to use it.
4. Contain these sections, in order: `When to use (trigger)`, `Inputs`, `Steps`, `Output format`, `Worked example`, `Honesty rules`.
5. Keep the shared honesty rules: no invented numbers, quotes, names or links; mark gaps as `[[PLACEHOLDER: ...]]`; say what was not checked; draft only.

`scripts/validate.py` enforces 1 to 4.

## Pull requests

- One change per pull request, with a clear description of what changed and why.
- If you change a skill's behavior, show before and after output from a real run and name the tool you used.
- Update `CHANGELOG.md` under `Unreleased`.

By contributing, you agree that your contribution is licensed under the MIT License.
