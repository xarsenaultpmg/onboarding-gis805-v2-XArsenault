"""
Shared helpers for GIS805 NexaMart synthetic-data generators.

Design rules
────────────
* stdlib only -- no pip install, no surprises.
* Every generator receives --team-seed; this module turns it into a
  seeded `random.Random` instance so results are deterministic per team
  yet different across teams.
* CSV writer always uses UTF-8 + RFC-4180 quoting so DuckDB / BigQuery
  import "just works."
* All generators share the NexaMart master catalog so conformed
  dimensions stay consistent across sessions and departments.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

SCENARIO_FAMILY = "NEXAMART_RETAIL_2026"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # .../repo-template/
SHARED_IDENTITY_REL = "shared/_identity.json"
META_IDENTITY_PATH = REPO_ROOT / "meta" / "dataset_identity.json"

# ── Argument parsing ────────────────────────────────────────────

def base_argparser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument(
        "--team-seed", type=int, required=True,
        help="Team number (1-30). Controls all randomness.",
    )
    p.add_argument(
        "--output-dir", type=str, default=None,
        help="Override output directory.",
    )
    return p


def resolve_output_dir(args: argparse.Namespace, session_tag: str) -> Path:
    if args.output_dir:
        out = Path(args.output_dir)
    else:
        out = Path("data") / "synthetic" / f"team_{args.team_seed}" / session_tag
    out.mkdir(parents=True, exist_ok=True)
    return out


def team_root(team_seed: int) -> Path:
    """Root directory for one team's synthetic data."""
    return Path("data") / "synthetic" / f"team_{team_seed}"


def shared_identity_path(team_seed: int) -> Path:
    return team_root(team_seed) / SHARED_IDENTITY_REL


# ── Shared identity (persists per-team counts so all sessions agree) ─────

def fingerprint(team_seed: int) -> str:
    payload = f"{SCENARIO_FAMILY}|{team_seed}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def write_shared_identity(team_seed: int, n_products: int, n_customers: int) -> dict:
    """Called ONLY by gen_shared_seeds.py. Persists the exact counts to disk
    so that every session generator (S02..S09) uses the same product and
    customer universe, guaranteeing zero orphan FKs."""
    identity = {
        "team_seed": team_seed,
        "scenario_family": SCENARIO_FAMILY,
        "n_products": n_products,
        "n_customers": n_customers,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "fingerprint": fingerprint(team_seed),
    }
    shared_path = shared_identity_path(team_seed)
    shared_path.parent.mkdir(parents=True, exist_ok=True)
    shared_path.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    # Also write the repo-root meta file (referenced by validation/rules.yaml
    # and tools/instructor/batch_validate.py).
    META_IDENTITY_PATH.parent.mkdir(parents=True, exist_ok=True)
    META_IDENTITY_PATH.write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    return identity


def read_shared_identity(team_seed: int) -> dict:
    """Called by every session generator. Fails fast with a helpful message
    if shared seeds have not been produced yet."""
    p = shared_identity_path(team_seed)
    if not p.exists():
        raise SystemExit(
            f"ERROR: shared identity not found at {p}. "
            "Run 'python scripts/datagen/gen_shared_seeds.py --team-seed "
            f"{team_seed}' first, or use gen_all.py which orchestrates the order."
        )
    return json.loads(p.read_text(encoding="utf-8"))


# ── Seeded RNG ──────────────────────────────────────────────────

def make_rng(team_seed: int, salt: str = "") -> random.Random:
    combined = f"nexamart-{team_seed}-{salt}"
    rng = random.Random()
    rng.seed(combined)
    return rng


# ── Date helpers ────────────────────────────────────────────────

def date_range(start: date, end: date) -> list[date]:
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def build_dim_date(start: date, end: date) -> list[dict]:
    rows: list[dict] = []
    for d in date_range(start, end):
        rows.append({
            "date_key": d.isoformat(),
            "year": d.year,
            "quarter": (d.month - 1) // 3 + 1,
            "month": d.month,
            "month_name": d.strftime("%B"),
            "week_iso": d.isocalendar()[1],
            "day_of_week": d.isoweekday(),
            "day_name": d.strftime("%A"),
            "is_weekend": 1 if d.isoweekday() >= 6 else 0,
        })
    return rows


# ── Weighted / nullable choice helpers ──────────────────────────

def weighted_choice(rng: random.Random, items: Sequence, weights: Sequence[float]) -> Any:
    return rng.choices(items, weights=weights, k=1)[0]


def maybe_null(rng: random.Random, value: Any, null_rate: float = 0.05) -> Any:
    if rng.random() < null_rate:
        return None
    return value


def triangular_int(rng: random.Random, low: int, mode: int, high: int) -> int:
    return int(rng.triangular(low, high, mode))


# ── CSV writer ──────────────────────────────────────────────────

def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> int:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        w.writerows(rows)
    return len(rows)


def banner(session: str, team_seed: int, outdir: Path, counts: dict[str, int]):
    print(f"\n{'='*60}")
    print(f"  {session}  |  team-seed {team_seed}  |  {outdir}")
    print(f"{'='*60}")
    for name, n in counts.items():
        print(f"  {name:<40s} {n:>6,} rows")
    print()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NexaMart Master Catalog -- shared across all generators
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

STORES = [
    {"store_id": "STR-001", "store_name": "NexaMart Centre-Ville",    "city": "Montréal", "region": "Québec",   "province": "QC", "store_type": "flagship"},
    {"store_id": "STR-002", "store_name": "NexaMart Rive-Sud",        "city": "Longueuil", "region": "Québec",   "province": "QC", "store_type": "standard"},
    {"store_id": "STR-003", "store_name": "NexaMart Laval",           "city": "Laval",     "region": "Québec",   "province": "QC", "store_type": "standard"},
    {"store_id": "STR-004", "store_name": "NexaMart Gatineau",        "city": "Gatineau",  "region": "Outaouais","province": "QC", "store_type": "standard"},
    {"store_id": "STR-005", "store_name": "NexaMart Sherbrooke",      "city": "Sherbrooke","region": "Estrie",   "province": "QC", "store_type": "compact"},
    {"store_id": "STR-006", "store_name": "NexaMart Ottawa",          "city": "Ottawa",    "region": "Ontario",  "province": "ON", "store_type": "standard"},
    {"store_id": "STR-007", "store_name": "NexaMart Toronto-Downtown","city": "Toronto",   "region": "Ontario",  "province": "ON", "store_type": "flagship"},
    {"store_id": "STR-008", "store_name": "NexaMart Mississauga",     "city": "Mississauga","region":"Ontario",  "province": "ON", "store_type": "standard"},
    {"store_id": "STR-009", "store_name": "NexaMart Calgary",         "city": "Calgary",   "region": "Alberta",  "province": "AB", "store_type": "standard"},
    {"store_id": "STR-010", "store_name": "NexaMart Vancouver",       "city": "Vancouver", "region": "BC",       "province": "BC", "store_type": "flagship"},
]

CHANNELS = [
    {"channel_id": "CH-WEB",   "channel_name": "E-Commerce Web",   "channel_type": "online"},
    {"channel_id": "CH-APP",   "channel_name": "Mobile App",       "channel_type": "online"},
    {"channel_id": "CH-STORE", "channel_name": "In-Store",         "channel_type": "physical"},
    {"channel_id": "CH-PHONE", "channel_name": "Telephone Orders", "channel_type": "phone"},
    {"channel_id": "CH-MKTPL", "channel_name": "Marketplace 3P",   "channel_type": "online"},
]

CATEGORIES = [
    "Electronics", "Clothing", "Home & Garden", "Sports & Outdoors",
    "Grocery", "Beauty & Health", "Toys & Games", "Books & Media",
    "Automotive", "Pet Supplies",
]

PRODUCTS_MASTER: list[dict] = []
_pid = 1
for _cat in CATEGORIES:
    for _i in range(1, 11):
        PRODUCTS_MASTER.append({
            "product_id": f"PRD-{_pid:04d}",
            "product_name": f"{_cat} Item {_i}",
            "category": _cat,
            "subcategory": f"{_cat[:4]}-Sub{(_i-1)%3+1}",
            "brand": f"Brand-{chr(64 + (_pid % 26) + 1)}",
            "unit_cost": round(5 + (_pid * 1.37) % 95, 2),
            "unit_price": round(10 + (_pid * 1.73) % 190, 2),
        })
        _pid += 1

SEGMENTS = ["Platinum", "Gold", "Silver", "Bronze", "New", "Inactive"]

CAMPAIGNS = [
    {"campaign_id": "CMP-001", "campaign_name": "Summer Blowout",     "campaign_type": "seasonal",  "start_date": "2025-06-01", "end_date": "2025-08-31"},
    {"campaign_id": "CMP-002", "campaign_name": "Back to School",     "campaign_type": "seasonal",  "start_date": "2025-08-15", "end_date": "2025-09-30"},
    {"campaign_id": "CMP-003", "campaign_name": "Black Friday",       "campaign_type": "event",     "start_date": "2025-11-28", "end_date": "2025-12-01"},
    {"campaign_id": "CMP-004", "campaign_name": "Holiday Season",     "campaign_type": "seasonal",  "start_date": "2025-12-01", "end_date": "2025-12-31"},
    {"campaign_id": "CMP-005", "campaign_name": "New Year Clearance", "campaign_type": "clearance",  "start_date": "2026-01-01", "end_date": "2026-01-31"},
    {"campaign_id": "CMP-006", "campaign_name": "Loyalty Double Pts", "campaign_type": "loyalty",   "start_date": "2025-10-01", "end_date": "2025-10-31"},
    {"campaign_id": "CMP-007", "campaign_name": "Spring Refresh",     "campaign_type": "seasonal",  "start_date": "2026-03-01", "end_date": "2026-04-15"},
    {"campaign_id": "CMP-008", "campaign_name": "Flash Sale Week",    "campaign_type": "event",     "start_date": "2026-02-10", "end_date": "2026-02-16"},
]


def build_customers(rng: random.Random, n: int) -> list[dict]:
    """Generate n NexaMart customers with team-specific variation."""
    first_names = ["Alice","Bob","Clara","David","Emma","Félix","Gabrielle",
                   "Hugo","Isabelle","Jean","Karim","Léa","Marc","Nadia",
                   "Olivier","Patricia","Quentin","Rose","Samuel","Tanya",
                   "Ugo","Valérie","William","Xiao","Yasmine","Zachary"]
    last_names = ["Tremblay","Roy","Gagnon","Bouchard","Côté","Gauthier",
                  "Morin","Lavoie","Fortin","Gagné","Ouellet","Pelletier",
                  "Bélanger","Lévesque","Bergeron","Leblanc","Paquette",
                  "Girard","Simard","Boucher","Caron","Beaulieu","Cloutier",
                  "Dubois","Poirier","Martin"]
    cities = ["Montréal","Toronto","Vancouver","Ottawa","Calgary","Québec",
              "Longueuil","Laval","Sherbrooke","Gatineau"]
    customers = []
    for i in range(1, n + 1):
        join_date = date(2023, 1, 1) + timedelta(days=rng.randint(0, 730))
        customers.append({
            "customer_id": f"CUS-{i:05d}",
            "first_name": rng.choice(first_names),
            "last_name": rng.choice(last_names),
            "email_domain": rng.choice(["gmail.com","outlook.com","yahoo.ca","hotmail.com","usherbrooke.ca"]),
            "city": rng.choice(cities),
            "province": rng.choice(["QC","ON","BC","AB"]),
            "loyalty_segment": weighted_choice(rng, SEGMENTS, [0.05, 0.15, 0.30, 0.25, 0.15, 0.10]),
            "join_date": join_date.isoformat(),
        })
    return customers


def build_employees(rng: random.Random, n: int) -> list[dict]:
    """Generate n NexaMart employees."""
    roles = ["Sales Associate","Cashier","Stock Clerk","Department Manager",
             "Store Manager","Analyst","Warehouse Operator","Customer Service"]
    employees = []
    for i in range(1, n + 1):
        employees.append({
            "employee_id": f"EMP-{i:04d}",
            "employee_name": f"Employee_{i}",
            "role": rng.choice(roles),
            "store_id": rng.choice(STORES)["store_id"],
            "hire_date": (date(2020, 1, 1) + timedelta(days=rng.randint(0, 1800))).isoformat(),
        })
    return employees


def select_products(rng: random.Random, n: int) -> list[dict]:
    """Pick n products from the master list (team-specific subset).

    NOTE: results depend on the current rng state. Prefer shared_products()
    below when you need identical results across call sites -- pure function
    of (team_seed, n).
    """
    return rng.sample(PRODUCTS_MASTER, min(n, len(PRODUCTS_MASTER)))


# ━━━ State-independent helpers for conformed dimensions ━━━━━━━━━━━━━━━━━━
# These are pure functions of (team_seed, n). They use their OWN internal
# rng so call order / prior advances cannot shift the result. Every
# generator (shared_seeds and per-session) must use these to guarantee
# the same product/customer universe.

def shared_products(team_seed: int, n: int) -> list[dict]:
    rng = make_rng(team_seed, "shared-products")
    return rng.sample(PRODUCTS_MASTER, min(n, len(PRODUCTS_MASTER)))


def shared_customers(team_seed: int, n: int) -> list[dict]:
    rng = make_rng(team_seed, "shared-customers")
    return build_customers(rng, n)
