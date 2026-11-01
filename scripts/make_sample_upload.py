"""Write a SYNTHETIC invoice export for trying the upload wizard (not real customers).

Headers deliberately differ from Online Retail II ("Order No", "SKU", "Qty", ...) so the
column mapping step has work to do. Seeded, so the file is reproducible.

  python3 scripts/make_sample_upload.py  ->  data/samples/synthetic_wholesale_invoices.csv
"""
from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "samples" / "synthetic_wholesale_invoices.csv"
PRODUCTS = [("GC-100", "Gift card set", 2.5), ("MUG-12", "Enamel mug", 4.2), ("CAN-07", "Soy candle", 6.9), ("TEA-20", "Loose tea tin", 3.6),
            ("BAG-03", "Jute tote", 1.9), ("LMP-55", "Table lamp", 18.0), ("NTB-09", "Linen notebook", 2.2), ("POST", "Postage", 15.0)]
COUNTRIES = ["United Kingdom"] * 7 + ["United Arab Emirates", "France", "Germany"]


def main(seed: int = 7, customers: int = 120, out: Path = OUT) -> None:
    rng = random.Random(seed)
    start, end = date(2024, 1, 2), date(2025, 6, 30)
    rows, invoice = [], 50000
    for c in range(customers):
        account = f"ACC-{1000 + c}"
        country = rng.choice(COUNTRIES)
        gap = rng.choice([14, 21, 30, 45, 60, 90])
        day = start + timedelta(days=rng.randint(0, 200))
        churn_day = start + timedelta(days=rng.randint(150, 600))
        while day <= min(end, churn_day):
            invoice += 1
            for code, name, price in rng.sample(PRODUCTS, rng.randint(1, 4)):
                qty = rng.choice([6, 12, 24, 48]) if code != "POST" else 1
                rows.append({"Order No": f"SO{invoice}", "SKU": code, "Item": name, "Qty": qty, "Order Date": day.strftime("%d/%m/%Y"),
                             "Unit Price": f"{price:.2f}", "Account": account, "Country": country})
            if rng.random() < 0.04:  # a credit note for part of the order
                invoice += 1
                rows.append({"Order No": f"C{invoice}", "SKU": "MUG-12", "Item": "Enamel mug", "Qty": -6, "Order Date": day.strftime("%d/%m/%Y"),
                             "Unit Price": "4.20", "Account": account, "Country": country})
            day += timedelta(days=max(3, int(rng.gauss(gap, gap / 3))))
    rows.append({"Order No": "SO-BAD", "SKU": "TEA-20", "Item": "Loose tea tin", "Qty": "twelve", "Order Date": "not a date", "Unit Price": "3.60", "Account": "ACC-1000", "Country": "United Kingdom"})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows for {customers} synthetic accounts to {out}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--customers", type=int, default=120)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    main(customers=args.customers, out=args.out)
