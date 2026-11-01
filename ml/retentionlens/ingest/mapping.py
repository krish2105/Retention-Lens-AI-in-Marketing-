"""Map whatever headers a customer's invoice export uses onto the canonical columns."""
from __future__ import annotations

import re

from ..data.load import CANONICAL, HEADER_MAP

REQUIRED = ["invoice", "invoice_date", "quantity", "price", "customer_id"]
OPTIONAL = ["stock_code", "description", "country"]

# Normalised header (lower case, letters and digits only) -> canonical column.
ALIASES = {
    "invoice": ["invoice", "invoiceno", "invoicenumber", "invoiceid", "orderid", "order", "orderno", "ordernumber", "documentno", "billno", "salesorder"],
    "stock_code": ["stockcode", "sku", "productcode", "itemcode", "productid", "itemid", "item", "code", "partno", "partnumber"],
    "description": ["description", "productname", "itemname", "product", "itemdescription", "productdescription", "name", "item"],
    "quantity": ["quantity", "qty", "units", "unitsordered", "qtyordered", "count"],
    "invoice_date": ["invoicedate", "date", "orderdate", "invoicedatetime", "transactiondate", "createdat", "datetime", "timestamp", "documentdate"],
    "price": ["price", "unitprice", "priceperunit", "unitcost", "rate", "sellingprice", "netprice"],
    "customer_id": ["customerid", "customer", "customerno", "customernumber", "customercode", "accountid", "account", "accountno", "accountcode", "clientid", "buyerid"],
    "country": ["country", "countrycode", "shiptocountry", "market", "region"],
}


def normalise(header: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(header).lower())


def suggest_mapping(headers: list[str]) -> dict[str, str | None]:
    """Canonical column -> source header, or None when nothing matches. Each header is used once."""
    mapping: dict[str, str | None] = {c: None for c in CANONICAL}
    used: set[str] = set()
    for header in headers:
        target = HEADER_MAP.get(str(header).strip())
        if target and mapping[target] is None:
            mapping[target], used = header, used | {header}
    for column in CANONICAL:
        if mapping[column] is not None:
            continue
        for alias in ALIASES[column]:
            match = next((h for h in headers if h not in used and normalise(h) == alias), None)
            if match is not None:
                mapping[column], used = match, used | {match}
                break
    return mapping


def check_mapping(mapping: dict[str, str | None], headers: list[str]) -> list[str]:
    """Problems that stop an import: missing required columns, unknown headers, a header used twice."""
    problems = [f"Choose a column for {c.replace('_', ' ')}" for c in REQUIRED if not mapping.get(c)]
    chosen = [h for h in mapping.values() if h]
    problems += [f"Column '{h}' is not in the file" for h in chosen if h not in headers]
    problems += [f"Column '{h}' is used more than once" for h in sorted({h for h in chosen if chosen.count(h) > 1})]
    return problems
