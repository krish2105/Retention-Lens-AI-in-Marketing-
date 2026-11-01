import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("calibrate", Path(__file__).resolve().parents[1] / "evals" / "calibrate_critic.py")
calibrate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(calibrate)


def test_kappa_perfect_and_chance():
    assert calibrate.cohen_kappa(["pass", "revise"] * 5, ["pass", "revise"] * 5) == 1.0
    assert abs(calibrate.cohen_kappa(["pass", "pass", "revise", "revise"], ["pass", "revise", "pass", "revise"])) < 1e-9
