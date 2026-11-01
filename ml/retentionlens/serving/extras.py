"""Extra serving builders added by later phases (segments, signals, product lab).

Each builder takes (prepared, scored, out_dir), may write its own JSON files, and returns
either None or a DataFrame of extra per-account columns indexed by customer_id.
"""
from ..product.lab import build_product_lab
from ..signals.build import build_signals
from .products import build_account_products
from .segments import build_segments

EXTRA_BUILDERS: list = [build_segments, build_signals, build_account_products, build_product_lab]
