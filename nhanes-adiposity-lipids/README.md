# NHANES adiposity and non-HDL cholesterol

This project compares waist-to-height ratio (WHtR) and BMI as correlates of non-HDL cholesterol in NHANES August 2021-August 2023. The current work covers descriptive statistics and probability. The analysis is observational and does not establish causation.

## Run the project

Use Python 3.11 or later. Run these commands from the project folder:

```bash
python -m pip install -r requirements.txt
python src/download_data.py
python src/phase1_pipeline.py
python src/phase2_probability.py
python src/build_reports.py
```

The download step reuses files already present. The scripts resolve paths relative to this project, so they can also be launched from another directory.

## Files

- `PROJECT_CARD.md`: question, population, variable definitions and limitations.
- `data/README.md`: official sources, retrieval details and data reconstruction.
- `src/data_preparation.py`: shared merges, cleaning and participant selection.
- `src/phase1_pipeline.py`: audit tables, descriptive statistics and four figures.
- `src/phase2_probability.py`: probabilities, binomial comparison, normal diagnostics and covariance.
- `src/build_reports.py`: regenerates both PDF reports and their Markdown sources from saved results.
- `tables/`: generated CSV tables, including source counts, merge audit and missingness.
- `figures/`: generated PNG figures.
- `reports/phase1.pdf` and `reports/phase2.pdf`: reports for submission.

The analytical sample contains 5,205 adults with complete core measurements after excluding known pregnancies. Unknown pregnancy status is retained and documented. Income summaries use the 4,548 available responses. All weighted results for this blood-analysis sample use `WTPH2YR`.

## Before committing and submitting

Raw XPT files and individual-level derived data are excluded from Git and the submission ZIP. Keep your existing Git history when copying these files into your repository. Inspect `git status` and `git diff` before committing. The required tags are `phase-1` and `phase-2`; do not overwrite existing tags. If both tags already exist, keep them and record corrections in a new commit. Follow the course instructions for any updated tagged submission.

Only aggregate tables are included. To rebuild the PDFs, run both analysis scripts first. The reports use ReportLab; a LaTeX installation is not required.
