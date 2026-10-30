"""Build the data file the website's charts read: site/pa-job-market.json.

Inputs are the tables in data/manual/ (copied by hand from NCCPA's yearly
reports, see docs/sources.md). Copy the output to public/research/ in the
alexanderk.dev repo.
"""
import json
from pathlib import Path

import pandas as pd

from states import STATES

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ROOT / "data" / "manual"
OUT = ROOT / "site" / "pa-job-market.json"


def csv(name):
    # Only empty cells are missing: "None" is a debt range, not a blank
    return pd.read_csv(MANUAL / name, keep_default_na=False, na_values=[""])


def records(df):
    return json.loads(df.to_json(orient="records"))


def states():
    df = pd.DataFrame(STATES, columns=["name", "abbr", "fips"])
    workforce = csv("nccpa_2025_states.csv").rename(columns={"state": "name", "growth_2021_2025": "growth"})
    income = csv("nccpa_2023_state_income.csv").rename(columns={"state": "name", "mean_2023": "pay", "median_2023": "pay_median"})
    new = csv("nccpa_recent_2024_states.csv").rename(columns={"state": "name", "new_pas_2024": "new_pas"})
    df = df.merge(workforce, on="name", how="left").merge(income, on="name", how="left").merge(new[["name", "new_pas"]], on="name", how="left")
    assert df[["pas", "pay", "new_pas"]].notna().all().all(), "a state is missing from a table"
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


def build():
    recent = json.loads((MANUAL / "nccpa_recent_2024_facts.json").read_text())
    profile = json.loads((MANUAL / "nccpa_2025_facts.json").read_text())
    pay = csv("nccpa_2024_specialty_pay.csv")
    pay_facts = json.loads((MANUAL / "nccpa_2024_specialty_facts.json").read_text())
    st = states()
    data = {
        "sources": [
            {"name": "NCCPA, 2025 Statistical Profile of Board Certified PAs", "year": 2025, "url": "https://doi.org/10.64936/SR0513"},
            {"name": "NCCPA, 2024 Statistical Profile of Recently Board Certified PAs", "year": 2024, "url": "https://doi.org/10.64936/MARE1040"},
            {"name": "NCCPA, 2024 Statistical Profile of Board Certified PAs by Specialty", "year": 2024,
             "url": "https://www.nccpa.net/wp-content/uploads/2025/08/2024-Statistical-Profile-of-Board-Certified-PAs-by-Specialty.pdf"},
            {"name": "NCCPA, 2023 Statistical Profile of Board Certified PAs by State", "year": 2023,
             "url": "https://www.nccpa.net/wp-content/uploads/2025/02/2023-NCCPA-Statistical-Profile-of-Board-Certified-PAs-by-State.pdf"},
        ],
        "headline": {
            "pas": profile["certified_pas"], "pas_2013": profile["certified_pas_2013"], "growth_4yr": profile["growth_2021_2025"],
            "median_pay": profile["salary_median"], "new_median_pay": recent["salary_median"], "new_median_pay_2020": recent["salary_median_2020"],
            "months_to_job": recent["months_to_job_median"], "two_plus_offers": recent["two_plus_offers"],
            "mean_pay_all_2024": pay_facts["mean_income_all"],
            "debt_median": recent["debt_median"], "new_certified": recent["certified_2024"], "respondents": recent["respondents"],
        },
        "states": records(st[["fips", "abbr", "name", "pas", "per_100k", "growth", "pay", "pay_median", "new_pas", "new_per_100"]]),
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
