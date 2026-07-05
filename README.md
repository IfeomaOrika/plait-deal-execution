# Plait Deal Execution

Routing + quote generation for Plait deals. Picks up where the scoring
pipeline (What Sales Sees) leaves off: a scored deal enters, gets routed
through the right approval gates, and on approval a quote PDF is generated.

## The flow

deal enters -> routing logic decides which approval gates apply ->
gates cleared -> order-form PDF generated

## Scripts

- `01_generate_deals.py` — synthetic deal generator. Hybrid mix: weighted
  toward realistic proportions (most deals clean) but every batch forces at
  least one deal per routing branch, so all branches are always demonstrable.
  Note: at small batch sizes the forced-coverage floor skews the mix
  exception-heavy; this evens out at larger batches.
- `02_route_deal.py` — the routing logic. Evaluates each deal against the
  deal-desk policy and returns the set of approval gates required. Gates
  accumulate: one deal can require several sign-offs. Run directly to see
  the built-in branch tests.
- `03_generate_quote.py` — renders an approved deal into an order-form PDF
  via `templates/quote.html`. List price is reconstructed from the discounted
  ACV so the discount math reconciles on the document.

## Policy thresholds

Set in `02_route_deal.py` as named constants. Illustrative, but the ratios
are realistic for a self-serve product like Plait:

- Discounts over 15% require a sales manager
- Non-standard terms require finance
- Deals at/above $25k ACV require leadership

## Note on data

All deals are synthetic. This is a portfolio artifact demonstrating routing
and document-generation design, not real commercial data. The generated PDFs
state this in their footer.

## Running it

    pip install -r requirements.txt
    # WeasyPrint needs a few system libs — see weasyprint.org install docs

    python3 02_route_deal.py       # prints PASS/FAIL for each routing branch
    python3 01_generate_deals.py   # writes deals.json
    python3 03_generate_quote.py   # writes a quote PDF into output/
