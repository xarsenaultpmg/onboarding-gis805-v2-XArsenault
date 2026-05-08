#!/usr/bin/env python3
"""
grade_brief.py — LLM-backed rubric grader for GIS805 executive briefs.

Safety properties (do not relax without instructor sign-off):
  * PII redaction: git author/email/SIN-like sequences stripped before
    any byte leaves the runner. Audit log at
    validation/results/grader_redactions.txt.
  * Prompt allowlist: the SHA-256 of every loaded prompt file MUST
    appear in tools/grader/prompt_allowlist.txt. Mismatch -> refuse.
  * Reference-copy refusal: if the student brief is byte-identical to
    the reference brief, output insufficient + flag (no API call).
  * Always exit 0 on grading failures: this script must never block
    a PR. Hard gating is the structural-submit-gate's job.
  * Result cache: writes to a private cache repo when GRADER_CACHE_DIR
    is set. Cache key is sha256(repo + session + brief).

Providers (preferred order):
  1. Anthropic (env: ANTHROPIC_API_KEY, model: claude-3-5-sonnet-latest)
  2. OpenAI    (env: OPENAI_API_KEY,    model: gpt-4o-mini)

Outputs:
  validation/results/rubric_report.json
  validation/results/rubric_report.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed.", file=sys.stderr)
    sys.exit(0)  # never block

ROOT = Path(__file__).resolve().parents[2]   # repo root
TOOLS_DIR = ROOT / "tools" / "grader"
PROMPT_PATH = TOOLS_DIR / "prompts" / "grader_system.md"
ALLOWLIST_PATH = TOOLS_DIR / "prompt_allowlist.txt"
MANIFEST_PATH = ROOT / "validation" / "session_manifest.yaml"
RESULTS_DIR = ROOT / "validation" / "results"
RUBRIC_PATH_CANDIDATES = [
    TOOLS_DIR / "rubric_descriptors.yaml",
    ROOT / "config" / "rubric_descriptors.yaml",
]

REDACT_PATTERNS = [
    # SIN-style (Canadian Social Insurance Number) 9 digits with optional separators.
    (re.compile(r"\b\d{3}[ -]?\d{3}[ -]?\d{3}\b"), "[REDACTED-SIN]"),
    # Emails.
    (re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"), "[REDACTED-EMAIL]"),
    # Phone numbers (loose).
    (re.compile(r"\+?\d{1,3}[\s\-.]?\(?\d{2,4}\)?[\s\-.]?\d{2,4}[\s\-.]?\d{2,4}"), "[REDACTED-PHONE]"),
]


# ============================================================
# Helpers
# ============================================================

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_file(p: Path) -> str:
    """Hash the LF-normalized text of a prompt file.

    We strip CR characters and trailing whitespace per line so the
    hash is identical on Windows (CRLF) and Linux runners (LF).
    """
    text = p.read_text(encoding="utf-8")
    norm = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))
    return sha256_bytes(norm.encode("utf-8"))


def load_allowlist() -> set[str]:
    if not ALLOWLIST_PATH.exists():
        return set()
    out: set[str] = set()
    for line in ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        out.add(s.split()[0])
    return out


def get_git_identity_tokens() -> list[str]:
    """Names/emails to scrub from any text we send out."""
    tokens: list[str] = []
    for cmd in [
        ["git", "log", "-1", "--format=%an"],
        ["git", "log", "-1", "--format=%ae"],
        ["git", "config", "user.name"],
        ["git", "config", "user.email"],
    ]:
        try:
            out = subprocess.run(cmd, check=True, capture_output=True,
                                 text=True, cwd=str(ROOT)).stdout.strip()
            if out and len(out) >= 3:
                tokens.append(out)
        except subprocess.CalledProcessError:
            pass
    return tokens


def redact(text: str, identity_tokens: list[str]) -> tuple[str, list[str]]:
    """Return (redacted_text, list_of_redaction_descriptions)."""
    audit: list[str] = []
    for tok in identity_tokens:
        if tok and tok in text:
            text = text.replace(tok, "[REDACTED-IDENTITY]")
            audit.append(f"identity:{tok[:3]}***")
    for pattern, replacement in REDACT_PATTERNS:
        n = 0
        def _sub(m):
            nonlocal n
            n += 1
            return replacement
        text = pattern.sub(_sub, text)
        if n:
            audit.append(f"{replacement}:{n}")
    return text, audit


def load_rubric() -> dict:
    for p in RUBRIC_PATH_CANDIDATES:
        if p.exists():
            with p.open(encoding="utf-8") as f:
                return yaml.safe_load(f)
    raise FileNotFoundError("rubric_descriptors.yaml not found")


def load_manifest() -> dict:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


# ============================================================
# Cache
# ============================================================

def cache_key(repo: str, session: str, brief: str) -> str:
    h = hashlib.sha256()
    h.update(repo.encode()); h.update(b"\0")
    h.update(session.encode()); h.update(b"\0")
    h.update(brief.encode("utf-8"))
    return h.hexdigest()


def cache_lookup(key: str) -> dict | None:
    base = os.environ.get("GRADER_CACHE_DIR")
    if not base:
        return None
    p = Path(base) / f"{key}.json"
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None
    return None


def cache_store(key: str, payload: dict) -> None:
    base = os.environ.get("GRADER_CACHE_DIR")
    if not base:
        return
    Path(base).mkdir(parents=True, exist_ok=True)
    (Path(base) / f"{key}.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# ============================================================
# Provider call
# ============================================================

def call_anthropic(system: str, user: str) -> str | None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic  # type: ignore
    except ImportError:
        return None
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest"),
        max_tokens=1500,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(block.text for block in msg.content
                   if getattr(block, "type", "") == "text")


def call_openai(system: str, user: str) -> str | None:
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI  # type: ignore
    except ImportError:
        return None
    client = OpenAI()
    rsp = client.chat.completions.create(
        model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": user}],
        temperature=0,
    )
    return rsp.choices[0].message.content


def call_llm(system: str, user: str) -> tuple[str | None, str]:
    out = call_anthropic(system, user)
    if out is not None:
        return out, "anthropic"
    out = call_openai(system, user)
    if out is not None:
        return out, "openai"
    return None, "none"


# ============================================================
# Brief assembly
# ============================================================

def session_for_path(path: str, manifest: dict) -> str | None:
    for sid, sdef in manifest["sessions"].items():
        for art in (sdef.get("required_artefacts") or []):
            if art.get("path") == path:
                return sid
    return None


def build_user_message(rubric: dict, emphasis: list[str], reference: str,
                       student: str, session_ctx: str) -> str:
    return (
        "RUBRIC:\n" + json.dumps(rubric, ensure_ascii=False) + "\n\n"
        "EMPHASIS:\n" + json.dumps(emphasis, ensure_ascii=False) + "\n\n"
        "REFERENCE_BRIEF:\n" + reference + "\n\n"
        "STUDENT_BRIEF:\n" + student + "\n\n"
        "SESSION_CONTEXT:\n" + session_ctx + "\n"
    )


def fallback_report(session: str, reason: str) -> dict:
    return {
        "session": session,
        "graded": False,
        "reason": reason,
        "headline_feedback": "Notation indicative non disponible. "
                             "Consultez la rétroaction de l'instructeur.",
    }


# ============================================================
# Main
# ============================================================

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief", required=False,
                    help="Path to executive brief (relative to repo root)")
    ap.add_argument("--session", default=None,
                    help="Session id (S01..S13). Inferred from --brief if omitted.")
    ap.add_argument("--print-prompt-hash", action="store_true",
                    help="Print SHA-256 of the system prompt and exit.")
    args = ap.parse_args()

    if args.print_prompt_hash:
        print(sha256_file(PROMPT_PATH))
        return 0

    if not args.brief:
        print("--brief required (or --print-prompt-hash)", file=sys.stderr)
        return 0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    manifest = load_manifest()
    session = args.session or session_for_path(args.brief, manifest)
    if not session:
        report = fallback_report("?", f"could not map {args.brief} to a session")
        write_report(report)
        return 0

    sdef = manifest["sessions"][session]
    rubric_cfg = (sdef.get("rubric") or {})
    ref_path = ROOT / rubric_cfg.get("reference_brief_path", "")
    if not ref_path.exists():
        report = fallback_report(session, f"reference brief not found: {ref_path}")
        write_report(report)
        return 0

    brief_path = ROOT / args.brief
    if not brief_path.exists():
        report = fallback_report(session, f"brief not found: {args.brief}")
        write_report(report)
        return 0

    student_raw = brief_path.read_text(encoding="utf-8", errors="replace")
    reference_raw = ref_path.read_text(encoding="utf-8", errors="replace")

    # Reference-copy refusal (byte-identical).
    if student_raw.strip() == reference_raw.strip():
        report = {
            "session": session, "graded": True, "provider": "refusal",
            "scores": {}, "weighted_score_pct": 0.0,
            "headline_feedback": "Le brief soumis est identique au brief de "
                                 "référence. Une réflexion personnelle est requise.",
            "concerns": ["reference_copy_detected"],
        }
        write_report(report)
        return 0

    # PII redaction.
    identity_tokens = get_git_identity_tokens()
    student, audit_s = redact(student_raw, identity_tokens)
    log_audit(args.brief, audit_s)

    # Prompt allowlist.
    if not PROMPT_PATH.exists():
        report = fallback_report(session, f"prompt file missing: {PROMPT_PATH}")
        write_report(report)
        return 0
    prompt_hash = sha256_file(PROMPT_PATH)
    allow = load_allowlist()
    if prompt_hash not in allow:
        report = fallback_report(
            session,
            f"prompt SHA-256 {prompt_hash[:12]}... not on allowlist; refusing call")
        write_report(report)
        return 0

    rubric = load_rubric()
    emphasis = rubric_cfg.get("emphasis_dimensions", [])
    system = PROMPT_PATH.read_text(encoding="utf-8")
    user = build_user_message(
        rubric, emphasis, reference_raw, student,
        f"{session} — {sdef.get('title', '')}")

    # Cache lookup.
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "local")
    key = cache_key(repo_slug, session, student)
    cached = cache_lookup(key)
    if cached:
        cached["from_cache"] = True
        write_report(cached)
        return 0

    raw, provider = call_llm(system, user)
    if raw is None:
        report = fallback_report(session, "no LLM provider available")
        write_report(report)
        return 0

    parsed = parse_llm_json(raw)
    if parsed is None:
        report = fallback_report(session, "LLM response was not valid JSON")
        report["raw_response_excerpt"] = raw[:500]
        write_report(report)
        return 0

    parsed.setdefault("session", session)
    parsed["graded"] = True
    parsed["provider"] = provider
    parsed["prompt_sha256"] = prompt_hash
    cache_store(key, parsed)
    write_report(parsed)
    return 0


def parse_llm_json(text: str) -> dict | None:
    text = text.strip()
    # Strip code fences if model added them.
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def write_report(report: dict) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR / "rubric_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (RESULTS_DIR / "rubric_report.md").write_text(render_md(report), encoding="utf-8")
    print(render_md(report))


def render_md(report: dict) -> str:
    lines = [f"# Rubric report — {report.get('session', '?')}",
             ""]
    if not report.get("graded"):
        lines += [f"_Indicative grading unavailable: {report.get('reason', '')}._"]
        return "\n".join(lines)
    if report.get("from_cache"):
        lines += ["_(cached result)_", ""]
    lines += [f"**Score pondéré :** {report.get('weighted_score_pct', '?')}%",
              "", f"_{report.get('headline_feedback', '')}_", ""]
    scores = report.get("scores") or {}
    if scores:
        lines += ["| Dimension | Niveau | Note | Évidence | Amélioration |",
                  "|---|---|---|---|---|"]
        for dim, s in scores.items():
            lines.append(
                f"| {dim} | {s.get('level','')} | {s.get('score','')} | "
                f"{s.get('evidence','')} | {s.get('improvement','')} |")
        lines.append("")
    if report.get("concerns"):
        lines += ["**Flags :** " + ", ".join(report["concerns"]), ""]
    lines += [f"_Provider : {report.get('provider','')} · "
              f"prompt SHA-256 : `{report.get('prompt_sha256','')[:12]}...`_"]
    return "\n".join(lines)


def log_audit(brief_path: str, items: list[str]) -> None:
    if not items:
        return
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    p = RESULTS_DIR / "grader_redactions.txt"
    with p.open("a", encoding="utf-8") as f:
        from datetime import datetime
        f.write(f"{datetime.utcnow().isoformat()}Z\t{brief_path}\t"
                f"{','.join(items)}\n")


if __name__ == "__main__":
    sys.exit(main())
