"""
01_generate_deals.py
Generates a batch of synthetic Plait deals for the routing pipeline.

Mix is hybrid: weighted toward realistic proportions (most deals clean),
but every batch forces at least one deal per routing branch so all six
branches are always demonstrable. This is stated openly in the README.

Output: deals.json (HubSpot push handled separately in the n8n stage).
"""

import json
import random

random.seed()  # remove or fix a seed for reproducible batches

BATCH_SIZE = 30

FIRST = ["Amara", "Tunde", "Ngozi", "Emeka", "Zainab", "Kofi", "Ada", "Femi",
         "Chidi", "Yemi", "Sade", "Obi"]
COMPANIES = ["Northbeam Labs", "Quartzline", "Fieldstone Analytics", "Havel & Co",
             "Brightmark Systems", "Cedar Loop", "Tidewater Data", "Onyx Metrics",
             "Lanternworks", "Grovepoint", "Silverbirch", "Mosaic Ledger"]

# --- deal shapes, one per routing branch ---

def clean_deal():
    """Standard deal: inside discount band, standard terms, normal size."""
    return {
        "tier": random.choice(["Team", "Business"]),
        "acv": random.randint(3_000, 15_000),
        "discount": round(random.uniform(0.0, 0.15), 2),
        "terms": random.choice(["monthly", "annual"]),
    }

def over_discount():
    """Trips the sales-manager gate."""
    d = clean_deal()
    d["discount"] = round(random.uniform(0.16, 0.40), 2)
    return d

def custom_terms():
    """Trips the finance gate."""
    d = clean_deal()
    d["terms"] = "custom"
    return d

def enterprise():
    """Trips the leadership gate."""
    d = clean_deal()
    d["acv"] = random.randint(25_000, 60_000)
    return d

def monster():
    """Trips all three gates at once."""
    return {
        "tier": "Business",
        "acv": random.randint(30_000, 60_000),
        "discount": round(random.uniform(0.25, 0.40), 2),
        "terms": "custom",
    }

def free_tier():
    """No quote path."""
    return {"tier": "Free", "acv": 0, "discount": 0.0, "terms": "monthly"}


def generate_batch(n=BATCH_SIZE):
    # 1) forced coverage: one of each branch, guaranteed
    deals = [clean_deal(), over_discount(), custom_terms(),
             enterprise(), monster(), free_tier()]

    # 2) fill the rest with a realistic weighting
    fillers = [clean_deal, over_discount, custom_terms, enterprise, free_tier]
    weights = [0.72,       0.10,          0.07,         0.05,       0.06]
    while len(deals) < n:
        maker = random.choices(fillers, weights=weights, k=1)[0]
        deals.append(maker())

    random.shuffle(deals)

    # attach identity fields
    for i, d in enumerate(deals, start=1):
        d["deal_id"] = f"PLT-{i:04d}"
        d["contact"] = random.choice(FIRST)
        d["company"] = random.choice(COMPANIES)

    return deals


if __name__ == "__main__":
    batch = generate_batch()
    with open("deals.json", "w") as f:
        json.dump(batch, f, indent=2)
    print(f"Wrote {len(batch)} deals to deals.json")
