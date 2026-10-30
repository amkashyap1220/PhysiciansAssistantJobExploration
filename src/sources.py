"""Every public file the analysis reads, with where it comes from.

`python src/download.py` fetches them into data/raw/. Nothing in data/raw/ is
committed; the tables built from it are, in data/processed/.
"""

OEWS = "https://www.bls.gov/oes/special-requests"

# Occupational Employment and Wage Statistics (BLS), May of each year.
# PAs are SOC 29-1071. May 2025 is the newest release (published spring 2026).
YEAR = 25
FILES = {
    # National, state, metro and nonmetro, and national by industry (4-digit NAICS)
    f"oesm{YEAR}nat.zip": f"{OEWS}/oesm{YEAR}nat.zip",
    f"oesm{YEAR}st.zip": f"{OEWS}/oesm{YEAR}st.zip",
    f"oesm{YEAR}ma.zip": f"{OEWS}/oesm{YEAR}ma.zip",
    f"oesm{YEAR}in4.zip": f"{OEWS}/oesm{YEAR}in4.zip",
    # Ten years back, for growth by state
    "oesm15st.zip": f"{OEWS}/oesm15st.zip",
    # BLS Employment Projections, 2024 to 2034, every occupation
    "ep-occupation.xlsx": "https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx",
    # BEA Regional Price Parities: how far a dollar goes in each state and metro
    "SARPP.zip": "https://apps.bea.gov/regional/zip/SARPP.zip",
    "MARPP.zip": "https://apps.bea.gov/regional/zip/MARPP.zip",
    # Census gazetteer: a point for each metro area, to place it on the map
    "gaz-cbsa.zip": "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_cbsa_national.zip",
    # NCCPA reports (the body that certifies PAs): specialties, settings and pay
    "nccpa-recent-2024.pdf": "https://www.nccpa.net/wp-content/uploads/2025/10/2024-Statistical-Profile-of-Recently-Board-Certified-PAs.pdf",
    "nccpa-specialty-2024.pdf": "https://www.nccpa.net/wp-content/uploads/2025/08/2024-Statistical-Profile-of-Board-Certified-PAs-by-Specialty.pdf",
    "nccpa-profile-2025.pdf": "https://www.nccpa.net/wp-content/uploads/reports/2025-Statistical-Profile-of-Board-Certified-PAs.pdf",
}

# National history of PA jobs and pay, one file per year
for y in range(15, YEAR):
    FILES[f"oesm{y:02d}nat.zip"] = f"{OEWS}/oesm{y:02d}nat.zip"
