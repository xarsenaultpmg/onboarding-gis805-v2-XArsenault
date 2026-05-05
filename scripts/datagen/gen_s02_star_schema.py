#!/usr/bin/env python3
"""
S02 -- Star schema & grain lab.

NexaMart Sales department: basic fact_sales + conformed dims.
Students build their first star schema and write a query answering
the CEO question from S01.

Usage:
    python scripts/datagen/gen_s02_star_schema.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, triangular_int, STORES, CHANNELS,
    shared_customers, shared_products, read_shared_identity,
)
from datetime import date, timedelta


def main():
    parser = base_argparser("S02 -- NexaMart star schema / grain lab data")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s02")
    outdir = resolve_output_dir(args, "s02")

    # Load the SAME product/customer universe written by gen_shared_seeds.
    # Using identity counts guarantees fact_sales references only keys that
    # exist in dim_product / dim_customer (zero orphan FKs).
    identity = read_shared_identity(args.team_seed)
    products = shared_products(args.team_seed, identity["n_products"])
    customers = shared_customers(args.team_seed, identity["n_customers"])

    # Team-specific parameters
    n_orders = rng.randint(800, 2500)
    avg_lines = rng.triangular(1.5, 4.0, 2.5)
    seasonal_peak_month = rng.choice([6, 7, 11, 12])  # summer or holiday peak
    store_weights = [rng.uniform(0.5, 2.0) for _ in STORES]
    channel_weights = [rng.uniform(0.3, 3.0) for _ in CHANNELS]

    # Generate fact_sales rows
    start_date = date(2024, 1, 1)
    end_date = date(2025, 12, 31)
    date_span = (end_date - start_date).days

    sales_rows = []
    line_id = 0
    for order_num in range(1, n_orders + 1):
        # Date with seasonal weighting
        d = start_date + timedelta(days=rng.randint(0, date_span))
        # Boost probability of peak month orders
        if d.month == seasonal_peak_month:
            pass  # keep it
        elif rng.random() < 0.15:
            # Shift some orders into peak month
            d = d.replace(month=seasonal_peak_month, day=min(d.day, 28))

        store = weighted_choice(rng, STORES, store_weights)
        channel = weighted_choice(rng, CHANNELS, channel_weights)
        customer = rng.choice(customers)
        n_lines = max(1, int(rng.gauss(avg_lines, 1.2)))

        for _ in range(n_lines):
            line_id += 1
            product = rng.choice(products)
            qty = triangular_int(rng, 1, 2, 8)
            unit_price = product["unit_price"]
            discount_pct = weighted_choice(rng, [0, 5, 10, 15, 20, 25], [0.50, 0.15, 0.15, 0.10, 0.05, 0.05])
            net_price = round(unit_price * (1 - discount_pct / 100), 2)
            sales_rows.append({
                "sale_line_id": line_id,
                "order_number": f"ORD-{order_num:06d}",
                "order_date": d.isoformat(),
                "customer_id": customer["customer_id"],
                "product_id": product["product_id"],
                "store_id": store["store_id"],
                "channel_id": channel["channel_id"],
                "quantity": qty,
                "unit_price": unit_price,
                "discount_pct": discount_pct,
                "net_price": net_price,
                "line_total": round(net_price * qty, 2),
            })

    counts = {}
    counts["fact_sales.csv"] = write_csv(
        outdir / "fact_sales.csv",
        ["sale_line_id","order_number","order_date","customer_id","product_id",
         "store_id","channel_id","quantity","unit_price","discount_pct","net_price","line_total"],
        sales_rows,
    )

    banner("S02 -- Star Schema", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
