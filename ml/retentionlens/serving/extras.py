"""Extra serving builders added by later phases (segments, signals, product lab).

Each builder takes (prepared, scored, out_dir), may write its own JSON files, and returns
either None or a DataFrame of extra per-account columns indexed by customer_id.
"""
EXTRA_BUILDERS: list = []
