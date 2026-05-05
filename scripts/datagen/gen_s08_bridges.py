#!/usr/bin/env python3
"""
S08 -- Bridges, M:N, SCD3/hybrid lab.

NexaMart Marketing & Loyalty department:
  - bridge_customer_segment (weighted M:N)
  - campaign_allocation (weighted bridge)
  - customer_history (SCD3: current + previous segment)
  - dim_segment_outrigger

Usage:
    python scripts/datagen/gen_s08_bridges.py --team-seed 7
"""
from _helpers import (
    base_argparser, resolve_output_dir, make_rng, write_csv, banner,
    weighted_choice, shared_customers, SEGMENTS, CAMPAIGNS,
    read_shared_identity,
)
from datetime import date, timedelta


def main():
    parser = base_argparser("S08 -- NexaMart bridges, M:N, SCD3")
    args = parser.parse_args()
    rng = make_rng(args.team_seed, "s08")
    outdir = resolve_output_dir(args, "s08")

    identity = read_shared_identity(args.team_seed)
    customers = shared_customers(args.team_seed, identity["n_customers"])

    # --- Bridge: customer ↔ segment (M:N with weights) ---
    overlap_density = rng.uniform(1.2, 2.5)  # avg segments per customer
    bridge_rows = []
    bridge_id = 0
    for cust in customers:
        n_segments = max(1, int(rng.gauss(overlap_density, 0.7)))
        n_segments = min(n_segments, len(SEGMENTS))
        assigned = rng.sample(SEGMENTS, n_segments)
        # Generate weights that sum to 1.0
        raw_weights = [rng.uniform(0.1, 1.0) for _ in assigned]
        total = sum(raw_weights)
        for seg, w in zip(assigned, raw_weights):
            bridge_id += 1
            bridge_rows.append({
                "bridge_id": bridge_id,
                "customer_id": cust["customer_id"],
                "segment": seg,
                "weight": round(w / total, 4),
                "effective_date": cust["join_date"],
                "is_primary": 1 if w == max(raw_weights) else 0,
            })

    # --- Campaign allocation bridge (campaign ↔ segment with budget weight) ---
    campaign_alloc = []
    alloc_id = 0
    for camp in CAMPAIGNS:
        n_target_segments = rng.randint(1, 4)
        target_segs = rng.sample(SEGMENTS[:5], n_target_segments)  # exclude Inactive
        raw_w = [rng.uniform(0.1, 1.0) for _ in target_segs]
        total_w = sum(raw_w)
        for seg, w in zip(target_segs, raw_w):
            alloc_id += 1
            campaign_alloc.append({
                "allocation_id": alloc_id,
                "campaign_id": camp["campaign_id"],
                "segment": seg,
                "budget_weight": round(w / total_w, 4),
                "planned_spend": round(rng.uniform(2000, 50000) * (w / total_w), 2),
            })

    # --- SCD3: customer history with current + previous segment ---
    scd3_rows = []
    pct_changed = rng.uniform(0.20, 0.50)
    n_changed = int(len(customers) * pct_changed)
    changers = rng.sample(customers, n_changed)
    for cust in customers:
        if cust in changers:
            prev_seg = cust["loyalty_segment"]
            curr_seg = rng.choice([s for s in SEGMENTS if s != prev_seg])
            change_d = (date.fromisoformat(cust["join_date"]) +
                       timedelta(days=rng.randint(60, 600)))
            scd3_rows.append({
                "customer_id": cust["customer_id"],
                "current_segment": curr_seg,
                "previous_segment": prev_seg,
                "segment_change_date": min(change_d, date(2025, 12, 31)).isoformat(),
                "city": cust["city"],
                "province": cust["province"],
            })
        else:
            scd3_rows.append({
                "customer_id": cust["customer_id"],
                "current_segment": cust["loyalty_segment"],
                "previous_segment": None,
                "segment_change_date": None,
                "city": cust["city"],
                "province": cust["province"],
            })

    # --- Segment outrigger dimension ---
    segment_outrigger = []
    seg_benefits = {
        "Platinum": {"discount_pct": 20, "free_shipping": 1, "priority_support": 1, "annual_reward": 500},
        "Gold":     {"discount_pct": 15, "free_shipping": 1, "priority_support": 1, "annual_reward": 200},
        "Silver":   {"discount_pct": 10, "free_shipping": 1, "priority_support": 0, "annual_reward": 50},
        "Bronze":   {"discount_pct": 5,  "free_shipping": 0, "priority_support": 0, "annual_reward": 0},
        "New":      {"discount_pct": 10, "free_shipping": 1, "priority_support": 0, "annual_reward": 0},
        "Inactive": {"discount_pct": 0,  "free_shipping": 0, "priority_support": 0, "annual_reward": 0},
    }
    for seg in SEGMENTS:
        b = seg_benefits[seg]
        segment_outrigger.append({
            "segment": seg,
            "discount_pct": b["discount_pct"],
            "free_shipping": b["free_shipping"],
            "priority_support": b["priority_support"],
            "annual_reward_value": b["annual_reward"],
        })

    counts = {}
    counts["bridge_customer_segment.csv"] = write_csv(
        outdir / "bridge_customer_segment.csv",
        ["bridge_id","customer_id","segment","weight","effective_date","is_primary"],
        bridge_rows,
    )
    counts["bridge_campaign_allocation.csv"] = write_csv(
        outdir / "bridge_campaign_allocation.csv",
        ["allocation_id","campaign_id","segment","budget_weight","planned_spend"],
        campaign_alloc,
    )
    counts["customer_scd3_history.csv"] = write_csv(
        outdir / "customer_scd3_history.csv",
        ["customer_id","current_segment","previous_segment","segment_change_date","city","province"],
        scd3_rows,
    )
    counts["dim_segment_outrigger.csv"] = write_csv(
        outdir / "dim_segment_outrigger.csv",
        ["segment","discount_pct","free_shipping","priority_support","annual_reward_value"],
        segment_outrigger,
    )

    banner("S08 -- Bridges & SCD3", args.team_seed, outdir, counts)


if __name__ == "__main__":
    main()
