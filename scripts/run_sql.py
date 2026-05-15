#!/usr/bin/env python3
"""Exécute un fichier .sql contre db/nexamart.duckdb (sans CLI duckdb)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "db" / "nexamart.duckdb"


def main() -> int:
    p = argparse.ArgumentParser(description="Run a SQL file against NexaMart DuckDB.")
    p.add_argument(
        "sql_file",
        type=Path,
        help="Chemin vers le fichier .sql (relatif à la racine du dépôt ou absolu).",
    )
    p.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Chemin vers la base DuckDB (défaut: {DEFAULT_DB})",
    )
    args = p.parse_args()

    sql_path = args.sql_file if args.sql_file.is_absolute() else Path.cwd() / args.sql_file
    if not sql_path.is_file():
        print(f"ERREUR: fichier introuvable: {sql_path}", file=sys.stderr)
        return 1
    if not args.db.is_file():
        print(
            f"ERREUR: base introuvable: {args.db}. Lancez d'abord generate puis load.",
            file=sys.stderr,
        )
        return 1

    sql = sql_path.read_text(encoding="utf-8")
    con = duckdb.connect(str(args.db), read_only=True)
    try:
        rel = con.execute(sql)
        if rel.description:
            print(rel.df().to_string(index=False))
        else:
            print("OK (pas de jeu de résultats).")
    finally:
        con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
