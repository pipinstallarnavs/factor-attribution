# Factor exposure and performance attribution

Rolling Fama-French five-factor plus momentum regressions on a real portfolio
series. Return attribution is checked against realized returns, then exposures
are tested for stability on a later holdout.

```bash
../NAS/venv/bin/python run.py
../NAS/venv/bin/python -m unittest -v
```

The official Ken French CSVs are downloaded and hashed. This project explains
returns; it does not claim factors are causal or that residual returns are alpha.
