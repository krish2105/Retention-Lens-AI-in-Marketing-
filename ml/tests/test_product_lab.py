import numpy as np
import pandas as pd

from retentionlens.product.lab import basket_rules, elasticity


def test_basket_rule_lift():
    rows = [(f"i{i}", c) for i in range(40) for c in ("A", "B")] + [(f"j{i}", "C") for i in range(60)]
    lines = pd.DataFrame(rows, columns=["invoice", "stock_code"]).assign(description=lambda d: d["stock_code"], is_sale=True)
    rules = basket_rules(lines, min_support=0.1, min_lift=1.5)
    ab = next(r for r in rules if r["if"] == "A" and r["then"] == "B")
    assert ab["confidence"] == 1.0 and ab["lift"] == 2.5 and ab["support"] == 0.4


def test_elasticity_recovers_known_slope():
    rng = np.random.default_rng(0)
    index = pd.date_range("2010-01-03", periods=80, freq="W")
    price = rng.uniform(1, 3, 80)
    quantity = np.exp(5 - 1.5 * np.log(price) + rng.normal(0, 0.05, 80))
    result = elasticity(pd.DataFrame({"price": price, "quantity": quantity}, index=index))
    assert abs(result["elasticity"] + 1.5) < 0.1 and result["ci_low"] < -1.5 < result["ci_high"]
