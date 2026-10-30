"""Build the data file the website's charts read: site/pa-job-market.json.

Inputs are the tables in data/manual/ (copied by hand from NCCPA's yearly
reports, listed in README.md) and data/bls/ (cut from the BLS, BEA and Census
downloads by src/extract_bls.py). Copy the output to public/research/ in the
alexanderk.dev repo.
"""
import json
from pathlib import Path

import pandas as pd

from states import STATES

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "data" / "manual"
BLS = ROOT / "data" / "bls"
OUT = ROOT / "site" / "pa-job-market.json"


def csv(name):
    # Only empty cells are missing: "None" is a debt range, not a blank
    return pd.read_csv(MANUAL / name, keep_default_na=False, na_values=[""])


def bls(name):
    return pd.read_csv(BLS / name, dtype={"area": str, "naics": str, "GeoFIPS": str, "GEOID": str})


def prices(name):
    """BEA's 2024 price level by area code, where 100 is the US average."""
    return bls(name).set_index("GeoFIPS")["2024"]


def adjusted(pay, rpp):
    """Pay at US-average prices: $130k where prices are 10% below average goes as far as about $144k."""
    return (pay / rpp * 100).round(-2).astype(int)


def records(df):
    return json.loads(df.to_json(orient="records"))


def states():
    df = pd.DataFrame(STATES, columns=["name", "abbr", "fips"])
    workforce = csv("nccpa_2025_states.csv").rename(columns={"state": "name", "growth_2021_2025": "growth"})
    new = csv("nccpa_recent_2024_states.csv").rename(columns={"state": "name", "new_pas_2024": "new_pas"})
    # BLS counts jobs and pay where PAs work; NCCPA counts PAs where they live
    oews = bls("oews_states_2025.csv").rename(columns={"prim_state": "abbr", "tot_emp": "jobs", "a_median": "pay"})
    df = df.merge(workforce, on="name", how="left").merge(new[["name", "new_pas"]], on="name", how="left").merge(oews[["abbr", "jobs", "pay"]], on="abbr", how="left")
    df["rpp"] = (df["fips"] + "000").map(prices("rpp_states.csv"))
    assert df[["pas", "new_pas", "pay", "rpp"]].notna().all().all(), "a state is missing from a table"
    df["pay_adj"] = adjusted(df["pay"], df["rpp"])
    # New PAs certified in 2024 for every 100 PAs already there: higher means more new grads competing for each opening
    df["new_per_100"] = (df["new_pas"] / df["pas"] * 100).round(1)
    return df


def specialties():
    """Where all PAs work (2025), where new grads took jobs (2024) and where the ones still looking want to work."""
    allp = csv("nccpa_2025_specialty.csv")
    new = csv("nccpa_recent_2024_practice_area.csv")
    key = lambda s: s.split(" (")[0].strip()
    allp["key"] = allp["area"].map(key)
    new["key"] = new["area"].map(key)
    df = allp.merge(new, on="key", how="left")
    df = df[df["key"] != "Other"]
    return [{"label": r.key, "all": r.pct, "new": r.pct_accepted, "want": r.pct_preferred_not_accepted} for r in df.itertuples()]


def short(title):
    """"Dallas-Fort Worth-Arlington, TX" -> "Dallas, TX", for chart labels."""
    cities, states = title.split(", ", 1)
    # Cities are joined by "-", or by "--" when one has a hyphen in its name; Winston-Salem is one city
    city = cities if cities == "Winston-Salem" else cities.split("--" if "--" in cities else "-")[0]
    return city + ", " + states.split("-")[0]


def metros():
    """Metro areas in the 50 states and DC with BLS pay, a price level and a point for the map."""
    df = bls("oews_metros_2025.csv")
    df = df[(df["area_type"] == 4) & df["prim_state"].isin([a for _, a, _ in STATES])].dropna(subset=["tot_emp", "a_median"])
    df["rpp"] = df["area"].map(prices("rpp_metros.csv"))
    points = bls("cbsa_points.csv").set_index("GEOID")
    df["lat"], df["lon"] = df["area"].map(points["INTPTLAT"]).round(2), df["area"].map(points["INTPTLONG"]).round(2)
    assert df[["rpp", "lat"]].notna().all().all(), "a metro area is missing a price level or a point"
    df["short"] = df["area_title"].map(short)
    df["pay_adj"] = adjusted(df["a_median"], df["rpp"])
    out = df.rename(columns={"area": "cbsa", "area_title": "name", "tot_emp": "jobs", "a_median": "pay"}).astype({"jobs": int, "pay": int})
    return out[["cbsa", "name", "short", "jobs", "pay", "rpp", "pay_adj", "lat", "lon"]].sort_values("jobs", ascending=False)


# The types of employer that have at least 1,000 PA jobs (4-digit NAICS), in plain words
EMPLOYERS = {
    "621100": "Doctors' offices", "622100": "General hospitals", "621400": "Outpatient care centers",
    "611300": "Colleges and universities", "999100": "Federal government", "621300": "Other practitioners' offices",
    "561300": "Staffing agencies", "622300": "Specialty hospitals",
}


def employers(total):
    df = bls("oews_industries_2025.csv")
    # The file lists each industry for all owners first, then again for private and public owners
    df = df[df["naics"].isin(EMPLOYERS)].drop_duplicates("naics")
    assert len(df) == len(EMPLOYERS) and (df["tot_emp"] >= 1000).all()
    return [{"label": EMPLOYERS[r.naics], "jobs": int(r.tot_emp), "share": round(r.tot_emp / total * 100, 1), "pay": int(r.a_median)}
            for r in df.itertuples()]


# Occupations to compare PAs' job growth with, by SOC code
COMPARE = {"29-1071": "PAs", "29-1171": "Nurse practitioners", "29-1141": "Registered nurses", "29-1210": "Physicians", "00-0000": "All jobs"}


def projections():
    """BLS Employment Projections table 1.2: jobs in thousands in 2025 and 2035, growth and openings a year."""
    df = bls("ep_projections.csv")
    # Columns as published: title, SOC code, row type, jobs 2025, jobs 2035, two shares, change, % change, % self-employed, openings
    df = df[(df["sheet"] == "Table 1.2") & df["1"].isin(COMPARE)]
    return [{"label": COMPARE[r["1"]], "jobs_2025": float(r["3"]) * 1000, "jobs_2035": float(r["4"]) * 1000,
             "growth": float(r["8"]), "openings": float(r["10"]) * 1000} for _, r in df.iterrows()]


def build():
    recent = json.loads((MANUAL / "nccpa_recent_2024_facts.json").read_text())
    profile = json.loads((MANUAL / "nccpa_2025_facts.json").read_text())
    pay = csv("nccpa_2024_specialty_pay.csv")
    pay_facts = json.loads((MANUAL / "nccpa_2024_specialty_facts.json").read_text())
    st = states()
    nat = bls("oews_national_history.csv").set_index("year").loc[2025]
    proj = projections()
    pa = next(p for p in proj if p["label"] == "PAs")
    data = {
        "sources": [
            {"name": "NCCPA, 2025 Statistical Profile of Board Certified PAs", "year": 2025, "url": "https://doi.org/10.64936/SR0513"},
            {"name": "NCCPA, 2024 Statistical Profile of Recently Board Certified PAs", "year": 2024, "url": "https://doi.org/10.64936/MARE1040"},
            {"name": "NCCPA, 2024 Statistical Profile of Board Certified PAs by Specialty", "year": 2024,
             "url": "https://www.nccpa.net/wp-content/uploads/2025/08/2024-Statistical-Profile-of-Board-Certified-PAs-by-Specialty.pdf"},
            {"name": "BLS, Occupational Employment and Wage Statistics, May 2025", "year": 2025, "url": "https://www.bls.gov/oes/current/oes291071.htm"},
            {"name": "BLS, Employment Projections 2025-35", "year": 2025, "url": "https://www.bls.gov/emp/"},
            {"name": "BEA, Regional Price Parities, 2024", "year": 2024, "url": "https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area"},
            {"name": "Census Bureau, 2024 Gazetteer of metro areas", "year": 2024, "url": "https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html"},
        ],
        "headline": {
            "pas": profile["certified_pas"], "pas_2013": profile["certified_pas_2013"], "growth_4yr": profile["growth_2021_2025"],
            "median_pay": profile["salary_median"], "new_median_pay": recent["salary_median"], "new_median_pay_2020": recent["salary_median_2020"],
            "months_to_job": recent["months_to_job_median"], "two_plus_offers": recent["two_plus_offers"],
            "mean_pay_all_2024": pay_facts["mean_income_all"],
            "debt_median": recent["debt_median"], "new_certified": recent["certified_2024"], "respondents": recent["respondents"],
            "bls_jobs": int(nat["tot_emp"]), "bls_median_pay": int(nat["a_median"]),
            "growth_2035": pa["growth"], "jobs_2035": pa["jobs_2035"], "openings": pa["openings"],
        },
        "states": records(st[["fips", "abbr", "name", "pas", "per_100k", "growth", "new_pas", "new_per_100", "jobs", "pay", "rpp", "pay_adj"]]),
        "metros": records(metros()),
        "employers": employers(nat["tot_emp"]),
        "projections": proj,
        "specialties": specialties(),
        "specialty_pay": records(pay.rename(columns={"specialty": "label"})),
        "settings": records(csv("nccpa_2025_setting.csv").merge(
            csv("nccpa_recent_2024_setting.csv").rename(columns={"setting": "setting"}), on="setting", how="left")),
        "experience_pay": records(csv("nccpa_2025_pay_by_experience.csv")),
        "new_salary": records(csv("nccpa_recent_2024_salary.csv")),
        "new_debt": records(csv("nccpa_recent_2024_debt.csv")),
        "new_challenges": records(csv("nccpa_recent_2024_challenges.csv")),
        "recent": recent,
        "profile": profile,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size / 1000:.0f} kB)")


if __name__ == "__main__":
    build()
