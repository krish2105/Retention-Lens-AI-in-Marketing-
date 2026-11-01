import numpy as np
import pandas as pd
import pytest

from retentionlens.features.snapshot import FEATURES
from retentionlens.models.baselines import LogisticRFM, NaiveValueModel, RecencyBucketModel
from retentionlens.models.gbm import GbmModel


def synthetic(n=600, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({f: rng.gamma(2.0, 10.0, n) for f in FEATURES})
    df["recency_days"] = rng.integers(1, 300, n)
    df["is_uk"] = rng.random(n) > 0.2
    p = 1 / (1 + np.exp(-(df["recency_days"] - 120) / 40))
    df["lapsed"] = (rng.random(n) < p).astype(int)
    df["future_value"] = np.where(df["lapsed"] == 1, 0.0, rng.gamma(2.0, 50.0, n))
    df.index = pd.Index([f"c{i}" for i in range(n)], name="customer_id")
    return df


@pytest.mark.parametrize("model", [RecencyBucketModel(), LogisticRFM(), GbmModel()])
def test_lapse_models_return_probabilities_and_learn_recency(model):
    train, test = synthetic(seed=1), synthetic(seed=2)
    p = model.fit(train, seed=7).predict_lapse(test)
    assert p.shape == (len(test),) and np.all((p >= 0) & (p <= 1))
    assert np.corrcoef(p, test["recency_days"])[0, 1] > 0.5


def test_value_models_non_negative():
    train, test = synthetic(seed=1), synthetic(seed=2)
    for model in (NaiveValueModel(), GbmModel()):
        v = model.fit(train, seed=7).predict_value(test, horizon_days=90)
        assert v.shape == (len(test),) and np.all(v >= 0)


def test_gbm_is_deterministic_for_a_seed():
    train, test = synthetic(seed=1), synthetic(seed=2)
    a = GbmModel().fit(train, seed=7).predict_lapse(test)
    b = GbmModel().fit(train, seed=7).predict_lapse(test)
    np.testing.assert_allclose(a, b)
