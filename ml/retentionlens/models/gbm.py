"""LightGBM challenger: lapse classifier plus a spend regressor for buyers."""
from __future__ import annotations

import numpy as np
import pandas as pd
from lightgbm import LGBMClassifier, LGBMRegressor

from ..features.snapshot import FEATURES

# Fixed before any result was seen; not tuned on dev or test cutoffs.
PARAMS = dict(
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=15,
    min_child_samples=40,
    subsample=0.8,
    subsample_freq=1,
    colsample_bytree=0.8,
    verbose=-1,
)


def _matrix(snap: pd.DataFrame) -> pd.DataFrame:
    return snap[FEATURES].astype(float)


class GbmModel:
    name = "lightgbm"

    def fit(self, train: pd.DataFrame, seed: int = 0) -> "GbmModel":
        self.classifier = LGBMClassifier(random_state=seed, deterministic=True, **PARAMS)
        self.classifier.fit(_matrix(train), train["lapsed"])
        buyers = train[train["future_value"] > 0]
        self.regressor = LGBMRegressor(random_state=seed, deterministic=True, **PARAMS)
        self.regressor.fit(_matrix(buyers), np.log1p(buyers["future_value"]))
        return self

    def predict_lapse(self, snap: pd.DataFrame) -> np.ndarray:
        return self.classifier.predict_proba(_matrix(snap))[:, 1]

    def predict_value(self, snap: pd.DataFrame, horizon_days: int = 90) -> np.ndarray:
        spend_if_buying = np.expm1(self.regressor.predict(_matrix(snap)))
        return np.clip((1 - self.predict_lapse(snap)) * spend_if_buying, 0, None)
