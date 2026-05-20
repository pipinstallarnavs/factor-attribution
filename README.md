![Factor Attribution banner](assets/banner.svg)

# Factor Attribution

A rolling factor exposure and performance-attribution study using the Fama-French five-factor model plus momentum.

## Method

The pipeline downloads and hashes the official Ken French factor archives, aligns them with a portfolio return series, and estimates rolling regressions. It then:

- Reports time-varying factor exposures
- Reconciles attributed and realized returns
- Measures unexplained residual return
- Tests exposure stability on a later holdout period

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
python -m unittest -v
```

Downloaded archives and generated reports remain outside version control.

## Interpretation

Regression attribution explains covariance with observed factors. It does not establish causality, and a positive residual should not automatically be described as skill or alpha.
