# Data

Downloads are kept out of the repository; `src/download.py` fetches them again.

| File | Source | Size |
|---|---|---|
| data/raw/fishbase/gillarea.parquet | FishBase v25.04, rOpenSci mirror: `https://huggingface.co/datasets/cboettig/fishbase/resolve/main/data/fb/v25.04/parquet/gillarea.parquet` | 12 kB |
| data/raw/fishbase/oxygen.parquet | same mirror, `oxygen.parquet` | 174 kB |
| data/raw/fishbase/species.parquet | same mirror, `species.parquet` | 5.1 MB |
| data/raw/fishbase/families.parquet | same mirror, `families.parquet` | 417 kB |

FishBase units as used here: GILLAREA gives total gill area in cm² against body weight in g (rows flagged doubtful are dropped); OXYGEN gives uptake in mg O₂ per kg per hour, with metabolic level and any applied stress.

Kept in the repository:

- `data/labels/excess.csv`: every animal temperature on the figures, with tissue, source, the assumed blood oxygen capacity range for its group, and whether the excess is a steady state.

Rebuilt by `src/run_all.py` (ignored): `data/derived/` (FishBase gill records and every oxygen-flux match).

Papers read while compiling `excess.csv` are cited there and in the README, and are not redistributed.
