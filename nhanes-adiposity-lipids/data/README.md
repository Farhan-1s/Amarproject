# NHANES August 2021-August 2023 data

Official source: CDC/NCHS public NHANES data files.

Base URL: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/

| File | Contents | Merge key |
|---|---|---|
| DEMO_L.xpt | Demographics, pregnancy code, interview/MEC weights, strata and PSU | SEQN |
| BMX_L.xpt | Height, waist circumference and BMI | SEQN |
| TCHOL_L.xpt | Total cholesterol and phlebotomy weight WTPH2YR | SEQN |
| HDL_L.xpt | HDL cholesterol | SEQN |
| BPQ_L.xpt | Cholesterol diagnosis and medication questions | SEQN |
| SMQ_L.xpt | Smoking history and current smoking | SEQN |

Add the filename to the base URL for the public download; replace `.xpt` with `.htm` for each official codebook. These files contain public, de-identified participant records and require no controlled-access application. NHANES combines interviews, standardized examinations and laboratory measurements.

The supplied data snapshot was checked on 20 November 2026. Its original download date was not recorded. `snapshot_sha256.csv` identifies the exact supplied bytes used to regenerate the reports. Running `python src/download_data.py` records actual downloads or local reuse, the check time, URLs and SHA-256 hashes in `data/retrieval.json`; this is not a claim about the original retrieval date.

`src/data_preparation.py` checks unique nonmissing SEQN identifiers and performs validated one-to-one left merges onto DEMO_L. It normalizes infinitesimal SAS floating values to zero, recodes questionnaire refusal/unknown values as missing, audits impossible measurement ranges and checks that total cholesterol is not below HDL. Impossible values are treated as missing, not clipped; valid extreme observations are retained.

The sample is restricted sequentially to examined participants with positive MEC weights, age 20 or older, exclusion of known pregnancy (`RIDEXPRG == 1`), complete BMI/waist/height, complete total/HDL cholesterol, and positive phlebotomy weight. Unknown pregnancy codes are retained and disclosed. Derived measurements are WHtR = waist/height (both cm), non-HDL = total cholesterol minus HDL (mg/dL), and binary indicators at WHtR >= 0.50 and non-HDL >= 160 mg/dL. BMI bins are [0,18.5), [18.5,25), [25,30), [30,infinity).

The weighted blood-analysis summaries use WTPH2YR. Positive WTMEC2YR is used to identify examined participants. Missing optional income or questionnaire data do not exclude otherwise eligible participants. Survey strata and PSU are retained for later inference. Raw XPT files and individual-level data must not be included in the repository or submission ZIP.
