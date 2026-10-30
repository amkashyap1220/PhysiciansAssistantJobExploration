"""PA rows (SOC 29-1071) from the BLS OEWS files in data/raw/.

Each zip holds one spreadsheet (two for some older years). Column names
changed case over the years, so they're lowercased here. BLS marks values it
can't publish with "*", "**" or "#" (a wage above the top of its scale);
those become missing.
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
PA = "29-1071"
NUM = ["tot_emp", "emp_prse", "jobs_1000", "loc_quotient", "pct_total", "h_mean", "a_mean", "mean_prse",
       "a_pct10", "a_pct25", "a_median", "a_pct75", "a_pct90"]


def read(name, occ=(PA,)):
    """Every row for the given occupation codes from one OEWS zip, as a DataFrame."""
    frames = []
    with zipfile.ZipFile(RAW / name) as z:
        for member in z.namelist():
            if not member.lower().endswith((".xlsx", ".xls")) or "field_desc" in member.lower():
                continue
            df = pd.read_excel(io.BytesIO(z.read(member)), dtype=str)
            df.columns = [c.strip().lower() for c in df.columns]
            if "occ_code" not in df.columns:
                continue
            frames.append(df[df["occ_code"].isin(occ)])
    df = pd.concat(frames, ignore_index=True)
    for c in NUM:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].str.replace(",", "", regex=False), errors="coerce")
    # 2015 called the state code "st" and the area name "area_name"
    df = df.rename(columns={"st": "prim_state", "area_name": "area_title", "state": "state_name"})
    return df
