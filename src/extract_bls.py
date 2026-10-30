"""Cut the downloaded BLS, BEA and Census files (data/raw/) down to the
small tables this project uses, in data/bls/. Those are committed, so the
site data can be rebuilt without downloading again.

Run after src/download.py.
"""
import io
import zipfile
from pathlib import Path

import pandas as pd

from oews import PA, RAW, read
from sources import YEAR

OUT = Path(__file__).resolve().parent.parent / "data" / "bls"
KEEP = ["area", "area_title", "area_type", "prim_state", "naics", "naics_title", "tot_emp", "jobs_1000", "loc_quotient",
        "a_mean", "a_pct10", "a_pct25", "a_median", "a_pct75", "a_pct90"]
# For comparison in the projections: nurse practitioners, physicians and surgeons (all), registered nurses, all occupations
COMPARE = [PA, "29-1171", "29-1210", "29-1141", "00-0000"]


def cols(df):
    return df[[c for c in KEEP if c in df.columns]]


def oews():
    year = 2000 + YEAR
    cols(read(f"oesm{YEAR}st.zip")).to_csv(OUT / f"oews_states_{year}.csv", index=False)
    cols(read(f"oesm{YEAR}ma.zip")).to_csv(OUT / f"oews_metros_{year}.csv", index=False)
    cols(read(f"oesm{YEAR}in4.zip")).to_csv(OUT / f"oews_industries_{year}.csv", index=False)
    cols(read("oesm15st.zip")).to_csv(OUT / "oews_states_2015.csv", index=False)
    rows = []
    for y in range(15, YEAR + 1):
        df = read(f"oesm{y:02d}nat.zip")
        # National files list the occupation once for all industries (and, in some years, again by ownership)
        if "naics" in df.columns:
            df = df[df["naics"].isin(["000000", "0"]) | df["naics"].isna()]
        r = df.iloc[0]
        rows.append({"year": 2000 + y, "tot_emp": r["tot_emp"], "a_mean": r.get("a_mean"), "a_median": r.get("a_median")})
    pd.DataFrame(rows).to_csv(OUT / "oews_national_history.csv", index=False)


def projections():
    """Every sheet's rows for PAs and the comparison occupations, as published."""
    sheets = pd.read_excel(RAW / "ep-occupation.xlsx", sheet_name=None, header=None, dtype=str)
    out = []
    for name, df in sheets.items():
        hit = df.apply(lambda r: r.astype(str).str.strip().isin(COMPARE).any(), axis=1)
        if hit.any():
            block = df[hit].copy()
            block.insert(0, "sheet", name)
            out.append(block)
            # The header is the last row above the first match that has text in most columns
            above = df.loc[: hit.idxmax() - 1].dropna(thresh=max(2, df.shape[1] // 2))
            print(f"{name}: {hit.sum()} rows; header: {list(above.iloc[-1]) if len(above) else None}")
    pd.concat(out).to_csv(OUT / "ep_projections.csv", index=False)


def rpp():
    """BEA Regional Price Parities, all items (line 1): 100 = the US average price level."""
    for name, out in [("SARPP.zip", "rpp_states.csv"), ("MARPP.zip", "rpp_metros.csv")]:
        with zipfile.ZipFile(RAW / name) as z:
            # The zip also holds other tables (price deflators, real income): take the one it's named for
            member = next(m for m in z.namelist() if m.startswith(name[:-4] + "_") and m.lower().endswith(".csv"))
            df = pd.read_csv(io.BytesIO(z.read(member)), dtype=str, encoding="latin-1")
        df.columns = [c.strip() for c in df.columns]
        df = df[df["LineCode"].str.strip() == "1"]
        df["GeoFIPS"] = df["GeoFIPS"].str.strip().str.strip('"')
        years = [c for c in df.columns if c.isdigit()]
        df[["GeoFIPS", "GeoName"] + years].to_csv(OUT / out, index=False)
        print(f"{out}: {len(df)} areas, years {years[0]}-{years[-1]}")


def gazetteer():
    """A point inside each metro area (Census), to place it on the map."""
    with zipfile.ZipFile(RAW / "gaz-cbsa.zip") as z:
        member = next(m for m in z.namelist() if m.endswith(".txt"))
        df = pd.read_csv(io.BytesIO(z.read(member)), sep="\t", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df.apply(lambda s: s.str.strip())
    df[["GEOID", "NAME", "INTPTLAT", "INTPTLONG"]].to_csv(OUT / "cbsa_points.csv", index=False)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for step in (oews, projections, rpp, gazetteer):
        step()
    for f in sorted(OUT.iterdir()):
        print(f"{f.name:32} {f.stat().st_size / 1000:.0f} kB")
