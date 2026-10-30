# PA Job Market

What the physician assistant (PA) job market looks like for new grads: which specialties hire new PAs, what they pay, where PAs are, how long the job search takes, and how much debt new PAs start with.

**See the charts:** [alexanderk.dev/research/pa-job-market](https://alexanderk.dev/research/pa-job-market)

## Findings

- **New grads find jobs fast.** PAs certified in 2024 typically accepted a job about 2 months after starting to look, and 78% had two or more offers.
- **First-job pay is about $115k** (median, 2024), up from $95k in 2020. 62% of first jobs pay $100k to $130k.
- **Specialty matters as much as experience.** Average income runs from $108k in general pediatrics to $155k in cardiothoracic and vascular surgery. Twenty years of experience adds about $28k.
- **Dermatology is crowded.** 9.2% of new grads still looking want dermatology, but only 3.9% of those who took a job got one there. Emergency, family and hospital medicine hire the most new PAs.
- **Debt is large.** The median new PA owes $137,500 for school.

## Data

Everything comes from the [NCCPA](https://www.nccpa.net/), which certifies every PA in the US and surveys them each year:

| Report | Used for |
| --- | --- |
| [2025 Statistical Profile of Board Certified PAs](https://doi.org/10.64936/SR0513) | PAs by state and specialty, settings, pay by experience, satisfaction and burnout |
| [2024 Statistical Profile of Recently Board Certified PAs](https://doi.org/10.64936/MARE1040) | New grads: where they took jobs, first-job salaries, job search, debt, new PAs by state |
| [2024 Statistical Profile of Board Certified PAs by Specialty](https://www.nccpa.net/wp-content/uploads/2025/08/2024-Statistical-Profile-of-Board-Certified-PAs-by-Specialty.pdf) | Pay and hours by specialty |
| [2023 Statistical Profile of Board Certified PAs by State](https://www.nccpa.net/wp-content/uploads/2025/02/2023-NCCPA-Statistical-Profile-of-Board-Certified-PAs-by-State.pdf) | Pay by state |

NCCPA publishes these as PDFs, so the tables used here were copied into `data/manual/` (one CSV or JSON file per table, named after its report). State and total rows were checked against the totals printed in each report.

## How it works

| Where | What |
| --- | --- |
| `data/manual/` | The NCCPA tables, as CSV and JSON |
| `src/site_data.py` | Joins them into `site/pa-job-market.json`, the file the website's charts read |
| `src/states.py` | State names, codes and FIPS codes (the map's shape ids) |
| `src/sources.py`, `src/download.py`, `src/oews.py` | Next step, not used yet: downloading BLS wage data by state and metro area (OEWS), BLS job projections and BEA cost of living, to add pay adjusted for local prices and metro areas |

To rebuild the site data:

```sh
pip install -r requirements.txt
python src/site_data.py
```

Then copy `site/pa-job-market.json` to `public/research/` in the [alexanderk.dev](https://github.com/amkashyap1220/alexanderk.dev) repo.

## Limits

- Pay is what PAs report earning from all their PA jobs in a year, so it includes bonuses and second jobs. It isn't adjusted for the cost of living yet.
- State figures use where PAs live, which is usually but not always where they work.
- NCCPA reports pay for 24 specialties; smaller ones aren't broken out.
- The new-grad survey covers PAs certified in 2024; 69% of them answered.
