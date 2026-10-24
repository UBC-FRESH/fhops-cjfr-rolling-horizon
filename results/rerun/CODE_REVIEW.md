# Code check against the raw run files

Methods states that the authors "reviewed the code, checked its outputs against the raw run files,
and take responsibility for the results". This records the check behind that sentence.

## What was checked

For all **234 runs** in the paper set, four window-level fields produced by `scripts/analyze_rerun.py`
(`windows`, `windows_no_solution`, `windows_empty`, `windows_skipped`) were compared with the
corresponding `plan_summary` values in the run's JSON in `UBC-FRESH/jaffray-masc-fhops-model`.

## Result

936 field comparisons. One apparent mismatch, explained:

- `ni_40_baseline_mip`: `windows_empty` = 0 in `runs_metrics.csv` versus 1 in the grid run's JSON.
  The paper set **replaces the 1,800 s MIP baselines with the 7,200 s sensitivity runs**
  (`--baseline-dir`), so the analysis row is the 7,200 s run, whose `empty_windows` is 0. Comparing
  against the 7,200 s JSON matches.

Everything else matched exactly, including every MIP window-failure count, which is what the paper
quotes.

## Reproduce

```bash
cd fhops-cjfr-rolling-horizon

python - <<'PY'
import json
from pathlib import Path
import pandas as pd

exp = Path("../jaffray-masc-fhops-model/data/output")
df = pd.read_csv("results/rerun/runs_metrics.csv")
for row in df.itertuples(index=False):
    d = exp / ("rerun_v101_gurobi/runs" if row.run_id.endswith("_sa")
               else "rerun_v101_gurobi_alone/runs")
    j = json.loads((d / f"{row.run_id}.json").read_text())["plan_summary"]
    assert row.windows == len(j["iterations"])
    assert row.windows_no_solution == j.get("no_solution_windows")
    assert row.windows_empty == j.get("empty_windows")
    assert row.windows_skipped == j.get("skipped_windows")
PY
```

The assertion fails only for the superseded 1,800 s baseline described above. Replace that run's
path with `rerun_v101_gurobi_sensitivity_ni40_baseline_7200s/runs/` and it passes.

Checked 2026-10-24.
