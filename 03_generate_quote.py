"""
03_generate_quote.py
Turns an approved Plait deal into an order-form PDF.

Called only after routing clears a deal (auto_approve, or all gates passed).
Renders templates/quote.html via WeasyPrint. Uses synthetic data throughout;
the footer states this openly.
"""

import json
import datetime
from pathlib import Path
from weasyprint import HTML

TEMPLATE = Path(__file__).parent / "templates" / "quote.html"
OUTDIR = Path(__file__).parent / "output"

TERMS_NOTE = {
    "monthly": "Billed monthly.",
    "annual": "Billed annually, paid upfront.",
    "custom": "Non-standard payment terms as agreed during negotiation.",
}


def build_quote(deal):
    """deal: dict with tier, acv, discount, terms, deal_id, company, contact."""
    acv = deal["acv"]
    discount = deal["discount"]

    # acv is the discounted figure; reconstruct list price so the math shows
    list_price = round(acv / (1 - discount)) if discount < 1 else acv
    discount_amt = list_price - acv

    fields = {
        "deal_id": deal["deal_id"],
        "date": datetime.date.today().strftime("%d %b %Y"),
        "company": deal["company"],
        "contact": deal["contact"],
        "tier": deal["tier"],
        "terms": deal["terms"],
        "list_price": f"{list_price:,}",
        "discount_pct": round(discount * 100),
        "discount_amt": f"{discount_amt:,}",
        "acv": f"{acv:,}",
        "terms_note": TERMS_NOTE.get(deal["terms"], ""),
    }

    html = TEMPLATE.read_text()
    for key, val in fields.items():
        html = html.replace("{{" + key + "}}", str(val))

    OUTDIR.mkdir(exist_ok=True)
    outpath = OUTDIR / f"quote_{deal['deal_id']}.pdf"
    HTML(string=html).write_pdf(str(outpath))
    return outpath


if __name__ == "__main__":
    # demo against a real deal from the batch
    deals = json.load(open(Path(__file__).parent / "deals.json"))
    target = next(d for d in deals if d["deal_id"] == "PLT-0010")
    path = build_quote(target)
    print(f"Quote written: {path}")
