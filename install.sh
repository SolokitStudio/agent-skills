#!/usr/bin/env bash
# Solokit Agent Skills installer
# https://github.com/SolokitStudio/agent-skills
#
# One command (macOS, Linux, WSL):
#   curl -fsSL https://raw.githubusercontent.com/SolokitStudio/agent-skills/main/install.sh | bash
#
# Pass options after "bash -s --":
#   curl -fsSL https://raw.githubusercontent.com/SolokitStudio/agent-skills/main/install.sh | bash -s -- --tool cursor
#
# Or from a clone:
#   ./install.sh [options]
set -euo pipefail

VERSION="1.0.0"
REPO="SolokitStudio/agent-skills"
REF="${AGENT_SKILLS_REF:-main}"

usage() {
  cat <<'USAGE'
Solokit Agent Skills installer

Usage: install.sh [options]

Options:
  --tool TOOL       all (default), claude, cursor, codex or gemini
  --scope SCOPE     user (default): every project for your account
                    project: one project folder (see --dir)
  --dir PATH        project root for --scope project (default: current directory)
  --link            symlink instead of copy (clone installs only)
  --force           overwrite skills that already exist at the destination
  --dry-run         print what would happen and change nothing
  --uninstall       remove this repo's skills from the destinations
  --list            list the skills and exit
  --version         print the installer version and exit
  -h, --help        show this help

Destinations:
  tool     user scope           project scope
  claude   ~/.claude/skills     <dir>/.claude/skills
  cursor   ~/.cursor/skills     <dir>/.cursor/skills
  codex    ~/.agents/skills     <dir>/.agents/skills
  gemini   ~/.gemini/skills     <dir>/.gemini/skills
  all      .claude/skills and .agents/skills
           (Claude Code reads .claude; Codex, Gemini CLI and Cursor read .agents)

Environment:
  AGENT_SKILLS_REF  git branch or tag to download when piped from curl (default: main)
USAGE
}

die() { echo "error: $*" >&2; exit 1; }

SCOPE="user"; TOOL="all"; DIR="$PWD"; LINK=0; FORCE=0; DRY=0; UNINSTALL=0; LIST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --tool)      [ $# -ge 2 ] || die "--tool needs a value"; TOOL="$2"; shift 2 ;;
    --tool=*)    TOOL="${1#*=}"; shift ;;
    --scope)     [ $# -ge 2 ] || die "--scope needs a value"; SCOPE="$2"; shift 2 ;;
    --scope=*)   SCOPE="${1#*=}"; shift ;;
    --dir)       [ $# -ge 2 ] || die "--dir needs a value"; DIR="$2"; shift 2 ;;
    --dir=*)     DIR="${1#*=}"; shift ;;
    --link)      LINK=1; shift ;;
    --force)     FORCE=1; shift ;;
    --dry-run)   DRY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --list)      LIST=1; shift ;;
    --version)   echo "agent-skills installer $VERSION"; exit 0 ;;
    -h|--help)   usage; exit 0 ;;
    *) die "unknown option: $1 (try --help)" ;;
  esac
done

case "$SCOPE" in user|project) ;; *) die "--scope must be user or project" ;; esac
case "$TOOL" in all|claude|cursor|codex|gemini) ;; *) die "--tool must be all, claude, cursor, codex or gemini" ;; esac

# Find the skills: next to this script in a clone, otherwise download the repo.
SRC=""; TMP=""
cleanup() { if [ -n "$TMP" ]; then rm -rf "$TMP"; fi; }
trap cleanup EXIT

SELF="${BASH_SOURCE[0]:-}"
if [ -n "$SELF" ] && [ -f "$SELF" ]; then
  HERE="$(cd "$(dirname "$SELF")" && pwd)"
  if [ -d "$HERE/skills" ] && [ -f "$HERE/install.sh" ]; then SRC="$HERE/skills"; fi
fi

if [ -z "$SRC" ]; then
  [ "$LINK" = 0 ] || die "--link needs a local clone (git clone https://github.com/$REPO)"
  TMP="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills.XXXXXX")"
  URL="https://codeload.github.com/$REPO/tar.gz/$REF"
  echo "Downloading $REPO ($REF)"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$URL" -o "$TMP/repo.tar.gz" || die "download failed: $URL"
  elif command -v wget >/dev/null 2>&1; then
    wget -q "$URL" -O "$TMP/repo.tar.gz" || die "download failed: $URL"
  else
    die "curl or wget is required"
  fi
  tar -xzf "$TMP/repo.tar.gz" -C "$TMP" || die "could not extract the download"
  for d in "$TMP"/*/; do
    if [ -d "${d}skills" ]; then SRC="${d%/}/skills"; break; fi
  done
  [ -n "$SRC" ] || die "no skills folder in the download"
fi

SKILLS=()
for d in "$SRC"/*/; do
  if [ -f "${d}SKILL.md" ]; then SKILLS+=("$(basename "$d")"); fi
done
[ "${#SKILLS[@]}" -gt 0 ] || die "no skills found in $SRC"

if [ "$LIST" = 1 ]; then printf '%s\n' "${SKILLS[@]}"; exit 0; fi

if [ "$SCOPE" = "user" ]; then
  BASE="$HOME"
else
  [ -d "$DIR" ] || die "--dir $DIR does not exist"
  BASE="$(cd "$DIR" && pwd)"
fi

case "$TOOL" in
  all)    DESTS=("$BASE/.claude/skills" "$BASE/.agents/skills") ;;
  claude) DESTS=("$BASE/.claude/skills") ;;
  cursor) DESTS=("$BASE/.cursor/skills") ;;
  codex)  DESTS=("$BASE/.agents/skills") ;;
  gemini) DESTS=("$BASE/.gemini/skills") ;;
esac

run() { if [ "$DRY" = 1 ]; then echo "  [dry-run] $*"; else "$@"; fi; }
verb() { if [ "$DRY" = 1 ]; then echo "would $1"; else echo "$2"; fi; }

installed=0; skipped=0; removed=0
for dest in "${DESTS[@]}"; do
  echo "-> $dest"
  if [ "$UNINSTALL" = 0 ]; then run mkdir -p "$dest"; fi
  for name in "${SKILLS[@]}"; do
    target="$dest/$name"
    if [ "$UNINSTALL" = 1 ]; then
      if [ -e "$target" ] || [ -L "$target" ]; then
        run rm -rf "$target"; removed=$((removed + 1))
        echo "  $(verb remove removed) $name"
      fi
      continue
    fi
    if [ -e "$target" ] || [ -L "$target" ]; then
      if [ "$FORCE" = 1 ]; then
        run rm -rf "$target"
      else
        echo "  skip $name (already exists; use --force to overwrite)"
        skipped=$((skipped + 1)); continue
      fi
    fi
    if [ "$LINK" = 1 ]; then run ln -s "$SRC/$name" "$target"; else run cp -R "$SRC/$name" "$target"; fi
    installed=$((installed + 1))
    echo "  $(verb install installed) $name"
  done
done

suffix=""; if [ "$DRY" = 1 ]; then suffix=" (dry run, nothing changed)"; fi
if [ "$UNINSTALL" = 1 ]; then
  echo "Done: removed $removed skill folder(s)$suffix."
  exit 0
fi
echo "Done: ${#SKILLS[@]} skills, ${#DESTS[@]} location(s): $installed installed, $skipped skipped (tool: $TOOL, scope: $SCOPE)$suffix."
if [ "$DRY" = 0 ] && [ "$installed" -gt 0 ]; then
  echo "Start a new agent session to load them. Try: /solo-product-page-audit"
fi
