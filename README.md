# PA Job Market

What the physician assistant (PA) job market looks like for new grads: which specialties hire new PAs, what they pay, where PAs are, where pay goes furthest after the cost of living, how fast PA jobs are growing, how long the job search takes, and how much debt new PAs start with.

**See the charts:** [alexanderk.dev/research/pa-job-market](https://alexanderk.dev/research/pa-job-market)

## Findings

- **New grads find jobs fast.** PAs certified in 2024 typically accepted a job about 2 months after starting to look, and 78% had two or more offers.
- **First-job pay is about $115k** (median, 2024), up from $95k in 2020. 62% of first jobs pay $100k to $130k.
- **Specialty matters as much as experience.** Average income runs from $108k in general pediatrics to $155k in cardiothoracic and vascular surgery. Twenty years of experience adds about $28k.
- **Dermatology is crowded.** 9.2% of new grads still looking want dermatology, but only 3.9% of those who took a job got one there. Emergency, family and hospital medicine hire the most new PAs.
- **Debt is large.** The median new PA owes $137,500 for school.
- **PA jobs are growing fast.** BLS expects 21% growth from 2025 to 2035, six times the rate for all jobs, or about 11,500 openings a year.
- **Pay depends on the employer.** Doctors' offices employ 54% of PAs and pay a median of $132k; the federal government pays $165k and staffing agencies $158k (May 2025).
- **The highest pay isn't the furthest-going.** New Jersey and California pay the most (about $166k median), but after the cost of living Oklahoma comes out on top at $155k. Among the 20 biggest PA job markets, San Francisco loses the most to prices and Atlanta pays the least.

## Data

Most of it comes from the [NCCPA](https://www.nccpa.net/), which certifies every PA in the US and surveys them each year:

| Report | Used for |
| --- | --- |
| [2025 Statistical Profile of Board Certified PAs](https://doi.org/10.64936/SR0513) | PAs by state and specialty, settings, pay by experience, satisfaction and burnout |
| [2024 Statistical Profile of Recently Board Certified PAs](https://doi.org/10.64936/MARE1040) | New grads: where they took jobs, first-job salaries, job search, debt, new PAs by state |
| [2024 Statistical Profile of Board Certified PAs by Specialty](https://www.nccpa.net/wp-content/uploads/2025/08/2024-Statistical-Profile-of-Board-Certified-PAs-by-Specialty.pdf) | Pay and hours by specialty |
| [2023 Statistical Profile of Board Certified PAs by State](https://www.nccpa.net/wp-content/uploads/2025/02/2023-NCCPA-Statistical-Profile-of-Board-Certified-PAs-by-State.pdf) | Pay by state (kept in `data/manual/`, no longer charted) |

NCCPA publishes these as PDFs, so the tables used here were copied into `data/manual/` (one CSV or JSON file per table, named after its report). State and total rows were checked against the totals printed in each report.

Jobs, pay and prices come from federal data, cut down to the rows used here in `data/bls/`:

| Source | Used for |
| --- | --- |
| [BLS Occupational Employment and Wage Statistics](https://www.bls.gov/oes/current/oes291071.htm), May 2025 (PAs are SOC 29-1071) | PA jobs and median pay by state, metro area and type of employer |
| [BLS Employment Projections](https://www.bls.gov/emp/), 2025 to 2035 | Job growth and openings for PAs, nurse practitioners, registered nurses, physicians and all jobs |
| [BEA Regional Price Parities](https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area), 2024 | How expensive each state and metro area is, to adjust pay for the cost of living |
| [Census Bureau Gazetteer](https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html), 2024 | A point in each metro area, to place it on the map |

## How it works

| Where | What |
| --- | --- |
| `data/manual/` | The NCCPA tables, as CSV and JSON |
| `data/bls/` | The BLS, BEA and Census tables, as CSV |
| `src/sources.py`, `src/download.py` | Where each federal file comes from, and a script that downloads them into `data/raw/` (not committed) |
| `src/oews.py`, `src/extract_bls.py` | Cut the downloads down to the tables in `data/bls/` |
| `src/site_data.py` | Joins everything into `site/pa-job-market.json`, the file the website's charts read |
| `src/states.py` | State names, codes and FIPS codes (the map's shape ids) |

bls.gov turns away scripted downloads, so the BLS files were saved from a browser into `data/raw/` before running `python src/extract_bls.py`. The tables it writes are committed, so rebuilding the site data needs no downloads.

To rebuild the site data:

```sh
pip install -r requirements.txt
python src/site_data.py
```

Then copy `site/pa-job-market.json` to `public/research/` in the [alexanderk.dev](https://github.com/amkashyap1220/alexanderk.dev) repo.

## Limits

- NCCPA pay is what PAs report earning from all their PA jobs in a year, so it includes bonuses and second jobs. BLS pay is wages from a survey of employers, without benefits or most bonuses, so the two don't match.
- NCCPA state figures use where PAs live, which is usually but not always where they work. BLS figures use where they work.
- Pay after the cost of living divides median pay by the BEA price level for the area (100 = US average). It doesn't account for taxes.
- BLS doesn't publish pay for metro areas with too few PA jobs to estimate, and rural areas outside metro areas aren't on the metro map.
- NCCPA reports pay for 24 specialties; smaller ones aren't broken out.
- The new-grad survey covers PAs certified in 2024; 69% of them answered.
