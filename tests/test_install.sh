#!/usr/bin/env bash
# Installer tests. Every case runs against a throwaway HOME, so nothing on
# your machine is touched.
#
#   bash tests/test_install.sh                 # local tests
#   TEST_REMOTE=1 AGENT_SKILLS_REF=<sha> bash tests/test_install.sh
#                                              # also test "curl | bash" against GitHub
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL="$ROOT/install.sh"
SKILL_COUNT="$(find "$ROOT/skills" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
PASS=0; FAIL=0
WORK="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-test.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT

fresh_home() { local h; h="$(mktemp -d "$WORK/home.XXXXXX")"; echo "$h"; }
count() { if [ -d "$1" ]; then find "$1" -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' '; else echo 0; fi; }
ok()   { PASS=$((PASS + 1)); echo "ok   $1"; }
bad()  { FAIL=$((FAIL + 1)); echo "FAIL $1"; }
expect_eq() { if [ "$2" = "$3" ]; then ok "$1"; else bad "$1 (expected $3, got $2)"; fi; }

# 1. default: user scope, all tools
H="$(fresh_home)"
HOME="$H" bash "$INSTALL" >/dev/null
expect_eq "default installs to ~/.claude/skills" "$(count "$H/.claude/skills")" "$SKILL_COUNT"
expect_eq "default installs to ~/.agents/skills" "$(count "$H/.agents/skills")" "$SKILL_COUNT"

# 2. each tool installs only to its own folder
for pair in claude:.claude cursor:.cursor codex:.agents gemini:.gemini; do
  tool="${pair%%:*}"; dir="${pair#*:}"
  H="$(fresh_home)"
  HOME="$H" bash "$INSTALL" --tool "$tool" >/dev/null
  expect_eq "--tool $tool installs to ~/$dir/skills" "$(count "$H/$dir/skills")" "$SKILL_COUNT"
  others="$(find "$H" -mindepth 1 -maxdepth 1 ! -name "$dir" | wc -l | tr -d ' ')"
  expect_eq "--tool $tool touches nothing else" "$others" "0"
done

# 3. installed files are identical to the source
H="$(fresh_home)"
HOME="$H" bash "$INSTALL" --tool claude >/dev/null
if diff -r "$ROOT/skills" "$H/.claude/skills" >/dev/null; then ok "installed files match source"; else bad "installed files match source"; fi

# 4. project scope
H="$(fresh_home)"; P="$(mktemp -d "$WORK/proj.XXXXXX")"
HOME="$H" bash "$INSTALL" --scope project --dir "$P" --tool codex >/dev/null
expect_eq "--scope project installs into <dir>/.agents/skills" "$(count "$P/.agents/skills")" "$SKILL_COUNT"
expect_eq "--scope project leaves HOME alone" "$(find "$H" -mindepth 1 | wc -l | tr -d ' ')" "0"

# 5. existing skills are skipped, --force overwrites
H="$(fresh_home)"
HOME="$H" bash "$INSTALL" --tool claude >/dev/null
echo "local edit" > "$H/.claude/skills/solo-say-do-check/NOTE.txt"
out="$(HOME="$H" bash "$INSTALL" --tool claude)"
case "$out" in *"0 installed, $SKILL_COUNT skipped"*) ok "re-run skips existing skills" ;; *) bad "re-run skips existing skills" ;; esac
expect_eq "skip keeps local edits" "$([ -f "$H/.claude/skills/solo-say-do-check/NOTE.txt" ] && echo yes || echo no)" "yes"
HOME="$H" bash "$INSTALL" --tool claude --force >/dev/null
expect_eq "--force replaces the folder" "$([ -f "$H/.claude/skills/solo-say-do-check/NOTE.txt" ] && echo yes || echo no)" "no"

# 6. dry run changes nothing
H="$(fresh_home)"
HOME="$H" bash "$INSTALL" --dry-run >/dev/null
expect_eq "--dry-run changes nothing" "$(find "$H" -mindepth 1 | wc -l | tr -d ' ')" "0"

# 7. uninstall removes only this repo's skills
H="$(fresh_home)"
mkdir -p "$H/.claude/skills/someone-elses-skill" && echo x > "$H/.claude/skills/someone-elses-skill/SKILL.md"
HOME="$H" bash "$INSTALL" >/dev/null
HOME="$H" bash "$INSTALL" --uninstall >/dev/null
expect_eq "--uninstall removes this repo's skills" "$(count "$H/.agents/skills")" "0"
expect_eq "--uninstall keeps other skills" "$(count "$H/.claude/skills")" "1"

# 8. --link creates symlinks
H="$(fresh_home)"
HOME="$H" bash "$INSTALL" --tool gemini --link >/dev/null
expect_eq "--link creates symlinks" "$(find "$H/.gemini/skills" -mindepth 1 -maxdepth 1 -type l | wc -l | tr -d ' ')" "$SKILL_COUNT"

# 9. --list, --version, bad input
expect_eq "--list prints every skill" "$(bash "$INSTALL" --list | wc -l | tr -d ' ')" "$SKILL_COUNT"
case "$(bash "$INSTALL" --version)" in "agent-skills installer "*) ok "--version" ;; *) bad "--version" ;; esac
if bash "$INSTALL" --tool vim >/dev/null 2>&1; then bad "rejects unknown --tool"; else ok "rejects unknown --tool"; fi
if bash "$INSTALL" --bogus >/dev/null 2>&1; then bad "rejects unknown option"; else ok "rejects unknown option"; fi
if bash "$INSTALL" --scope project --dir "$WORK/missing" >/dev/null 2>&1; then bad "rejects missing --dir"; else ok "rejects missing --dir"; fi

# 10. remote: piped from stdin, downloads from GitHub (opt-in, needs network)
if [ "${TEST_REMOTE:-0}" = 1 ]; then
  H="$(fresh_home)"; C="$(mktemp -d "$WORK/cwd.XXXXXX")"
  (cd "$C" && HOME="$H" bash -s -- --tool claude < "$INSTALL" >/dev/null)
  expect_eq "curl | bash installs from GitHub (${AGENT_SKILLS_REF:-main})" "$(count "$H/.claude/skills")" "$SKILL_COUNT"
  expect_eq "curl | bash cleans up its temp folder" "$(find "$C" -mindepth 1 | wc -l | tr -d ' ')" "0"
fi

echo "$PASS passed, $FAIL failed"
[ "$FAIL" = 0 ]
