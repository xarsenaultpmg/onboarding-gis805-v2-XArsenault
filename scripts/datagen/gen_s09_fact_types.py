#!/usr/bin/env python3
"""
S09 -- Four fact table types lab.

Maps NexaMart processes to fact table types:
  Transaction:           fact_orders (one row per order event)
  Periodic snapshot:     fact_daily_inventory (one row per product×store×day)
  Accumulating snapshot: fact_order_pipeline (one row per order lifecycle)
  Factless:              fact_promo_exposure (customer × campaign × date presence)

Usage:
    python scripts/datagen/gen_s09_fact_types.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, triangular_int, maybe_null,
    shared_products, shared_customers, STORES, CHANNELS, CAMPAIGNS,
    read_shared_identity,
)
from datetime import date, timedelta


def main():
    parser = base_argparser("S09 -- NexaMart four fact table types")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s09")
    outdir = resolve_output_dir(args, "s09")

    identity = read_shared_identity(args.team_seed)
    products = shared_products(args.team_seed, identity["n_products"])
    customers = shared_customers(args.team_seed, identity["n_customers"])

    start_d = date(2025, 1, 1)
    end_d = date(2025, 6, 30)  # 6 months to keep data manageable
    date_span = (end_d - start_d).days

    # ---- 1. TRANSACTION FACT: fact_orders ----
    n_orders = rng.randint(800, 2500)
    order_rows = []
    for i in range(1, n_orders + 1):
        d = start_d + timedelta(days=rng.randint(0, date_span))
        product = rng.choice(products)
        qty = triangular_int(rng, 1, 2, 8)
        order_rows.append({
            "transaction_id": i,
            "transaction_date": d.isoformat(),
            "transaction_type": weighted_choice(rng, ["sale","return","exchange"], [0.85, 0.10, 0.05]),
            "product_id": product["product_id"],
            "store_id": rng.choice(STORES)["store_id"],
            "customer_id": rng.choice(customers)["customer_id"],
            "quantity": qty if rng.random() > 0.10 else -qty,  # returns are negative
            "amount": round(product["unit_price"] * qty, 2),
        })

    # ---- 2. PERIODIC SNAPSHOT: fact_daily_inventory ----
    # Small subset: 10 products × 5 stores × 30 days (Jan 2025)
    snap_products = rng.sample(products, min(10, len(products)))
    snap_stores = rng.sample(STORES, 5)
    inventory_rows = []
    snap_id = 0
    for day_offset in range(30):
        d = date(2025, 1, 1) + timedelta(days=day_offset)
        for prod in snap_products:
            for store in snap_stores:
                snap_id += 1
                base_qty = triangular_int(rng, 0, 40, 150)
                inventory_rows.append({
                    "snapshot_id": snap_id,
                    "snapshot_date": d.isoformat(),
                    "product_id": prod["product_id"],
                    "store_id": store["store_id"],
                    "quantity_on_hand": max(0, base_qty + rng.randint(-15, 15)),
                    "quantity_on_order": max(0, rng.randint(0, 40)),
                    "days_of_supply": round(rng.uniform(1, 30), 1),
                })

    # ---- 3. ACCUMULATING SNAPSHOT: fact_order_pipeline ----
    n_pipeline = rng.randint(300, 800)
    pipeline_rows = []
    for i in range(1, n_pipeline + 1):
        order_d = start_d + timedelta(days=rng.randint(0, date_span))
        # Milestones: order → payment → pick → ship → deliver
        payment_d = order_d + timedelta(days=rng.randint(0, 2))
        pick_d = payment_d + timedelta(days=rng.randint(0, 3))
        ship_d = pick_d + timedelta(days=rng.randint(0, 4))
        deliver_d = ship_d + timedelta(days=rng.randint(1, 10))

        # Some orders stall at various stages
        stall_stage = weighted_choice(rng,
            ["completed","pending_ship","pending_pick","pending_payment","cancelled"],
            [0.70, 0.10, 0.07, 0.05, 0.08])

        pipeline_rows.append({
            "pipeline_id": i,
            "order_id": f"ORD-{i:06d}",
            "order_date": order_d.isoformat(),
            "payment_date": payment_d.isoformat() if stall_stage != "pending_payment" else None,
            "pick_date": pick_d.isoformat() if stall_stage in ["completed","pending_ship"] else None,
            "ship_date": ship_d.isoformat() if stall_stage == "completed" else None,
            "delivery_date": deliver_d.isoformat() if stall_stage == "completed" else None,
            "current_status": stall_stage,
            "days_order_to_deliver": (deliver_d - order_d).days if stall_stage == "completed" else None,
            "product_id": rng.choice(products)["product_id"],
            "store_id": rng.choice(STORES)["store_id"],
            "customer_id": rng.choice(customers)["customer_id"],
        })

    # ---- 4. FACTLESS FACT: fact_promo_exposure ----
    exposure_rows = []
    exp_id = 0
    active_campaigns = [c for c in CAMPAIGNS
                        if date.fromisoformat(c["start_date"]) <= end_d]
    for camp in active_campaigns:
        camp_start = max(start_d, date.fromisoformat(camp["start_date"]))
        camp_end = min(end_d, date.fromisoformat(camp["end_date"]))
        if camp_start > camp_end:
            continue
        # Each campaign exposes a subset of customers
        exposure_rate = rng.uniform(0.10, 0.60)
        exposed = rng.sample(customers, int(len(customers) * exposure_rate))
        for cust in exposed:
            exp_id += 1
            exposure_d = camp_start + timedelta(days=rng.randint(0, (camp_end - camp_start).days))
            exposure_rows.append({
                "exposure_id": exp_id,
                "exposure_date": exposure_d.isoformat(),
                "campaign_id": camp["campaign_id"],
                "customer_id": cust["customer_id"],
                "channel_id": rng.choice(CHANNELS)["channel_id"],
                # No measure columns -- this is a factless fact
            })

    counts = {}
    counts["fact_orders_transaction.csv"] = write_csv(
        outdir / "fact_orders_transaction.csv",
        ["transaction_id","transaction_date","transaction_type","product_id",
         "store_id","customer_id","quantity","amount"],
        order_rows,
    )
    counts["fact_daily_inventory.csv"] = write_csv(
        outdir / "fact_daily_inventory.csv",
        ["snapshot_id","snapshot_date","product_id","store_id",
         "quantity_on_hand","quantity_on_order","days_of_supply"],
        inventory_rows,
    )
    counts["fact_order_pipeline.csv"] = write_csv(
        outdir / "fact_order_pipeline.csv",
        ["pipeline_id","order_id","order_date","payment_date","pick_date",
         "ship_date","delivery_date","current_status","days_order_to_deliver",
         "product_id","store_id","customer_id"],
        pipeline_rows,
    )
    counts["fact_promo_exposure.csv"] = write_csv(
        outdir / "fact_promo_exposure.csv",
        ["exposure_id","exposure_date","campaign_id","customer_id","channel_id"],
        exposure_rows,
    )

    banner("S09 -- Four Fact Types", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
