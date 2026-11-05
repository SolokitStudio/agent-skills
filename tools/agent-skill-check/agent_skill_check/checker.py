"""Deterministic acceptance checks over an agent tool-log export.

Checks
------
1. required_evidence — each declared evidence item must match ≥1 log entry
2. prohibited_actions — any matching log entry fails the run
3. approval_before_send — every send-like action must be preceded by an approval

This tool cannot certify overall safety or correctness. It only reports whether
the exported log satisfies the declared acceptance criteria.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore


@dataclass
class Finding:
    check: str
    status: str  # pass | fail | skip
    message: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    name: str
    path: str
    expect: str  # pass | fail
    findings: list[Finding]
    actual: str = "pass"
    matched_expect: bool = True

    def finalize(self) -> None:
        failed = any(f.status == "fail" for f in self.findings)
        self.actual = "fail" if failed else "pass"
        self.matched_expect = self.actual == self.expect


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML files: pip install pyyaml")
        return yaml.safe_load(text)
    import json

    return json.loads(text)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _entry_matches(entry: dict[str, Any], match: dict[str, Any]) -> bool:
    """Return True when every key in match equals the entry (case-sensitive strings)."""
    if not isinstance(entry, dict) or not isinstance(match, dict):
        return False
    for key, expected in match.items():
        actual = entry.get(key)
        if actual is None:
            return False
        if isinstance(expected, str) and isinstance(actual, str):
            if actual != expected:
                return False
        elif actual != expected:
            return False
    return True


def _normalize_run(data: dict[str, Any]) -> list[dict[str, Any]]:
    if "tool_log" in data and isinstance(data["tool_log"], list):
        return [e for e in data["tool_log"] if isinstance(e, dict)]
    if "events" in data and isinstance(data["events"], list):
        return [e for e in data["events"] if isinstance(e, dict)]
    if isinstance(data.get("log"), list):
        return [e for e in data["log"] if isinstance(e, dict)]
    raise ValueError("run file must contain a list under tool_log, events, or log")


def _normalize_acceptance(data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("acceptance must be a mapping")
    expect = str(data.get("expect", "pass")).lower()
    if expect not in {"pass", "fail"}:
        raise ValueError("acceptance.expect must be 'pass' or 'fail'")
    return {
        "name": data.get("name") or "unnamed",
        "description": data.get("description") or "",
        "expect": expect,
        "required_evidence": _as_list(data.get("required_evidence")),
        "prohibited_actions": _as_list(data.get("prohibited_actions")),
        "approval_before_send": data.get("approval_before_send") or {},
    }


def check_required_evidence(
    log: list[dict[str, Any]], required: list[Any]
) -> list[Finding]:
    findings: list[Finding] = []
    if not required:
        findings.append(
            Finding("required_evidence", "skip", "No required evidence declared.")
        )
        return findings
    for i, item in enumerate(required):
        if not isinstance(item, dict):
            findings.append(
                Finding(
                    "required_evidence",
                    "fail",
                    f"required_evidence[{i}] must be a mapping with a match block.",
                )
            )
            continue
        label = item.get("id") or item.get("name") or f"evidence[{i}]"
        match = item.get("match") or {
            k: v for k, v in item.items() if k not in {"id", "name", "description"}
        }
        if not match:
            findings.append(
                Finding(
                    "required_evidence",
                    "fail",
                    f"{label}: empty match criteria.",
                )
            )
            continue
        hit = next((e for e in log if _entry_matches(e, match)), None)
        if hit is None:
            findings.append(
                Finding(
                    "required_evidence",
                    "fail",
                    f"Missing required evidence '{label}' (match={match}).",
                    {"id": label, "match": match},
                )
            )
        else:
            findings.append(
                Finding(
                    "required_evidence",
                    "pass",
                    f"Found required evidence '{label}'.",
                    {"id": label, "match": match, "entry": hit},
                )
            )
    return findings


def check_prohibited_actions(
    log: list[dict[str, Any]], prohibited: list[Any]
) -> list[Finding]:
    findings: list[Finding] = []
    if not prohibited:
        findings.append(
            Finding("prohibited_actions", "skip", "No prohibited actions declared.")
        )
        return findings
    for i, item in enumerate(prohibited):
        if isinstance(item, str):
            match: dict[str, Any] = {"action": item}
            label = item
        elif isinstance(item, dict):
            label = item.get("id") or item.get("name") or f"prohibited[{i}]"
            match = item.get("match") or {
                k: v for k, v in item.items() if k not in {"id", "name", "description"}
            }
        else:
            findings.append(
                Finding(
                    "prohibited_actions",
                    "fail",
                    f"prohibited_actions[{i}] must be a string or mapping.",
                )
            )
            continue
        hits = [e for e in log if _entry_matches(e, match)]
        if hits:
            findings.append(
                Finding(
                    "prohibited_actions",
                    "fail",
                    f"Prohibited action '{label}' occurred {len(hits)} time(s) (match={match}).",
                    {"id": label, "match": match, "entries": hits},
                )
            )
        else:
            findings.append(
                Finding(
                    "prohibited_actions",
                    "pass",
                    f"No prohibited action '{label}' found.",
                    {"id": label, "match": match},
                )
            )
    return findings


def check_approval_before_send(
    log: list[dict[str, Any]], gate: dict[str, Any]
) -> list[Finding]:
    findings: list[Finding] = []
    if not gate:
        findings.append(
            Finding("approval_before_send", "skip", "Approval-before-send gate not configured.")
        )
        return findings
    if gate.get("enabled", True) is False:
        findings.append(
            Finding("approval_before_send", "skip", "Approval-before-send gate disabled.")
        )
        return findings

    send_match = gate.get("send_match") or {"action": "send"}
    approval_match = gate.get("approval_match") or {
        "tool": "human.approve",
        "status": "approved",
    }

    sends = [(idx, e) for idx, e in enumerate(log) if _entry_matches(e, send_match)]
    if not sends:
        findings.append(
            Finding(
                "approval_before_send",
                "pass",
                "No send actions in the log; approval gate not triggered.",
                {"send_match": send_match},
            )
        )
        return findings

    for idx, send_entry in sends:
        prior = log[:idx]
        approved = any(_entry_matches(e, approval_match) for e in prior)
        target = send_entry.get("target") or send_entry.get("id") or f"index {idx}"
        if approved:
            findings.append(
                Finding(
                    "approval_before_send",
                    "pass",
                    f"Send '{target}' was preceded by an approval.",
                    {"send": send_entry, "approval_match": approval_match},
                )
            )
        else:
            findings.append(
                Finding(
                    "approval_before_send",
                    "fail",
                    f"Send '{target}' occurred without a prior approval (match={approval_match}).",
                    {"send": send_entry, "approval_match": approval_match},
                )
            )
    return findings


def run_checks(acceptance: dict[str, Any], log: list[dict[str, Any]], path: str = "") -> CheckResult:
    acc = _normalize_acceptance(acceptance)
    findings: list[Finding] = []
    findings.extend(check_required_evidence(log, acc["required_evidence"]))
    findings.extend(check_prohibited_actions(log, acc["prohibited_actions"]))
    findings.extend(check_approval_before_send(log, acc["approval_before_send"]))
    result = CheckResult(
        name=str(acc["name"]),
        path=path,
        expect=acc["expect"],
        findings=findings,
    )
    result.finalize()
    return result


def load_fixture(fixture_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], str]:
    """Load a fixture directory or a single combined JSON/YAML file.

    Directory layout:
      acceptance.yaml|yml|json
      run.json|yaml|yml   (or tool_log.json)

    Combined file:
      { "acceptance": {...}, "tool_log"|"run": {...} }
    """
    if fixture_path.is_dir():
        acc_path = None
        for name in ("acceptance.yaml", "acceptance.yml", "acceptance.json"):
            candidate = fixture_path / name
            if candidate.is_file():
                acc_path = candidate
                break
        if acc_path is None:
            raise FileNotFoundError(f"No acceptance.yaml/json in {fixture_path}")
        run_path = None
        for name in ("run.json", "run.yaml", "run.yml", "tool_log.json"):
            candidate = fixture_path / name
            if candidate.is_file():
                run_path = candidate
                break
        if run_path is None:
            raise FileNotFoundError(f"No run.json / tool_log.json in {fixture_path}")
        acceptance = _load(acc_path)
        run_data = _load(run_path)
        if isinstance(run_data, list):
            run_data = {"tool_log": run_data}
        return acceptance, _normalize_run(run_data), str(fixture_path)

    data = _load(fixture_path)
    if not isinstance(data, dict):
        raise ValueError(f"{fixture_path} must be a mapping")
    if "acceptance" in data:
        acceptance = data["acceptance"]
        if "tool_log" in data or "events" in data or "log" in data:
            log = _normalize_run(data)
        elif isinstance(data.get("run"), dict):
            log = _normalize_run(data["run"])
        else:
            raise ValueError(f"{fixture_path}: combined file needs tool_log/run")
        return acceptance, log, str(fixture_path)
    raise ValueError(
        f"{fixture_path}: expected a fixture directory or a combined file with an 'acceptance' key"
    )


def discover_fixtures(root: Path) -> list[Path]:
    if not root.is_dir():
        raise NotADirectoryError(root)
    found: list[Path] = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and not child.name.startswith("."):
            if any(
                (child / name).is_file()
                for name in ("acceptance.yaml", "acceptance.yml", "acceptance.json")
            ):
                found.append(child)
    return found
