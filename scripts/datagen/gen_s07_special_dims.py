#!/usr/bin/env python3
"""
S07 -- Special dimensions lab.

NexaMart fulfillment with:
  - Role-playing dates (order_date, ship_date, delivery_date)
  - Geography hierarchy (store → city → region → province)
  - NULL handling (unknown carrier, missing delivery dates)
  - Mini-dimension potential (customer age-band, spend-band)

Usage:
    python scripts/datagen/gen_s07_special_dims.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, triangular_int, maybe_null, shared_products,
    shared_customers, STORES, CHANNELS, read_shared_identity,
)
from datetime import date, timedelta


CARRIERS = ["Purolator", "Canada Post", "FedEx", "UPS", "DHL", "Local Courier"]


def main():
    parser = base_argparser("S07 -- NexaMart special dimensions (role-playing, hierarchies, NULLs)")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s07")
    outdir = resolve_output_dir(args, "s07")

    identity = read_shared_identity(args.team_seed)
    products = shared_products(args.team_seed, identity["n_products"])
    customers = shared_customers(args.team_seed, identity["n_customers"])

    # Team-specific NULL rates
    null_carrier_rate = rng.uniform(0.05, 0.25)
    null_delivery_rate = rng.uniform(0.08, 0.30)

    n_shipments = rng.randint(600, 2000)
    start_d = date(2025, 1, 1)
    end_d = date(2025, 12, 31)
    date_span = (end_d - start_d).days

    shipment_rows = []
    for i in range(1, n_shipments + 1):
        order_d = start_d + timedelta(days=rng.randint(0, date_span))
        processing_days = triangular_int(rng, 0, 1, 5)
        ship_d = order_d + timedelta(days=processing_days)
        transit_days = triangular_int(rng, 1, 3, 14)
        delivery_d = ship_d + timedelta(days=transit_days)

        # Some deliveries are still in transit (NULL delivery_date)
        if rng.random() < null_delivery_rate:
            delivery_d_str = None
            delivery_status = "in_transit"
        else:
            delivery_d_str = min(delivery_d, end_d).isoformat()
            delivery_status = weighted_choice(rng, ["delivered","returned","failed"], [0.90, 0.05, 0.05])

        carrier = maybe_null(rng, rng.choice(CARRIERS), null_carrier_rate)

        store = rng.choice(STORES)
        product = rng.choice(products)
        customer = rng.choice(customers)

        # Destination hierarchy (sometimes different from store)
        dest_city = customer["city"]
        dest_province = customer["province"]

        shipment_rows.append({
            "shipment_id": i,
            "order_date": order_d.isoformat(),
            "ship_date": ship_d.isoformat(),
            "delivery_date": delivery_d_str,
            "product_id": product["product_id"],
            "store_id": store["store_id"],
            "customer_id": customer["customer_id"],
            "channel_id": rng.choice(CHANNELS)["channel_id"],
            "carrier": carrier,
            "destination_city": dest_city,
            "destination_province": dest_province,
            "delivery_status": delivery_status,
            "shipping_cost": round(rng.uniform(4.99, 35.00), 2),
        })

    # Geography hierarchy dimension (for hierarchy design exercise)
    geo_rows = []
    seen_cities = set()
    for s in STORES:
        if s["city"] not in seen_cities:
            seen_cities.add(s["city"])
            geo_rows.append({
                "city": s["city"],
                "region": s["region"],
                "province": s["province"],
                "country": "Canada",
            })
    for c in customers:
        if c["city"] not in seen_cities:
            seen_cities.add(c["city"])
            geo_rows.append({
                "city": c["city"],
                "region": "Unknown",
                "province": c["province"],
                "country": "Canada",
            })

    # Mini-dimension seed: customer spend bands
    spend_bands = []
    for c in customers:
        spend_bands.append({
            "customer_id": c["customer_id"],
            "age_band": weighted_choice(rng, ["18-25","26-35","36-45","46-55","56-65","65+"],
                                        [0.10, 0.25, 0.25, 0.20, 0.12, 0.08]),
            "spend_band": weighted_choice(rng, ["low","medium","high","premium"],
                                          [0.30, 0.35, 0.25, 0.10]),
            "frequency_band": weighted_choice(rng, ["rare","occasional","regular","frequent"],
                                              [0.20, 0.35, 0.30, 0.15]),
        })

    counts = {}
    counts["fact_shipment.csv"] = write_csv(
        outdir / "fact_shipment.csv",
        ["shipment_id","order_date","ship_date","delivery_date","product_id",
         "store_id","customer_id","channel_id","carrier","destination_city",
         "destination_province","delivery_status","shipping_cost"],
        shipment_rows,
    )
    counts["dim_geography.csv"] = write_csv(
        outdir / "dim_geography.csv",
        ["city","region","province","country"],
        geo_rows,
    )
    counts["customer_profile_bands.csv"] = write_csv(
        outdir / "customer_profile_bands.csv",
        ["customer_id","age_band","spend_band","frequency_band"],
        spend_bands,
    )

    banner("S07 -- Special Dimensions", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
