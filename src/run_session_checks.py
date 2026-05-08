#!/usr/bin/env python3
"""
run_session_checks.py — Assignment-aware CI runner.

Reads validation/session_manifest.yaml, detects which session(s) a push
or PR touches (via git diff), and runs only the checks that matter for
those sessions.

Modes:
  --mode push    Used by classroom.yml on every push to main.
                 Blocks (exit 1) ONLY on hard SQL syntax errors in
                 committed *.sql files. Missing artefacts, deadline
                 misses, weak content -> warn (exit 0).
  --mode submit  Used by submit-gate.yml on PRs to submit/aX.
                 Blocks ALSO on missing/empty required_artefacts for
                 every session in the submission window.

Diff source:
  --since BASE   Compute changed files between BASE and HEAD.
                 If unset: try $GITHUB_EVENT_BEFORE then HEAD~1; fall
                 back to "all manifest sessions" on first push.

Outputs (always):
  validation/results/session_report.json
  validation/results/session_report.md
  Stdout: human-readable summary.
  $GITHUB_STEP_SUMMARY: appended report (if env var set).
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path

MIN_PY = (3, 10)
if sys.version_info < MIN_PY:
    print(f"ERROR: Python {'.'.join(map(str, MIN_PY))}+ required.")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

try:
    import duckdb
except ImportError:
    duckdb = None  # warehouse_checks will be skipped with a warning.

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "validation" / "session_manifest.yaml"
CHECKS_SQL = ROOT / "validation" / "checks.sql"
DB_PATH = ROOT / "db" / "nexamart.duckdb"
RESULTS_DIR = ROOT / "validation" / "results"

# Severity ordering for exit-code logic.
SEV_ERROR = "error"            # Always blocks.
SEV_SUBMIT = "submit_required" # Blocks only in submit mode.
SEV_WARN = "warn"              # Never blocks.
SEV_INFO = "info"              # Never blocks.
SEV_PASS = "pass"              # Never blocks.

SECTION_HEADER_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
RULE_MARKER_RE = re.compile(r"^--\s*@rule:\s*([A-Za-z0-9_]+)\s*$", re.MULTILINE)


# ============================================================
# Manifest + diff loading
# ============================================================

def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        die(f"Manifest not found: {MANIFEST_PATH}")
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def changed_files(since: str | None) -> list[str] | None:
    """Return list of repo-relative changed paths, or None to mean 'all sessions'."""
    if since is None:
        since = os.environ.get("GITHUB_EVENT_BEFORE") or "HEAD~1"
    # Filter out the all-zero SHA GitHub uses for the very first push.
    if since.strip("0") == "":
        return None
    try:
        out = subprocess.run(
            ["git", "diff", "--name-only", f"{since}..HEAD"],
            check=True, capture_output=True, text=True, cwd=str(ROOT),
        ).stdout
    except subprocess.CalledProcessError:
        # Probably a shallow clone or unknown ref -> fall back to listing
        # everything currently tracked in the manifest paths.
        return None
    files = [line.strip() for line in out.splitlines() if line.strip()]
    return files


def sessions_for_files(files: list[str] | None, manifest: dict) -> list[str]:
    """Map changed files to session keys (S01..S13). None means all sessions."""
    sessions = manifest["sessions"]
    if files is None:
        return [s for s in sessions.keys()
                if sessions[s].get("path_globs")]
    hits: set[str] = set()
    for path in files:
        for sid, sdef in sessions.items():
            for glob in sdef.get("path_globs") or []:
                if fnmatch.fnmatch(path, glob) or _glob_matches(path, glob):
                    hits.add(sid)
                    break
    return sorted(hits)


def _glob_matches(path: str, pattern: str) -> bool:
    """Support **/ in path globs (fnmatch alone doesn't)."""
    if "**" not in pattern:
        return fnmatch.fnmatch(path, pattern)
    # Convert glob with ** to regex.
    regex = re.escape(pattern).replace(r"\*\*", ".*").replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
    return re.fullmatch(regex, path) is not None


def sessions_for_window(window: str, manifest: dict) -> list[str]:
    """Return all session ids belonging to a submission window."""
    win = (manifest.get("submission_windows") or {}).get(window)
    if not win:
        die(f"Unknown submission_window '{window}' in manifest")
    return list(win.get("sessions") or [])


# ============================================================
# Check primitives
# ============================================================

def check_required_artefact(art: dict, mode: str) -> dict:
    """Verify a required_artefact: existence, min_bytes, sections."""
    rel = art["path"]
    p = ROOT / rel
    out = {"check": "required_artefact", "path": rel}
    if not p.exists():
        out["severity"] = SEV_SUBMIT if mode == "submit" else SEV_WARN
        out["message"] = f"fichier absent : {rel}"
        return out
    size = p.stat().st_size
    min_bytes = art.get("min_bytes", 0)
    if size < min_bytes:
        out["severity"] = SEV_SUBMIT if mode == "submit" else SEV_WARN
        out["message"] = f"trop court : {size} o < {min_bytes} o"
        return out
    sections = art.get("must_contain_sections")
    if sections:
        text = p.read_text(encoding="utf-8", errors="replace")
        present = {m.group(1) for m in SECTION_HEADER_RE.finditer(text)}
        missing = [s for s in sections
                   if not any(s.lower() in p.lower() for p in present)]
        if missing:
            # Missing sections are coaching warnings, not submit blockers.
            out["severity"] = SEV_WARN
            out["message"] = f"sections manquantes : {', '.join(missing)}"
            return out
    out["severity"] = SEV_PASS
    out["message"] = f"OK ({size} o)"
    return out


def check_sql_artefact(art: dict, mode: str) -> dict:
    """Verify a sql_artefact: file present, parses, and creates target object.

    SQL parse failure -> SEV_ERROR (blocks BOTH push and submit).
    Missing file -> SEV_SUBMIT in submit mode, SEV_WARN in push mode.
    Object-not-created -> SEV_WARN (might be an upstream view, etc.).
    """
    rel = art["path"]
    p = ROOT / rel
    out = {"check": "sql_artefact", "path": rel}
    if not p.exists():
        out["severity"] = SEV_SUBMIT if mode == "submit" else SEV_WARN
        out["message"] = f"fichier absent : {rel}"
        return out
    sql = p.read_text(encoding="utf-8")
    if not sql.strip():
        out["severity"] = SEV_SUBMIT if mode == "submit" else SEV_WARN
        out["message"] = "fichier vide"
        return out
    # Parse-check using a throwaway in-memory DuckDB. EXPLAIN doesn't run
    # the statement but does parse + bind it. We split by ';' to surface
    # the first failing statement.
    if duckdb is None:
        out["severity"] = SEV_WARN
        out["message"] = "duckdb non installé ; vérification ignorée"
        return out
    try:
        con = duckdb.connect(":memory:")
        for stmt in _split_sql(sql):
            try:
                con.execute(f"EXPLAIN {stmt}")
            except duckdb.ParserException as e:
                out["severity"] = SEV_ERROR
                out["message"] = f"erreur syntaxe SQL : {str(e).splitlines()[0]}"
                con.close()
                return out
            except duckdb.Error:
                # Binder errors (missing tables, unknown columns) are
                # expected pre-load -- not a syntax problem.
                continue
        con.close()
    except Exception as e:
        out["severity"] = SEV_WARN
        out["message"] = f"vérification syntaxique impossible : {e}"
        return out
    target = art.get("must_create_object")
    if target:
        if not re.search(rf"\bCREATE\s+(OR\s+REPLACE\s+)?(TABLE|VIEW)\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(target)}\b",
                         sql, re.IGNORECASE):
            out["severity"] = SEV_WARN
            out["message"] = f"ne crée pas l'objet '{target}'"
            return out
    out["severity"] = SEV_PASS
    out["message"] = f"syntaxe OK, crée {target or '(non spécifié)'}"
    return out


def _split_sql(sql: str) -> list[str]:
    """Naive split on ';' boundaries, ignoring comment-only chunks."""
    parts = []
    for raw in sql.split(";"):
        cleaned = raw.strip()
        lines = [l for l in cleaned.splitlines() if not l.strip().startswith("--")]
        if any(l.strip() for l in lines):
            parts.append(cleaned)
    return parts


def check_deadline(sdef: dict, today: date) -> dict | None:
    """Emit an advisory warn if a session's deadline has passed."""
    dl = sdef.get("deadline")
    if not dl:
        return None
    try:
        d = datetime.strptime(dl, "%Y-%m-%d").date()
    except ValueError:
        return None
    if today > d:
        return {
            "check": "deadline",
            "severity": SEV_WARN,
            "message": f"échéance dépassée ({dl}) ; rétroaction seulement, non bloquant",
        }
    return None


# ============================================================
# Warehouse checks (subset checks.sql by @rule)
# ============================================================

def parse_checks_sql() -> dict[str, list[str]]:
    """Return {rule_name: [stmt, ...]} based on -- @rule: markers."""
    if not CHECKS_SQL.exists():
        return {}
    text = CHECKS_SQL.read_text(encoding="utf-8")
    blocks: dict[str, list[str]] = {}
    # Split on rule markers; first chunk before any marker is ignored.
    pieces = re.split(r"^--\s*@rule:\s*([A-Za-z0-9_]+)\s*$", text, flags=re.MULTILINE)
    # pieces = [preamble, name1, body1, name2, body2, ...]
    for i in range(1, len(pieces), 2):
        name = pieces[i].strip()
        body = pieces[i + 1] if i + 1 < len(pieces) else ""
        blocks[name] = _split_sql(body)
    return blocks


def run_warehouse_checks(rule_names: list[str]) -> list[dict]:
    """Execute the SQL blocks for the given rule names against the DuckDB."""
    results: list[dict] = []
    if not rule_names:
        return results
    if duckdb is None:
        return [{"check": "warehouse", "rule": "all",
                 "severity": SEV_WARN, "message": "duckdb non installé"}]
    if not DB_PATH.exists():
        return [{"check": "warehouse", "rule": r,
                 "severity": SEV_WARN,
                 "message": "db/nexamart.duckdb non construit ; ignoré"}
                for r in rule_names]
    blocks = parse_checks_sql()
    con = duckdb.connect(str(DB_PATH), read_only=True)
    for name in rule_names:
        stmts = blocks.get(name)
        if not stmts:
            results.append({"check": "warehouse", "rule": name,
                            "severity": SEV_WARN,
                            "message": "règle introuvable dans checks.sql"})
            continue
        for stmt in stmts:
            try:
                rows = con.execute(stmt).fetchall()
                for row in rows:
                    if len(row) >= 3:
                        ctype, detail, result = row[0], row[1], row[2]
                        sev = SEV_PASS if str(result).startswith("PASS") else SEV_WARN
                        # Warehouse FAILs are coaching, not blocking, in
                        # both modes (per design: only SQL parse errors
                        # block).
                        results.append({"check": "warehouse",
                                        "rule": name, "type": ctype,
                                        "detail": detail, "result": result,
                                        "severity": sev})
            except duckdb.CatalogException as e:
                results.append({"check": "warehouse", "rule": name,
                                "severity": SEV_INFO,
                                "message": f"IGNORÉ (table absente) : "
                                           f"{str(e).splitlines()[0]}"})
            except duckdb.Error as e:
                results.append({"check": "warehouse", "rule": name,
                                "severity": SEV_WARN,
                                "message": f"erreur d'exécution : {e}"})
    con.close()
    return results


# ============================================================
# Reporting
# ============================================================

ICON = {
    SEV_ERROR: "❌",
    SEV_SUBMIT: "🛑",
    SEV_WARN: "⚠️ ",
    SEV_INFO: "ℹ️ ",
    SEV_PASS: "✅",
}


def render_md(report: dict) -> str:
    lines = [
        f"# Rapport de validation — mode `{report['mode']}`",
        "",
        f"- Sessions détectées : **{', '.join(report['sessions']) or '(aucune)'}**",
        f"- Mode : `{report['mode']}`",
        f"- Bloquant : **{'OUI' if report['blocking'] else 'non'}**  "
        f"({report['counts']})",
        "",
    ]
    if not report["sessions"]:
        lines += ["_Aucune modification pertinente détectée. Rien à vérifier._"]
        return "\n".join(lines)
    for sid in report["sessions"]:
        sec = report["per_session"][sid]
        lines += [f"## {sid} — {sec['title']}", ""]
        if sec["deadline_warning"]:
            lines += [f"- {ICON[SEV_WARN]} Échéance : "
                      f"{sec['deadline_warning']['message']}", ""]
        if not sec["results"]:
            lines += ["_Aucune vérification exécutée._", ""]
            continue
        lines += ["| Sévérité | Vérification | Message |", "|---|---|---|"]
        for r in sec["results"]:
            ic = ICON.get(r["severity"], "?")
            ck = r.get("check", "")
            if ck == "warehouse":
                msg = r.get("detail") or r.get("message") or ""
                if r.get("result"):
                    msg = f"{msg} → {r['result']}"
                ck_disp = f"warehouse / {r.get('rule', '')}"
            else:
                msg = r.get("message", "")
                ck_disp = f"{ck} {r.get('path', '')}".strip()
            lines.append(f"| {ic} | `{ck_disp}` | {msg} |")
        lines.append("")
    return "\n".join(lines)


def write_outputs(report: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "session_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md = render_md(report)
    (RESULTS_DIR / "session_report.md").write_text(md, encoding="utf-8")
    # GitHub Actions step summary.
    step_sum = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_sum:
        try:
            with open(step_sum, "a", encoding="utf-8") as f:
                f.write(md + "\n")
        except OSError:
            pass
    print(md)


# ============================================================
# Main
# ============================================================

def die(msg: str) -> None:
    print(f"FATAL: {msg}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["push", "submit"], default="push")
    ap.add_argument("--since", default=None,
                    help="Git ref to diff against (default: $GITHUB_EVENT_BEFORE or HEAD~1)")
    ap.add_argument("--window", default=None,
                    help="Submission window (a1|a2|final). In --mode submit "
                         "this overrides diff-based session detection and "
                         "checks ALL sessions in the window.")
    ap.add_argument("--all-sessions", action="store_true",
                    help="Force-run checks for every session (debug aid).")
    args = ap.parse_args()

    manifest = load_manifest()
    sessions_def = manifest["sessions"]

    if args.all_sessions:
        sessions = [s for s in sessions_def
                    if sessions_def[s].get("path_globs")]
    elif args.mode == "submit" and args.window:
        sessions = sessions_for_window(args.window, manifest)
    else:
        files = changed_files(args.since)
        sessions = sessions_for_files(files, manifest)

    today = date.today()
    per_session: dict[str, dict] = {}
    counts = {SEV_ERROR: 0, SEV_SUBMIT: 0, SEV_WARN: 0,
              SEV_INFO: 0, SEV_PASS: 0}

    for sid in sessions:
        sdef = sessions_def[sid]
        sec = {"title": sdef.get("title", ""), "results": [],
               "deadline_warning": None}
        sec["deadline_warning"] = check_deadline(sdef, today)

        for art in sdef.get("required_artefacts") or []:
            sec["results"].append(check_required_artefact(art, args.mode))
        for art in sdef.get("sql_artefacts") or []:
            sec["results"].append(check_sql_artefact(art, args.mode))
        sec["results"].extend(
            run_warehouse_checks(sdef.get("warehouse_checks") or [])
        )

        for r in sec["results"]:
            counts[r["severity"]] = counts.get(r["severity"], 0) + 1
        per_session[sid] = sec

    if args.mode == "push":
        blocking = counts[SEV_ERROR] > 0
    else:
        blocking = counts[SEV_ERROR] > 0 or counts[SEV_SUBMIT] > 0

    report = {
        "mode": args.mode,
        "sessions": sessions,
        "per_session": per_session,
        "counts": ", ".join(f"{k}:{v}" for k, v in counts.items() if v),
        "blocking": blocking,
    }
    write_outputs(report)
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
