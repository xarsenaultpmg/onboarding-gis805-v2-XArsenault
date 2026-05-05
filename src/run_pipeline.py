#!/usr/bin/env python3
"""
run_pipeline.py — Load generated CSVs into DuckDB and execute SQL pipeline.

Steps:
  1. Connect to db/nexamart.duckdb (created if missing)
  2. Auto-import all CSVs from data/synthetic/ as raw_* tables
  3. Execute SQL files in order: sql/staging/ → sql/dims/ → sql/facts/
  4. Report tables created + row counts

Usage:
    python src/run_pipeline.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Python version guard -- the list[tuple[...]] and PEP 604 unions used below
# (and in src/run_checks.py) require 3.10+. The studio target is 3.12. We
# refuse to run on older interpreters rather than produce a cryptic
# "unsupported operand" TypeError halfway through the pipeline.
MIN_PY = (3, 10)
if sys.version_info < MIN_PY:
    print(
        f"ERROR: Python {'.'.join(map(str, MIN_PY))}+ is required, "
        f"you are on {sys.version.split()[0]}.\n"
        "       Install Python 3.12 (see docs/S00-SETUP.md) or open a Codespace."
    )
    sys.exit(1)

try:
    import duckdb
except ImportError:
    print("ERROR: duckdb not installed. Run: pip install duckdb")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "db" / "nexamart.duckdb"
DATA_DIR = ROOT / "data" / "synthetic"
SQL_DIRS = [
    ROOT / "sql" / "staging",
    ROOT / "sql" / "dims",
    ROOT / "sql" / "facts",
    ROOT / "sql" / "bridges",
]


def find_csvs(data_dir: Path) -> list[tuple[str, Path]]:
    """Find all CSVs under data/synthetic/ and derive table names.

    Convention: data/synthetic/team_7/shared/dim_date.csv → raw_dim_date
                data/synthetic/team_7/s02/fact_sales.csv  → raw_fact_sales
    If two sessions produce the same filename, the later session wins.
    """
    tables: dict[str, Path] = {}
    if not data_dir.exists():
        return []
    for csv_path in sorted(data_dir.rglob("*.csv")):
        stem = csv_path.stem                       # e.g. "dim_date"
        table_name = f"raw_{stem}"                 # e.g. "raw_dim_date"
        tables[table_name] = csv_path              # later session overwrites
    return list(tables.items())


def load_csvs(con: duckdb.DuckDBPyConnection, csvs: list[tuple[str, Path]]) -> None:
    """Import each CSV as a raw table."""
    for table_name, csv_path in csvs:
        con.execute(f"DROP TABLE IF EXISTS {table_name}")
        con.execute(
            f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{csv_path.as_posix()}')"
        )
        count = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  {table_name:<40s} {count:>8,} rows  <- {csv_path.relative_to(ROOT)}")


def execute_sql_dir(con: duckdb.DuckDBPyConnection, sql_dir: Path) -> int:
    """Execute all .sql files in a directory (alphabetical order). Returns count."""
    if not sql_dir.exists():
        return 0
    sql_files = sorted(sql_dir.glob("*.sql"))
    for sql_file in sql_files:
        sql = sql_file.read_text(encoding="utf-8")
        if sql.strip():
            try:
                con.execute(sql)
                print(f"  OK {sql_file.relative_to(ROOT)}")
            except duckdb.Error as e:
                print(f"  FAIL {sql_file.relative_to(ROOT)} -- {e}")
    return len(sql_files)


def report(con: duckdb.DuckDBPyConnection) -> None:
    """Print summary of all tables and row counts."""
    tables = con.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'main' ORDER BY table_name"
    ).fetchall()
    print(f"\n{'='*60}")
    print(f"  {len(tables)} tables in db/nexamart.duckdb")
    print(f"{'='*60}")
    for (tbl,) in tables:
        count = con.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
        print(f"  {tbl:<40s} {count:>8,} rows")
    print()


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))

    # Step 1 — Load CSVs
    csvs = find_csvs(DATA_DIR)
    if not csvs:
        print(f"ERROR: No CSVs found in {DATA_DIR.relative_to(ROOT)}/")
        print("       Run 'make generate' (or .\\run.ps1 generate) first.")
        con.close()
        sys.exit(1)

    print(f"\n-- Loading {len(csvs)} CSVs into DuckDB --\n")
    load_csvs(con, csvs)

    # Step 2 — Execute SQL pipeline
    for sql_dir in SQL_DIRS:
        label = sql_dir.name
        n = execute_sql_dir(con, sql_dir)
        if n:
            print(f"  ({n} file(s) from sql/{label}/)")

    # Step 3 — Report
    report(con)
    con.close()
    print("Done. Database: db/nexamart.duckdb")


if __name__ == "__main__":
    main()
