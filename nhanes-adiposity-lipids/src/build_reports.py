from html import escape
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether

ROOT = Path(__file__).resolve().parents[1]
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body', fontName='Times-Roman', fontSize=10.5, leading=14, spaceAfter=8))
styles.add(ParagraphStyle(name='CaptionSmall', fontName='Times-Italic', fontSize=9, leading=11, spaceAfter=8))
styles['Title'].fontName = 'Times-Bold'
styles['Title'].fontSize = 19
styles['Title'].leading = 23
styles['Heading2'].fontName = 'Times-Bold'
styles['Heading2'].fontSize = 13
styles['Heading2'].leading = 16
styles['Heading2'].spaceBefore = 10
styles['Heading2'].spaceAfter = 8
story, markdown = [], []


def read(name):
    return pd.read_csv(ROOT / 'tables' / f'{name}.csv')


def paragraph(text, style='Body'):
    story.append(Paragraph(escape(text), styles[style]))
    markdown.append(text + '\n')


def heading(text):
    paragraph(text, 'Heading2')


def page():
    story.append(PageBreak())


def table(frame, caption, digits=2):
    def fmt(value):
        if pd.isna(value):
            return '-'
        if isinstance(value, float):
            return f'{value:,.{digits}f}'
        return str(value)
    rows = [[str(x).replace('_', ' ') for x in frame.columns]] + [[fmt(x) for x in row] for row in frame.itertuples(index=False, name=None)]
    font = ParagraphStyle('Cell', fontName='Times-Roman', fontSize=8.5, leading=10.5)
    cells = [[Paragraph(escape(x), font) for x in row] for row in rows]
    widths = [481 / len(rows[0])] * len(rows[0])
    t = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf2')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.black),('LINEBELOW',(0,-1),(-1,-1),.5,colors.grey),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story.append(KeepTogether([Paragraph(escape(caption), styles['CaptionSmall']), t, Spacer(1,9)]))
    markdown.append(caption + '\n\n' + '| ' + ' | '.join(rows[0]) + ' |\n' + '| ' + ' | '.join(['---']*len(rows[0])) + ' |\n' + '\n'.join('| ' + ' | '.join(r) + ' |' for r in rows[1:]) + '\n')


def figure(name, caption, height=190):
    image = Image(str(ROOT / 'figures' / name))
    scale = min(481 / image.imageWidth, height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    story.append(KeepTogether([image, Spacer(1,5), Paragraph(escape(caption), styles['CaptionSmall'])]))
    markdown.append(f'![{caption}](../figures/{name})\n')


def title(text):
    paragraph(text, 'Title')
    paragraph('Farhan Behmanesh | Student ID 403170117', 'CaptionSmall')
    paragraph('NHANES August 2021-August 2023', 'CaptionSmall')


def footer(canvas, doc):
    canvas.setFont('Times-Roman', 9)
    canvas.drawCentredString(A4[0]/2, 30, str(doc.page))


def finish(name):
    (ROOT / 'reports').mkdir(exist_ok=True)
    doc = SimpleDocTemplate(str(ROOT / 'reports' / f'{name}.pdf'), pagesize=A4, rightMargin=57, leftMargin=57, topMargin=42, bottomMargin=45, title=name + ' NHANES adiposity and cholesterol', author='Farhan Behmanesh')
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    (ROOT / 'reports' / f'{name}.md').write_text('\n'.join(markdown), encoding='utf-8')


def references():
    heading('Sources')
    paragraph('CDC/NCHS public documentation, consulted 20 November 2026. DEMO_L describes the sampling variables and pregnancy codes; TCHOL_L and HDL_L specify WTPH2YR for blood-analyte analysis. The sample-design overview describes age-based selection and nonresponse adjustments.', 'CaptionSmall')
    for url in ['https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm', 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/TCHOL_L.htm', 'https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/HDL_L.htm']:
        paragraph(url, 'CaptionSmall')


title('Phase 1\nStudy design and descriptive statistics')
heading('Question and study design')
paragraph('How do waist-to-height ratio (WHtR) and body mass index (BMI) relate to non-HDL cholesterol among adults, and how do the observed patterns vary by sex, age and income? This phase describes the data and compares cholesterol across adiposity groups. The same measurements are available for each retained participant, making a descriptive comparison possible. Formal inference and adjusted comparisons are reserved for later phases.')
paragraph('NHANES is a cross-sectional observational survey of the US civilian, non-institutionalized population. Household interviews are followed by standardized measurements at mobile examination centers (MECs) and laboratory testing. Its probability sample uses geographic strata, primary sampling units and household selection. Age groups have unequal selection probabilities. Random selection of participants does not make adiposity an assigned treatment, so these data cannot establish causation.')
paragraph('One row represents one participant, identified by SEQN. The source files have unique identifiers and are joined using validated one-to-one left merges onto the interview sample. This preserves people without examination or laboratory records until explicit sample selection. The data are public and de-identified.')
table(read('source_counts'), 'Table 1. Source records and identifier checks.', 0)
table(read('merge_audit'), 'Table 2. Sequential merges onto DEMO_L. Unmatched indicates no record in that component.', 0)
page()
heading('Selection and data quality')
table(read('sample_flow'), 'Table 3. Sample retained and exclusions at each stage.', 0)
figure('fig1_sample_flow.png', 'Figure 1. Participant selection. The final blood-analysis sample contains 5,205 adults.', 110)
paragraph('Known pregnancies (RIDEXPRG=1) are excluded. Code 3 means unknown pregnancy status and is retained: 14 women aged 20-44 in the final sample have this code. Pregnancy status is publicly released only for women aged 20-44, so missing codes elsewhere are not evidence of non-pregnancy. The population is described as adults excluding known pregnancies.')
paragraph('The audit normalizes infinitesimal SAS floating values to zero, recodes questionnaire refusal/unknown codes as missing and preserves structural skips. Nonpositive anthropometry/lipids, invalid age or income ranges, and total cholesterol below HDL are checked. No such impossible measurements were found in the supplied snapshot. Valid extreme values are retained. Full counts and actions are saved in quality_audit.csv and missingness.csv.')
missing = read('missingness')
missing = missing[(missing.Sample == 'Final analytical sample') & missing.Variable.isin(['INDFMPIR','BPQ101D','SMQ040'])]
missing = pd.concat([pd.DataFrame([{'Variable':'All five core measures','Valid':5205,'Missing':0,'Missing_percent':0}]), missing], ignore_index=True)
table(missing[['Variable','Valid','Missing','Missing_percent']], 'Table 4. Final sample availability. SMQ040 includes structural skips.', 2)
page()
heading('Variable scales and continuous summaries')
paragraph('Non-HDL cholesterol (total minus HDL, mg/dL), WHtR (waist/height, both in cm) and BMI (kg/m2) are quantitative continuous ratio variables. Age is recorded in integer years and top-coded at 80; income-to-poverty ratio is continuous and capped at 5. Sex and threshold indicators are binary categories, BMI categories are ordinal, smoking status is nominal and SEQN is an identifier.')
table(read('phase1_descriptive'), 'Table 5. Unweighted summaries. SD uses n-1; count is variable-specific.', 2)
figure('fig2_distributions.png', 'Figure 2. Distributions with the mean (dashed red) and median (solid black).', 175)
paragraph('Non-HDL cholesterol, BMI and WHtR show upper tails, with means above their medians. Median and IQR resist the influence of extreme observations; mean and SD retain information about the full distribution. The income row uses 4,548 observations, with 657 missing (12.62%). No income values are imputed. Age and income caps must be considered when interpreting their upper quartiles.')
heading('Sampling weights and interpretation')
table(read('phase1_weighted'), 'Table 6. Unweighted and WTPH2YR-weighted means in the same analytical sample.', 2)
paragraph('WTPH2YR is required for this cycle\'s blood-analyte analyses, including derived non-HDL cholesterol. Interview and MEC weights cover broader components; the phlebotomy weight additionally addresses blood-draw nonresponse. The weighted age mean is lower than the raw mean, consistent with unequal selection and response. Weighting does not guarantee correction for the additional complete-case exclusions. These are descriptive point estimates; survey variance estimation will use SDMVSTRA and SDMVPSU in later work.')
page()
heading('Categorical distributions')
freq = read('phase1_frequencies')
table(freq, 'Table 7. Counts and percentages of all 5,205 retained participants, including unknown smoking status.', 2)
figure('fig8_bmi_frequencies.png', 'Figure 3. BMI category frequencies. Bars start at zero.', 175)
paragraph('The categorical tables distinguish the composition of this retained sample from a population estimate. Central adiposity is common even though the BMI categories separate a range of general body sizes. Unknown questionnaire responses are shown rather than silently removed from the denominator. Current smoking includes every-day or some-day smoking among participants reporting at least 100 lifetime cigarettes.')
page()
heading('Descriptive group comparisons')
figure('fig3_group_comparisons.png', 'Figure 4. Cholesterol by BMI category and WHtR threshold. Outliers remain visible.', 175)
table(read('phase1_groups'), 'Table 8. Unweighted non-HDL cholesterol by BMI category and central-adiposity status.', 2)
paragraph('Within the normal BMI category, participants above the WHtR threshold have a higher median non-HDL cholesterol than those below it. Substantial distributional overlap remains. Small cells, particularly the underweight group with high WHtR, should not support strong generalizations. These are descriptive differences, without a significance claim.')
heading('Scope and limitations')
paragraph('The finalized question compares WHtR and BMI as correlates of cholesterol. The complete core measurements support that comparison, while the questionnaire and demographic variables permit later adjustment. Missing income, unknown pregnancy status and selection into the complete-case sample limit interpretation. Age top-coding hides variation above 80. Cross-sectional measurements cannot establish temporal order; medication, diet and other confounders may affect cholesterol. The weighted results target the civilian adult population under the survey weighting assumptions, subject to the additional selection limitations.')
references()
finish('phase1')
story, markdown = [], []

prob = read('phase2_probabilities').set_index('Quantity').Value
title('Phase 2\nProbability and distributions')
heading('Events and random variables')
paragraph('The sample is the same 5,205 adults used in phase 1, excluding known pregnancies and retaining 14 unknown pregnancy statuses. Each SEQN identifies one participant. A uniform draw from the retained rows defines the unweighted empirical probability space; weighted proportions use WTPH2YR and have a different target interpretation.')
paragraph('Event A is non-HDL cholesterol >=160 mg/dL. Event B is WHtR >=0.50. X is non-HDL cholesterol (mg/dL), Y is WHtR (unitless), and I(A) is the Bernoulli event indicator. K counts event A in a random subsample of 20 distinct retained participants. Thresholds are fixed operational categories, not diagnoses or evidence of future cardiovascular events.')
heading('Marginal and joint probabilities')
table(read('phase2_joint'), 'Table 1. Empirical joint probabilities; rows are B and columns are A, with marginal totals.', 4)
paragraph(f'P(A)={prob["P(A)"]:.4f}, P(B)={prob["P(B)"]:.4f}, and P(A and B)={prob["P(A and B)"]:.4f}. Under independence the joint probability would equal P(A)P(B)={prob["P(A)P(B)"]:.4f}. The difference is descriptive evidence of dependence in the empirical distribution, not a formal population independence test.')
heading('Conditioning and Bayes theorem')
paragraph(f'P(A|B)={prob["P(A|B)"]:.4f}, whereas P(A|not B)={prob["P(A|not B)"]:.4f}. The former is about {prob["P(A|B)"]/prob["P(A|not B)"]:.2f} times the latter. This comparison uses adults below the waist threshold as its reference, not the unconditional P(A).')
paragraph(f'Bayes theorem gives P(B|A)=P(A|B)P(B)/P(A)={prob["P(B|A) Bayes"]:.4f}. The directly counted P(B|A) is also {prob["P(B|A) empirical"]:.4f}. Observing A updates the empirical probability of B from {prob["P(B)"]:.4f} to {prob["P(B|A) empirical"]:.4f}. All computations use unrounded values.')
page()
heading('Subgroup probabilities and survey weighting')
table(read('phase2_subgroups'), 'Table 2. Event A by WHtR indicator, sex and age group. High WHtR: 0=below 0.50, 1=at least 0.50.', 4)
figure('fig4_subgroup_probs.png', 'Figure 1. Unweighted conditional event probabilities across subgroups.', 175)
paragraph('The observed proportions are similar by sex and vary more across age groups, peaking at ages 40-59. Medication use is one possible explanation for the lower observed proportion at ages 60+, but this analysis does not test that explanation. No hypothesis test, causal interpretation or longitudinal risk estimate is implied.')
weighted = pd.DataFrame([['A', prob['P(A)'], prob['Weighted P(A)']], ['B', prob['P(B)'], prob['Weighted P(B)']]], columns=['Event','Unweighted','WTPH2YR weighted'])
table(weighted, 'Table 3. Sample proportions and phlebotomy-weighted estimates.', 4)
paragraph('The phlebotomy weight accounts for unequal sampling and blood-draw response under the survey adjustments. The observed weight-induced shifts do not identify a single causal explanation: age, other demographics and response adjustments may all contribute. Complete-case selection can still bias weighted estimates. Proportions here do not include survey confidence intervals.')
page()
heading('Counts and the binomial approximation')
figure('fig5_binomial_comparison.png', 'Figure 2. Counts in 1,000 subsamples of 20 distinct rows and the fitted binomial model. Seed=42.', 240)
table(read('phase2_count_moments'), 'Table 4. Count means and variances. Simulation variance uses 999 in its denominator.', 4)
paragraph('The count support is K=0,...,20. For a binomial model, E[K]=np and Var(K)=np(1-p), with p equal to the pooled empirical proportion. Each simulated subsample is drawn uniformly without replacement. Its exact conditional count distribution is hypergeometric, with variance np(1-p)(N-n)/(N-1). Here n/N=20/5205 is about 0.00384, so the binomial approximation is close; simulation noise also contributes to differences in moments. Exact PMFs for all three distributions are saved in phase2_count_pmf.csv.')
paragraph('A binomial model requires a fixed number of binary trials, independent draws and a common marginal success probability. Independent uniform draws with replacement from this pooled empirical population would satisfy that model. Different clinical subgroup probabilities do not themselves invalidate that pooled model. Without-replacement dependence makes the actual simulation hypergeometric. The original NHANES field design also includes clustering and unequal selection, so this row-sampling exercise must not be treated as a reproduction of the survey design.')
page()
heading('Continuous distributions and moments')
diagnostics = read('phase2_diagnostics')
table(diagnostics[['Variable','Empirical_mean','Empirical_variance','Sample_variance','Sample_SD']], 'Table 5. Empirical moments (variance denominator n) and sample summaries (n-1).', 4)
table(diagnostics[['Variable','Skewness','Excess_kurtosis','IQR_outliers']], 'Table 6. Distribution shape and outliers beyond 1.5 IQR fences.', 4)
figure('fig6_normal_diagnostics.png', 'Figure 3. Non-HDL cholesterol density and normal Q-Q plot.', 210)
paragraph('The empirical expectation is the average of the finite observed distribution. Empirical variance divides the squared deviations by n, while sample variance and SD use n-1; these are deliberately distinguished. Cholesterol has an empirical mean near 134.03 mg/dL and SD near 41.04 mg/dL. Its variance is measured in (mg/dL)^2. For I(A), E[I(A)]=p and Var(I(A))=p(1-p), about 0.1824, describing variability of a single binary classification.')
paragraph('Non-HDL cholesterol is right-skewed, with 78 IQR outliers and a Q-Q plot that departs from the reference line in the tails. The fitted normal density therefore gives an inadequate description of individual tail probabilities, even if central coverage is reasonably close. WHtR has milder right skew and 57 IQR outliers; exact normality is not assumed. Valid outliers remain in every calculation. A normality test alone is not used as evidence of fit.')
page()
heading('Two quantitative variables and covariance')
table(read('phase2_covariance'), 'Table 7. Sample variance-covariance matrix using n-1.', 4)
figure('fig7_covariance_scatter.png', 'Figure 4. WHtR and BMI plotted against non-HDL cholesterol.', 215)
paragraph('Both adiposity measures have positive covariance with non-HDL cholesterol, indicating a positive direction of linear co-variation in this sample. The scatter remains broad. Covariance magnitudes cannot directly compare association strength because WHtR and BMI have different scales and units. Standardized associations and regression will be examined later. WHtR and BMI also move together, which matters when both enter a model.')
heading('Interpretation and reproducibility')
paragraph('All subgroup and joint calculations describe the retained cross-sectional sample unless explicitly weighted. Selection due to missing anthropometry or laboratory measurements, unknown pregnancy status, treatment and other confounding limit broader interpretation. Neither covariance nor conditional probability establishes causation. The two analysis scripts use the same preparation function, and the reports are regenerated from saved aggregate CSV tables and figures. The binomial simulation uses NumPy default_rng with seed 42.')
references()
finish('phase2')
