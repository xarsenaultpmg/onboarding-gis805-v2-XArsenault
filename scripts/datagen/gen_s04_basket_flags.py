#!/usr/bin/env python3
"""
S04 -- Degenerate + junk dimension lab.

NexaMart orders with order numbers (degenerate dim) and boolean
operational flags consolidated into a junk dimension.

Usage:
    python scripts/datagen/gen_s04_basket_flags.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, triangular_int, shared_products, shared_customers,
    STORES, CHANNELS, read_shared_identity,
)
from datetime import date, timedelta


FLAG_NAMES = [
    "is_gift_wrapped", "is_express_shipping", "is_loyalty_redeemed",
    "is_promo_applied", "is_employee_purchase", "is_online_pickup",
    "is_fragile", "is_oversized",
]


def main():
    parser = base_argparser("S04 -- NexaMart degenerate + junk dimension lab")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s04")
    outdir = resolve_output_dir(args, "s04")

    identity = read_shared_identity(args.team_seed)
    products = shared_products(args.team_seed, identity["n_products"])
    customers = shared_customers(args.team_seed, identity["n_customers"])

    # Team-specific flag base rates (different teams get different flag distributions)
    flag_rates = {f: rng.uniform(0.03, 0.35) for f in FLAG_NAMES}

    # Seasonal flag spikes
    spike_flag = rng.choice(FLAG_NAMES[:4])
    spike_month = rng.choice([11, 12, 6, 7])

    n_orders = rng.randint(300, 800)
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    date_span = (end_date - start_date).days

    orders = []
    order_lines = []
    line_id = 0

    for order_num in range(1, n_orders + 1):
        d = start_date + timedelta(days=rng.randint(0, date_span))
        store = rng.choice(STORES)
        channel = rng.choice(CHANNELS)
        customer = rng.choice(customers)

        # Build flags
        flags = {}
        for f in FLAG_NAMES:
            rate = flag_rates[f]
            if f == spike_flag and d.month == spike_month:
                rate = min(rate * 3, 0.85)
            flags[f] = 1 if rng.random() < rate else 0

        orders.append({
            "order_number": f"ORD-{order_num:06d}",
            "order_date": d.isoformat(),
            "customer_id": customer["customer_id"],
            "store_id": store["store_id"],
            "channel_id": channel["channel_id"],
            **flags,
        })

        # Order lines (basket analysis)
        n_lines = triangular_int(rng, 1, 2, 7)
        basket = rng.sample(products, min(n_lines, len(products)))
        for product in basket:
            line_id += 1
            qty = triangular_int(rng, 1, 1, 5)
            order_lines.append({
                "line_id": line_id,
                "order_number": f"ORD-{order_num:06d}",
                "product_id": product["product_id"],
                "quantity": qty,
                "unit_price": product["unit_price"],
                "line_total": round(product["unit_price"] * qty, 2),
            })

    counts = {}
    counts["orders.csv"] = write_csv(
        outdir / "orders.csv",
        ["order_number","order_date","customer_id","store_id","channel_id"] + FLAG_NAMES,
        orders,
    )
    counts["order_lines.csv"] = write_csv(
        outdir / "order_lines.csv",
        ["line_id","order_number","product_id","quantity","unit_price","line_total"],
        order_lines,
    )

    banner("S04 -- Basket & Flags", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
