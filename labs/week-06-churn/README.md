# Lab: Retaining customers: churn analysis

**Aim:** Compare lapse models on rolling cutoffs with a frozen test; discuss calibration.

This is a scaffold. The analysis and the written report must be your own work; the commands and files below give you reproducible evidence to cite.

## Reproduce

```bash
cd ml
uv run python -m retentionlens.cli models --include-test
```

- Model lab → Lapse table and calibration chart

## Evidence to cite

- `reports/model_results.md`
- `ml/retentionlens/eval/experiment.py`

## Report structure (rubric headings, section 3.3 of the unit outline)

1. **Implementation**: what you ran and why (models, settings, data version and checksum).
2. **Experimentation**: what you compared, on which cutoffs, and the measured results.
3. **Problem-solving**: issues found in the data or models and how you handled them.
4. **Reporting**: charts with source footers, limitations, and what a marketer should do differently.

_Write your analysis here._
