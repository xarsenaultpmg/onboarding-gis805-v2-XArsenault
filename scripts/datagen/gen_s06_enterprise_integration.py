#!/usr/bin/env python3
"""
S06 -- Enterprise integration night.

All four NexaMart departments produce their fact tables:
  Sales:      fact_sales, fact_returns
  Operations: fact_inventory_snapshot
  Finance:    fact_budget

Students write drill-across queries and actual-vs-target views
using conformed dimensions.

Usage:
    python scripts/datagen/gen_s06_enterprise_integration.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, triangular_int, shared_products, shared_customers,
    STORES, CHANNELS, CATEGORIES, read_shared_identity,
)
from datetime import date, timedelta


def main():
    parser = base_argparser("S06 -- NexaMart enterprise integration / multi-fact")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s06")
    outdir = resolve_output_dir(args, "s06")

    identity = read_shared_identity(args.team_seed)
    products = shared_products(args.team_seed, identity["n_products"])
    customers = shared_customers(args.team_seed, identity["n_customers"])

    start_d = date(2025, 1, 1)
    end_d = date(2025, 12, 31)
    date_span = (end_d - start_d).days

    # --- FACT_SALES ---
    n_sales = rng.randint(1500, 4000)
    store_weights = [rng.uniform(0.5, 2.5) for _ in STORES]
    sales_rows = []
    order_num = 0
    line_in_order = 0
    current_order_meta = None  # (date, customer, store, channel)
    for i in range(1, n_sales + 1):
        # Start a new order roughly every 2-5 lines
        if current_order_meta is None or line_in_order >= rng.randint(2, 5):
            order_num += 1
            d = start_d + timedelta(days=rng.randint(0, date_span))
            customer = rng.choice(customers)
            store = weighted_choice(rng, STORES, store_weights)
            channel = rng.choice(CHANNELS)
            current_order_meta = (d, customer, store, channel)
            line_in_order = 0
        d, customer, store, channel = current_order_meta
        line_in_order += 1
        product = rng.choice(products)
        qty = triangular_int(rng, 1, 2, 6)
        discount_pct = weighted_choice(rng, [0, 0.05, 0.10, 0.15, 0.20],
                                       [0.55, 0.15, 0.15, 0.10, 0.05])
        net_price = round(product["unit_price"] * (1 - discount_pct), 2)
        sales_rows.append({
            "sale_line_id": i,
            "order_number": f"ORD-{order_num:06d}",
            "order_date": d.isoformat(),
            "customer_id": customer["customer_id"],
            "product_id": product["product_id"],
            "store_id": store["store_id"],
            "channel_id": channel["channel_id"],
            "quantity": qty,
            "unit_price": product["unit_price"],
            "discount_pct": discount_pct,
            "net_price": net_price,
            "line_total": round(net_price * qty, 2),
        })

    # --- FACT_RETURNS ---
    return_rate = rng.uniform(0.05, 0.18)
    n_returns = int(n_sales * return_rate)
    returned_sales = rng.sample(sales_rows, n_returns)
    returns_rows = []
    for idx, sale in enumerate(returned_sales, 1):
        sale_d = date.fromisoformat(sale["order_date"])
        return_d = sale_d + timedelta(days=rng.randint(1, 45))
        return_qty = rng.randint(1, sale["quantity"])
        reason = weighted_choice(rng,
            ["defective","wrong_size","changed_mind","damaged_shipping","duplicate"],
            [0.25, 0.20, 0.30, 0.15, 0.10])
        returns_rows.append({
            "return_id": idx,
            "original_sale_line_id": sale["sale_line_id"],
            "return_date": min(return_d, end_d).isoformat(),
            "product_id": sale["product_id"],
            "store_id": sale["store_id"],
            "return_quantity": return_qty,
            "refund_amount": round(sale["net_price"] * return_qty, 2),
            "return_reason": reason,
        })

    # --- FACT_INVENTORY_SNAPSHOT (periodic: weekly snapshots) ---
    inventory_rows = []
    snap_id = 0
    # Each product × each store has a weekly snapshot
    product_store_pairs = [(p, s) for p in rng.sample(products, min(25, len(products)))
                           for s in rng.sample(STORES, rng.randint(3, 7))]
    snap_date = start_d
    while snap_date <= end_d:
        for prod, store in product_store_pairs:
            snap_id += 1
            base_qty = triangular_int(rng, 5, 50, 200)
            # Seasonal variation
            if snap_date.month in [11, 12]:
                base_qty = int(base_qty * rng.uniform(0.4, 0.8))  # stock drawdown
            inventory_rows.append({
                "snapshot_id": snap_id,
                "snapshot_date": snap_date.isoformat(),
                "product_id": prod["product_id"],
                "store_id": store["store_id"],
                "quantity_on_hand": max(0, base_qty + rng.randint(-20, 20)),
                "quantity_on_order": max(0, triangular_int(rng, 0, 10, 60)),
                "reorder_point": rng.choice([10, 15, 20, 25, 30]),
            })
        snap_date += timedelta(days=7)

    # --- FACT_BUDGET (monthly budget targets by category × store) ---
    budget_rows = []
    budget_id = 0
    cat_store_pairs = [(cat, store) for cat in CATEGORIES
                       for store in STORES]
    for month in range(1, 13):
        for cat, store in cat_store_pairs:
            budget_id += 1
            base_target = rng.uniform(5000, 80000)
            # Budget bias: some teams get optimistic budgets, some pessimistic
            bias = rng.uniform(0.8, 1.3)
            budget_rows.append({
                "budget_id": budget_id,
                "budget_month": f"2025-{month:02d}-01",
                "category": cat,
                "store_id": store["store_id"],
                "target_revenue": round(base_target * bias, 2),
                "target_units": int(base_target * bias / rng.uniform(15, 50)),
            })

    counts = {}
    counts["fact_sales.csv"] = write_csv(
        outdir / "fact_sales.csv",
        ["sale_line_id","order_number","order_date","customer_id","product_id",
         "store_id","channel_id","quantity","unit_price","discount_pct",
         "net_price","line_total"],
        sales_rows,
    )
    counts["fact_returns.csv"] = write_csv(
        outdir / "fact_returns.csv",
        ["return_id","original_sale_line_id","return_date","product_id","store_id",
         "return_quantity","refund_amount","return_reason"],
        returns_rows,
    )
    counts["fact_inventory_snapshot.csv"] = write_csv(
        outdir / "fact_inventory_snapshot.csv",
        ["snapshot_id","snapshot_date","product_id","store_id",
         "quantity_on_hand","quantity_on_order","reorder_point"],
        inventory_rows,
    )
    counts["fact_budget.csv"] = write_csv(
        outdir / "fact_budget.csv",
        ["budget_id","budget_month","category","store_id","target_revenue","target_units"],
        budget_rows,
    )

    banner("S06 -- Enterprise Integration", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
