#!/usr/bin/env python3
"""Validate every skills/<name>/SKILL.md against the Agent Skills format.

Checks, per skill:
  - YAML frontmatter opens and closes with '---'
  - only spec keys: name, description, license, compatibility, metadata, allowed-tools
  - name matches the folder, is kebab-case and at most 64 characters
  - description is present and at most 1024 characters
  - metadata values are strings
  - the body has every section this repo requires
  - code fences are balanced

Usage: python3 scripts/validate.py [skills_dir]
Exit code 0 when every skill passes, 1 otherwise. Requires PyYAML.
"""
import os
import re
import sys

import yaml

ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REQUIRED_SECTIONS = [
    "## When to use (trigger)",
    "## Inputs",
    "## Steps",
    "## Output format",
    "## Worked example",
    "## Honesty rules",
]


def check(path, folder):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        return "", 0, ["no leading '---' frontmatter"]
    try:
        frontmatter, body = text[4:].split("\n---\n", 1)
    except ValueError:
        return "", 0, ["frontmatter is not closed with '---'"]
    try:
        meta = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError as exc:
        return "", 0, [f"invalid YAML: {exc}"]
    if not isinstance(meta, dict):
        return "", 0, ["frontmatter must be a YAML mapping"]

    problems = []
    unknown = set(meta) - ALLOWED_KEYS
    if unknown:
        problems.append(f"unknown keys {sorted(unknown)}")
    name = meta.get("name", "")
    if name != folder:
        problems.append("name does not match folder")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append("name must be kebab-case, max 64 chars")
    description = meta.get("description", "")
    if not isinstance(description, str) or not description or len(description) > 1024:
        problems.append(f"description must be 1-1024 chars (got {len(description or '')})")
    metadata = meta.get("metadata", {}) or {}
    if not isinstance(metadata, dict) or not all(isinstance(v, str) for v in metadata.values()):
        problems.append("metadata values must be strings")
    for section in REQUIRED_SECTIONS:
        if section not in body:
            problems.append(f"missing section '{section}'")
    if body.count("```") % 2:
        problems.append("unbalanced code fences")
    return name, len(description or ""), problems


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "skills"
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory")
        return 1
    checked = failing = 0
    for folder in sorted(os.listdir(root)):
        path = os.path.join(root, folder, "SKILL.md")
        if not os.path.isfile(path):
            continue
        checked += 1
        name, desc_len, problems = check(path, folder)
        status = "FAIL" if problems else "ok  "
        detail = "; ".join(problems)
        print(f"{status} {folder:32s} description={desc_len:4d} chars  {detail}".rstrip())
        failing += bool(problems)
    print(f"{checked} skills checked, {failing} failing")
    return 1 if failing or checked == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
