"""CLI for agent-skill-check."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .checker import CheckResult, discover_fixtures, load_fixture, run_checks

DISCLAIMER = (
    "Disclaimer: agent-skill-check runs deterministic fixture checks only. "
    "It cannot certify overall safety, correctness, or policy compliance."
)


def _print_result(result: CheckResult, verbose: bool = True) -> None:
    tag = "OK" if result.matched_expect else "MISMATCH"
    outcome = f"actual={result.actual} expect={result.expect}"
    print(f"[{tag}] {result.name} ({outcome})")
    if result.path:
        print(f"       path: {result.path}")
    if verbose:
        for finding in result.findings:
            mark = {"pass": "+", "fail": "-", "skip": "o"}[finding.status]
            print(f"       {mark} [{finding.check}] {finding.message}")


def _markdown_report(results: list[CheckResult]) -> str:
    lines = [
        "# agent-skill-check report",
        "",
        DISCLAIMER,
        "",
        "| Fixture | Expect | Actual | Matched |",
        "|---|---|---|---|",
    ]
    for r in results:
        matched = "yes" if r.matched_expect else "NO"
        lines.append(f"| `{r.name}` | {r.expect} | {r.actual} | {matched} |")
    lines.append("")
    for r in results:
        lines.append(f"## {r.name}")
        lines.append("")
        lines.append(f"- Path: `{r.path}`")
        lines.append(f"- Expect: `{r.expect}` · Actual: `{r.actual}`")
        lines.append("")
        for f in r.findings:
            lines.append(f"- **{f.status}** `{f.check}`: {f.message}")
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agent-skill-check",
        description=(
            "Check agent tool-log exports against a predeclared acceptance test. "
            "Distinct from say-do-diff (claim vs log): this is log/behavior vs acceptance criteria."
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="fixtures",
        help="Fixture directory, fixtures root, or combined JSON/YAML file (default: fixtures)",
    )
    parser.add_argument(
        "--acceptance",
        help="Acceptance YAML/JSON when path is a single run file",
    )
    parser.add_argument(
        "--markdown",
        metavar="FILE",
        help="Write a Markdown report to FILE",
    )
    parser.add_argument(
        "--json",
        metavar="FILE",
        help="Write machine-readable JSON results to FILE",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print the summary line per fixture",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"agent-skill-check {__version__}",
    )
    args = parser.parse_args(argv)

    print(DISCLAIMER)
    print()

    target = Path(args.path)
    # Resolve relative to CWD; if default fixtures/ missing, try beside this package.
    if args.path == "fixtures" and not target.exists():
        sibling = Path(__file__).resolve().parent.parent / "fixtures"
        if sibling.is_dir():
            target = sibling

    results: list[CheckResult] = []
    try:
        if args.acceptance:
            # Single run file + explicit acceptance
            from .checker import _load, _normalize_run

            acceptance = _load(Path(args.acceptance))
            run_data = _load(target)
            if isinstance(run_data, list):
                run_data = {"tool_log": run_data}
            log = _normalize_run(run_data)
            results.append(run_checks(acceptance, log, path=str(target)))
        elif target.is_file():
            acceptance, log, label = load_fixture(target)
            results.append(run_checks(acceptance, log, path=label))
        elif target.is_dir():
            # Directory may itself be one fixture, or a root of fixtures.
            if any(
                (target / name).is_file()
                for name in ("acceptance.yaml", "acceptance.yml", "acceptance.json")
            ):
                acceptance, log, label = load_fixture(target)
                results.append(run_checks(acceptance, log, path=label))
            else:
                fixtures = discover_fixtures(target)
                if not fixtures:
                    print(f"error: no fixtures found under {target}", file=sys.stderr)
                    return 2
                for fixture in fixtures:
                    acceptance, log, label = load_fixture(fixture)
                    results.append(run_checks(acceptance, log, path=label))
        else:
            print(f"error: path not found: {target}", file=sys.stderr)
            return 2
    except Exception as exc:  # noqa: BLE001 — CLI surface
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for result in results:
        _print_result(result, verbose=not args.quiet)
        print()

    matched = sum(1 for r in results if r.matched_expect)
    mismatched = [r for r in results if not r.matched_expect]
    print(f"Summary: {matched}/{len(results)} fixtures matched their expected outcome.")
    if mismatched:
        print("Mismatched:")
        for r in mismatched:
            print(f"  - {r.name}: expect={r.expect} actual={r.actual}")

    if args.markdown:
        Path(args.markdown).write_text(_markdown_report(results), encoding="utf-8")
        print(f"Wrote Markdown report: {args.markdown}")

    if args.json:
        payload = []
        for r in results:
            payload.append(
                {
                    "name": r.name,
                    "path": r.path,
                    "expect": r.expect,
                    "actual": r.actual,
                    "matched_expect": r.matched_expect,
                    "findings": [
                        {
                            "check": f.check,
                            "status": f.status,
                            "message": f.message,
                            "detail": f.detail,
                        }
                        for f in r.findings
                    ],
                }
            )
        Path(args.json).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote JSON report: {args.json}")

    return 0 if not mismatched else 1


if __name__ == "__main__":
    raise SystemExit(main())
