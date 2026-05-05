#!/usr/bin/env python3
"""
Generate NexaMart conformed dimension seed pack.

Produces the "CEO office" shared seeds that all departments reference:
  dim_date.csv, dim_product.csv, dim_store.csv, dim_channel.csv, dim_customer.csv

Usage:
    python scripts/datagen/gen_shared_seeds.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, build_dim_date,
    write_csv, banner, STORES, CHANNELS, PRODUCTS_MASTER,
    shared_customers, shared_products, write_shared_identity,
)
from datetime import date

def main():
    parser = base_argparser("Generate NexaMart shared conformed dimension seeds")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "shared-seeds")
    outdir = resolve_output_dir(args, "shared")
    counts = {}

    # dim_date: 2 years of history
    dim_date = build_dim_date(date(2024, 1, 1), date(2025, 12, 31))
    counts["dim_date.csv"] = write_csv(
        outdir / "dim_date.csv",
        ["date_key","year","quarter","month","month_name","week_iso","day_of_week","day_name","is_weekend"],
        dim_date,
    )

    # dim_product: team-specific subset of 40-70 products
    n_products = rng.randint(40, 70)
    products = shared_products(args.team_seed, n_products)
    counts["dim_product.csv"] = write_csv(
        outdir / "dim_product.csv",
        ["product_id","product_name","category","subcategory","brand","unit_cost","unit_price"],
        products,
    )

    # dim_store: all 10 stores (canonical)
    counts["dim_store.csv"] = write_csv(
        outdir / "dim_store.csv",
        ["store_id","store_name","city","region","province","store_type"],
        STORES,
    )

    # dim_channel: all 5 channels (canonical)
    counts["dim_channel.csv"] = write_csv(
        outdir / "dim_channel.csv",
        ["channel_id","channel_name","channel_type"],
        CHANNELS,
    )

    # dim_customer: team-specific 150-400 customers
    n_customers = rng.randint(150, 400)
    customers = shared_customers(args.team_seed, n_customers)
    counts["dim_customer.csv"] = write_csv(
        outdir / "dim_customer.csv",
        ["customer_id","first_name","last_name","email_domain","city","province",
         "loyalty_segment","join_date"],
        customers,
    )

    # Persist the chosen counts so every session generator can reuse the
    # SAME product/customer universe -- guarantees zero orphan FKs.
    # Also writes meta/dataset_identity.json at repo root.
    write_shared_identity(args.team_seed, n_products=n_products, n_customers=n_customers)

    banner("Shared Seeds", args.team_seed, outdir, counts)

if __name__ == "__main__":
    main()
