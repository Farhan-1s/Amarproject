# Project Card: Central Adiposity, General BMI, and Non-HDL Cholesterol

## 1. Dataset and Subset Used
- **Track:** Track A — NHANES 2021–2023 (August 2021 – August 2023 cycle)
- **Specific Files:**
  - `DEMO_L.XPT`: Demographics and sample weights (`SEQN`, `RIDAGEYR`, `RIAGENDR`, `INDFMPIR`, `WTINT2YR`, `WTMEC2YR`, `SDMVPSU`, `SDMVSTRA`)
  - `BMX_L.XPT`: Body Measures (`SEQN`, `BMXBMI`, `BMXWAIST`, `BMXHT`)
  - `TCHOL_L.XPT`: Total Cholesterol laboratory file (`SEQN`, `LBXTC`, `WTPH2YR`)
  - `HDL_L.XPT`: Direct HDL-Cholesterol laboratory file (`SEQN`, `LBDHDD`)
  - `BPQ_L.XPT` & `SMQ_L.XPT`: Blood Pressure/Cholesterol & Smoking Questionnaires (`SEQN`, `BPQ101D` for lipid-lowering medication use, `SMQ020` for smoking history)
- **Analytical Subset:** US adults excluding known pregnancies aged 20 years and older who completed both the household interview and the Mobile Examination Center (MEC) examination with valid anthropometric and serum lipid measurements.

## 2. Provisional Project Title
 Comparing Waist-to-Height Ratio and Body Mass Index as Correlates of Non-HDL Cholesterol in US Adults (NHANES 2021–2023)

## 3. Primary Statistical Question
Among US adults aged 20 years and older, how strongly does central adiposity—measured by Waist-to-Height Ratio (WHtR)—associate with serum Non-HDL Cholesterol (`LBXTC - LBDHDD`) compared to general adiposity (BMI), and how does this relationship vary across sex, age groups, and socioeconomic strata?

## 4. Unit of Observation and Target Population
- **Unit of Observation:** A single individual survey participant uniquely identified by the respondent sequence number (`SEQN`). Each row in the merged analytical dataset represents one distinct person (cross-sectional observation).
- **Target Population:** Phlebotomy weights (`WTPH2YR`, in `TCHOL_L`) are used for analyses involving blood cholesterol. The intended target is the civilian, non-institutionalized adult population (aged $\ge 20$) of the United States during 2021–2023. Complete-case selection may still introduce bias after weighting. Results must be interpreted with that limitation. Without weights, summaries describe only the retained sample.

## 5. Main Variables and Measurement Scales
| Variable Name | Source File | Description | Statistical Type & Scale |
| :--- | :--- | :--- | :--- |
| `SEQN` | All files | Respondent sequence number | Identifier (Nominal) |
| `Non_HDL_C` | Derived (`LBXTC - LBDHDD`) | Non-HDL Cholesterol (mg/dL) | Quantitative Continuous (Ratio) |
| `WHtR` | Derived (`BMXWAIST / BMXHT`) | Waist-to-Height Ratio (unitless ratio) | Quantitative Continuous (Ratio) |
| `BMXBMI` | `BMX_L` | Body Mass Index ($\text{kg/m}^2$) | Quantitative Continuous (Ratio) |
| `RIDAGEYR` | `DEMO_L` | Age in years at screening (top-coded at 80) | Quantitative Discrete (Ratio) |
| `INDFMPIR` | `DEMO_L` | Ratio of family income to poverty threshold (0 to 5.0) | Quantitative Continuous (Ratio, capped) |
| `BMI_Category` | Derived | Standard clinical BMI tiers (Underweight, Normal, Overweight, Obese) | Categorical Ordinal |
| `RIAGENDR` | `DEMO_L` | Biological sex (1 = Male, 2 = Female) | Categorical Binary |
| `High_WHtR` | Derived | Central obesity indicator ($\text{WHtR} \ge 0.50$ vs. $< 0.50$) | Categorical Binary |
| `Smoking_Status`| Derived (`SMQ_L`) | Never, Former, or Current smoker | Categorical Nominal |

## 6. Role of Variables in the Question
- **Primary Response Variable:** `Non_HDL_C` (serum Non-HDL Cholesterol in mg/dL, continuous) for descriptive distribution profiling (Phase 1) and linear regression modeling (Phase 4), alongside a clinical binary threshold ($\text{Non-HDL-C} \ge 160\text{ mg/dL}$) for probability and group inference (Phases 2–3).
- **Primary Explanatory Variables:** `WHtR` (central fat distribution) and `BMXBMI` (overall body mass).
- **Grouping & Adjustment Variables:** `RIAGENDR` (sex), `RIDAGEYR` (age), `INDFMPIR` (socioeconomic status), `Smoking_Status`, and cholesterol medication status (`BPQ101D`).

## 7. Question Type
Primarily **associational and comparative**. We compare the distribution of atherogenic cholesterol across central vs. general adiposity categories (descriptive/comparative in Phases 1–3) and evaluate their joint and separate linear associations with Non-HDL Cholesterol (associational in Phase 4).

## 8. Initial Scientific Hypothesis
We expect both BMI and Waist-to-Height Ratio to show a positive association with Non-HDL Cholesterol, as excess adipose tissue promotes dyslipidemia. However, because visceral abdominal fat is more metabolically active in hepatic lipid metabolism than peripheral subcutaneous fat, we hypothesize that individuals with elevated central adiposity ($\text{WHtR} \ge 0.50$) will exhibit higher mean and median Non-HDL Cholesterol even within the same standard BMI category, and that accounting for `WHtR` will attenuate the apparent linear slope of `BMXBMI`.

## 9. Initial Anticipated Limitations
1. **Cross-Sectional Observational Design & Reverse Causality:** Because NHANES captures all measurements at a single time point without experimental intervention, we cannot establish temporal precedence or causal effects. Furthermore, individuals diagnosed with high cholesterol may already be taking statins (`BPQ101D`) or modifying their diet, artificially lowering their observed `Non_HDL_C` despite high BMI/WHtR.
2. **Staged Missingness and Selection into Lab/MEC Subsamples:** While 11,933 individuals completed the initial household interview, only 8,860 attended the Mobile Examination Center. After filtering for adults, excluding 41 pregnant individuals to prevent physiological confounding of waist and lipid measurements, and removing incomplete anthropometric or serum lab results, the final analytical subset stabilized at 5,205 complete adult observations.
3. **Top-Coding of Continuous Variables:** Age (`RIDAGEYR`) is top-coded at 80 years and income-to-poverty ratio (`INDFMPIR`) is top-coded at 5.0 for confidentiality, creating artificial right-censoring spikes in their empirical distributions.
## 10. Operational definitions and analysis scope

The finalized question remains the comparison of WHtR and BMI as correlates of non-HDL cholesterol. Both measurements and both lipid components are available in the same cross-sectional participants. Phases 1 and 2 describe distributions and empirical probabilities; adjusted association and formal inference are reserved for later phases.

The pregnancy rule excludes `RIDEXPRG == 1`. Code 3 (unknown) is retained and explicitly reported; missing pregnancy codes outside the released female age range are not interpreted as evidence of non-pregnancy. Fourteen women aged 20-44 have unknown status in the retained sample. Thus the sample is described as excluding known pregnancies, not as confirmed non-pregnant adults.

The final 5,205 participants have complete core measurements. Income is available for 4,548 participants; income summaries use those observed values without imputation. Questionnaire unknown/refusal codes become missing; structural skips are preserved. Smoking is derived using both SMQ020 and SMQ040 (never, former, current); unresolved responses remain unknown. Questionnaire adjustment is planned for later modeling, not required for the current lipid sample.

Use `WTPH2YR` for the complete-case blood-analysis sample, including comparisons of age and WHtR within that sample. `WTMEC2YR` identifies examined participants; `WTINT2YR` applies to interview-only analyses. `SDMVSTRA` and `SDMVPSU` are retained for later survey variance estimation. No survey confidence intervals or hypothesis tests are claimed in phases 1 and 2.

## Official documentation

- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/TCHOL_L.htm
- https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/HDL_L.htm
- https://wwwn.cdc.gov/Nchs/Nhanes/continuousnhanes/OverviewBrief.aspx?Cycle=2021-2023
