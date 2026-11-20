import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from data_preparation import ROOT, prepare_data, save_table

df, audits = prepare_data()
for name, table in audits.items():
    save_table(table, name)
variables = ['Non_HDL_C', 'WHtR', 'BMXBMI', 'RIDAGEYR', 'INDFMPIR']
desc = df[variables].agg(['count', 'mean', 'std', 'median']).T
desc['Q1'] = df[variables].quantile(.25)
desc['Q3'] = df[variables].quantile(.75)
desc['IQR'] = desc.Q3 - desc.Q1
save_table(desc.rename_axis('Variable').reset_index(), 'phase1_descriptive')
freq = []
for col in ['Sex', 'BMI_Category', 'High_WHtR', 'Age_Group', 'Smoking_Status']:
    for category, count in df[col].astype(object).fillna('Unknown').value_counts().items():
        freq.append((col, str(category), int(count), 100 * count / len(df)))
save_table(pd.DataFrame(freq, columns=['Variable', 'Category', 'Count', 'Percent']), 'phase1_frequencies')
weighted = pd.DataFrame([(col, df[col].mean(), np.average(df[col], weights=df.WTPH2YR)) for col in ['RIDAGEYR', 'Non_HDL_C']], columns=['Variable', 'Unweighted', 'Phlebotomy_weighted'])
save_table(weighted, 'phase1_weighted')
groups = df.groupby(['BMI_Category', 'High_WHtR'], observed=False).Non_HDL_C.agg(['count', 'mean', 'median', 'std']).reset_index()
save_table(groups, 'phase1_groups')
print(audits['sample_flow'].to_string(index=False))
print(desc.to_string())
print(weighted.to_string(index=False))
sns.set_theme(style='whitegrid', font_scale=1.05)
(ROOT / 'figures').mkdir(exist_ok=True)

plt.figure(figsize=(10, 5))
plt.barh(audits['sample_flow'].Stage, audits['sample_flow'].Retained, color='steelblue')
plt.gca().invert_yaxis()
plt.xlabel('Number of participants')
plt.title('Selection of the analytical sample')
plt.tight_layout()
plt.savefig(ROOT / 'figures/fig1_sample_flow.png', dpi=200)
plt.close()

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
labels = ['Non-HDL cholesterol (mg/dL)', 'BMI (kg/m²)', 'Waist-to-height ratio (unitless)']
for ax, col, label in zip(axes, ['Non_HDL_C', 'BMXBMI', 'WHtR'], labels):
    sns.histplot(df[col], kde=True, ax=ax, color='steelblue')
    ax.axvline(df[col].mean(), color='firebrick', linestyle='--', label='Mean')
    ax.axvline(df[col].median(), color='black', label='Median')
    ax.set(xlabel=label, ylabel='Number of participants', title=label.split(' (')[0])
    ax.legend(fontsize=9)
fig.tight_layout()
fig.savefig(ROOT / 'figures/fig2_distributions.png', dpi=200)
plt.close(fig)

plt.figure(figsize=(10, 5))
plot_df = df.assign(Central_obesity=df.High_WHtR.map({0: 'WHtR < 0.50', 1: 'WHtR ≥ 0.50'}))
sns.boxplot(data=plot_df, x='BMI_Category', y='Non_HDL_C', hue='Central_obesity', palette='Set2')
plt.xlabel('BMI category')
plt.ylabel('Non-HDL cholesterol (mg/dL)')
plt.title('Cholesterol by BMI category and waist-to-height ratio')
plt.legend(title='Waist-to-height ratio')
plt.tight_layout()
plt.savefig(ROOT / 'figures/fig3_group_comparisons.png', dpi=200)
plt.close()

plt.figure(figsize=(8, 4))
counts = df.BMI_Category.value_counts(sort=False)
plt.bar(counts.index.astype(str), counts.values, color='steelblue')
plt.xlabel('BMI category')
plt.ylabel('Number of participants')
plt.title('BMI categories in the analytical sample')
plt.tight_layout()
plt.savefig(ROOT / 'figures/fig8_bmi_frequencies.png', dpi=200)
plt.close()
