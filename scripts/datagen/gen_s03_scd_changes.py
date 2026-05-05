#!/usr/bin/env python3
"""
S03 -- SCD lab.

Generates customer and store change events so students experience
Type 1, Type 2, and Type 3 decisions.

Usage:
    python scripts/datagen/gen_s03_scd_changes.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, shared_customers, STORES, SEGMENTS,
    read_shared_identity,
)
from datetime import date, timedelta


def main():
    parser = base_argparser("S03 -- NexaMart SCD change events")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s03")
    outdir = resolve_output_dir(args, "s03")

    # Reuse the SAME customer universe written by gen_shared_seeds.
    identity = read_shared_identity(args.team_seed)
    customers = shared_customers(args.team_seed, identity["n_customers"])

    # Team-specific change intensity
    pct_customers_changing = rng.uniform(0.15, 0.45)
    n_changers = int(len(customers) * pct_customers_changing)
    changers = rng.sample(customers, n_changers)

    cities = ["Montréal","Toronto","Vancouver","Ottawa","Calgary","Québec",
              "Longueuil","Laval","Sherbrooke","Gatineau"]

    change_events = []
    for cust in changers:
        n_changes = weighted_choice(rng, [1, 2, 3, 4], [0.50, 0.30, 0.15, 0.05])
        join_d = date.fromisoformat(cust["join_date"])
        event_d = join_d + timedelta(days=rng.randint(30, 500))

        for _ in range(n_changes):
            change_type = weighted_choice(rng,
                ["city_move", "segment_change", "name_correction", "province_change"],
                [0.35, 0.35, 0.15, 0.15])

            old_val, new_val = "", ""
            if change_type == "city_move":
                old_val = cust["city"]
                new_val = rng.choice([c for c in cities if c != old_val])
            elif change_type == "segment_change":
                old_val = cust["loyalty_segment"]
                new_val = rng.choice([s for s in SEGMENTS if s != old_val])
            elif change_type == "name_correction":
                old_val = cust["last_name"]
                new_val = old_val.upper()  # typo correction
            elif change_type == "province_change":
                old_val = cust["province"]
                new_val = rng.choice([p for p in ["QC","ON","BC","AB"] if p != old_val])

            change_events.append({
                "customer_id": cust["customer_id"],
                "change_date": min(event_d, date(2025, 12, 31)).isoformat(),
                "change_type": change_type,
                "field_changed": change_type.replace("_change","").replace("_move","").replace("_correction",""),
                "old_value": old_val,
                "new_value": new_val,
            })
            event_d += timedelta(days=rng.randint(30, 300))

    # Store changes (region reassignment, type upgrade)
    store_changes = []
    n_store_changes = rng.randint(2, 5)
    for _ in range(n_store_changes):
        store = rng.choice(STORES)
        ch_type = rng.choice(["region_reassign", "type_upgrade"])
        if ch_type == "region_reassign":
            old_v = store["region"]
            new_v = rng.choice(["Québec","Ontario","Alberta","BC","Outaouais","Estrie"])
        else:
            old_v = store["store_type"]
            new_v = rng.choice(["flagship","standard","compact","express"])
        store_changes.append({
            "store_id": store["store_id"],
            "change_date": (date(2025, 1, 1) + timedelta(days=rng.randint(0, 364))).isoformat(),
            "change_type": ch_type,
            "old_value": old_v,
            "new_value": new_v,
        })

    counts = {}
    counts["customer_changes.csv"] = write_csv(
        outdir / "customer_changes.csv",
        ["customer_id","change_date","change_type","field_changed","old_value","new_value"],
        change_events,
    )
    counts["store_changes.csv"] = write_csv(
        outdir / "store_changes.csv",
        ["store_id","change_date","change_type","old_value","new_value"],
        store_changes,
    )

    banner("S03 -- SCD Changes", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
