import pytest

from retentionlens.eval.experiment import evaluation_cutoffs, training_cutoffs


def test_training_cutoffs_are_strictly_earlier():
    assert training_cutoffs("2011-03-01") == ["2010-09-01", "2010-12-01"]
    assert training_cutoffs("2010-12-01") == ["2010-09-01"]


def test_label_window_crossing_eval_cutoff_is_rejected():
    with pytest.raises(ValueError):
        training_cutoffs("2010-12-01", horizon_days=120)


def test_frozen_test_only_on_request():
    assert "2011-09-01" not in evaluation_cutoffs(include_test=False)
    assert evaluation_cutoffs(include_test=True)[-1] == "2011-09-01"
    assert len(evaluation_cutoffs(include_test=True)) == 4
