"""Run validation/checks.sql against the NexaMart DuckDB warehouse."""

import os
import re
import sys
from pathlib import Path

# Python version guard -- matches src/run_pipeline.py. Keep in sync.
MIN_PY = (3, 10)
if sys.version_info < MIN_PY:
    print(
        f"ERROR: Python {'.'.join(map(str, MIN_PY))}+ is required, "
        f"you are on {sys.version.split()[0]}.\n"
        "       Install Python 3.12 (see docs/S00-SETUP.md) or open a Codespace."
    )
    sys.exit(1)

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "nexamart.duckdb"
CHECKS_SQL = ROOT / "validation" / "checks.sql"
RESULTS_DIR = ROOT / "validation" / "results"


def _split_statements(sql_text: str) -> list[str]:
    """Split SQL text into individual statements, ignoring comments."""
    stmts = []
    for raw in sql_text.split(";"):
        cleaned = raw.strip()
        # skip empty or comment-only blocks
        lines = [l for l in cleaned.splitlines() if not l.strip().startswith("--")]
        if any(l.strip() for l in lines):
            stmts.append(cleaned)
    return stmts


def main() -> int:
    if not DB_PATH.exists():
        print(f"ERROR: database not found: {DB_PATH}")
        print("       Run generate + load first.")
        return 1

    if not CHECKS_SQL.exists():
        print(f"ERROR: checks file not found: {CHECKS_SQL}")
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    results_file = RESULTS_DIR / "check_results.txt"

    sql_text = CHECKS_SQL.read_text(encoding="utf-8")
    stmts = _split_statements(sql_text)

    con = duckdb.connect(str(DB_PATH), read_only=True)
    results = []
    pass_count = 0
    fail_count = 0
    skip_count = 0

    for stmt in stmts:
        try:
            rows = con.execute(stmt).fetchall()
            for row in rows:
                check_type, detail, result = row[0], row[1], row[2]
                status = "PASS" if result == "PASS" else "FAIL"
                if status == "PASS":
                    pass_count += 1
                else:
                    fail_count += 1
                line = f"[{status:4s}]  {check_type:<15s}  {detail:<45s}  {result}"
                results.append(line)
        except duckdb.CatalogException as e:
            # Table/view doesn't exist yet (student hasn't written the SQL)
            skip_count += 1
            # Extract table name from error if possible
            msg = str(e).split("\n")[0]
            results.append(f"[SKIP]  {'MISSING_TABLE':<15s}  {msg}")
        except Exception as e:
            skip_count += 1
            msg = str(e).split("\n")[0]
            results.append(f"[SKIP]  {'ERROR':<15s}  {msg}")

    con.close()

    # Print summary
    header = f"NexaMart Validation: {pass_count} PASS, {fail_count} FAIL, {skip_count} SKIP"
    sep = "=" * len(header)
    output_lines = [sep, header, sep, ""] + results + [""]
    output_text = "\n".join(output_lines)

    print(output_text)
    results_file.write_text(output_text, encoding="utf-8")
    print(f"Results saved to {results_file.relative_to(ROOT)}")

    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
