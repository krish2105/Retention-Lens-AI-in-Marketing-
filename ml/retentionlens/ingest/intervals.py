"""Value intervals for an uploaded dataset, calibrated on its own last 90 days."""
from __future__ import annotations

import pandas as pd

from ..features.seasonal import season_multiplier
from ..features.snapshot import build_snapshot
from ..models.btyd import BtydModel
from ..models.conformal import coverage, interval, residual_quantiles
from ..serving.scoring import net_adjusted

ALPHA = 0.2  # 80% intervals


def add_value_intervals(prepared: pd.DataFrame, scored: pd.DataFrame, cutoff: str) -> tuple[pd.DataFrame, dict]:
    """Fit on history up to cutoff-90d, measure residuals on the 90 days that followed, apply to today's scores."""
    calibration_cutoff = (pd.Timestamp(cutoff) - pd.Timedelta(days=90)).date().isoformat()
    empty = pd.DataFrame(index=scored.index, columns=["value_low_90", "value_high_90"], dtype=float)
    try:
        snap = net_adjusted(build_snapshot(prepared, calibration_cutoff))
        model = BtydModel().fit(snap)
        # Same seasonal adjustment as the served scores, so residuals match what is shown.
        predicted = model.predict_value(snap) * season_multiplier(prepared, calibration_cutoff)["multiplier"]
        quantiles = residual_quantiles(snap["future_value"], predicted, ALPHA)
    except (ValueError, KeyError, RuntimeError) as error:
        return empty, {"available": False, "reason": f"Not enough history before {calibration_cutoff} to calibrate ({error})"}
    low, high = interval(scored["expected_value_90"], quantiles)
    frame = pd.DataFrame({"value_low_90": low, "value_high_90": high}, index=scored.index)
    cal_low, cal_high = interval(predicted, quantiles)
    meta = {
        "available": True,
        "level": 1 - ALPHA,
        "calibration_cutoff": calibration_cutoff,
        "calibration_customers": int(len(snap)),
        "calibration_coverage": round(coverage(snap["future_value"], cal_low, cal_high), 3),
        "method": "split conformal on log1p residuals, calibrated on the previous 90 days",
    }
    return frame, meta
