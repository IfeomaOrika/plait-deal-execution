"""
02_route_deal.py
Routing logic for Plait deal execution.
Takes a single deal, returns the set of approval gates it must pass.

This is the judgment layer. n8n orchestrates; this decides.
Gates accumulate: one deal can require several sign-offs.
"""

# --- thresholds (the deal-desk policy, stated plainly) ---
DISCOUNT_AUTO_LIMIT = 0.15      # up to 15% discount needs no manager
ENTERPRISE_ACV = 25_000        # at/above this, leadership signs off
STANDARD_TERMS = {"monthly", "annual"}


def route_deal(deal):
    """
    deal: dict with keys tier, acv, discount, terms
    returns: dict with the decision and the gates required
    """
    gates = []

    # Free tier never produces a paid quote
    if deal["tier"] == "Free":
        return {"decision": "no_quote", "gates": [], "reason": "Free tier"}

    # discount above the auto band -> sales manager
    if deal["discount"] > DISCOUNT_AUTO_LIMIT:
        gates.append("sales_manager")

    # non-standard terms -> finance
    if deal["terms"] not in STANDARD_TERMS:
        gates.append("finance")

    # large deal -> leadership, regardless of the above
    if deal["acv"] >= ENTERPRISE_ACV:
        gates.append("leadership")

    if not gates:
        return {"decision": "auto_approve", "gates": []}

    return {"decision": "needs_approval", "gates": gates}


# --- test cases: one deal per branch, written by hand ---
if __name__ == "__main__":
    tests = [
        # (label, deal, expected gates)
        ("standard clean",      {"tier": "Team",     "acv": 6000,  "discount": 0.10, "terms": "annual"},  []),
        ("discount over band",  {"tier": "Business", "acv": 12000, "discount": 0.30, "terms": "annual"},  ["sales_manager"]),
        ("non-standard terms",  {"tier": "Team",     "acv": 8000,  "discount": 0.10, "terms": "custom"},  ["finance"]),
        ("enterprise size",     {"tier": "Business", "acv": 40000, "discount": 0.10, "terms": "annual"},  ["leadership"]),
        ("deep discount + big", {"tier": "Business", "acv": 50000, "discount": 0.35, "terms": "custom"},  ["sales_manager", "finance", "leadership"]),
        ("free tier",           {"tier": "Free",     "acv": 0,     "discount": 0.0,  "terms": "monthly"}, []),
    ]

    for label, deal, expected in tests:
        result = route_deal(deal)
        ok = result["gates"] == expected
        flag = "PASS" if ok else "FAIL"
        print(f"[{flag}] {label:22} -> {result['decision']:14} gates={result['gates']}")
