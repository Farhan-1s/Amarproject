import matplotlib
matplotlib.use('Agg')
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

from data_preparation import ROOT, prepare_data, save_table

df, _ = prepare_data()
(ROOT / 'figures').mkdir(exist_ok=True)

p_A = df["High_Lipid"].mean()
p_B = df["High_WHtR"].mean()
p_AB = ((df["High_Lipid"] == 1) & (df["High_WHtR"] == 1)).mean()
p_A_given_B = df.loc[df["High_WHtR"] == 1, "High_Lipid"].mean()
p_A_given_notB = df.loc[df["High_WHtR"] == 0, "High_Lipid"].mean()
p_B_given_A_emp = df.loc[df["High_Lipid"] == 1, "High_WHtR"].mean()
p_B_given_A_bayes = (p_A_given_B * p_B) / p_A

print(f"N = {len(df)}")
print(f"P(A: Non-HDL >= 160) = {p_A:.4f}")
print(f"P(B: WHtR >= 0.50)   = {p_B:.4f}")
print(f"P(A and B)           = {p_AB:.4f}")
print(f"P(A) * P(B)          = {p_A * p_B:.4f}")
print(f"P(A | B)             = {p_A_given_B:.4f}")
print(f"P(A | not B)         = {p_A_given_notB:.4f}")
print(f"P(B | A) Empirical   = {p_B_given_A_emp:.4f}")
print(f"P(B | A) Bayes       = {p_B_given_A_bayes:.4f}\n")

print("Joint Probability Table (Rows: High_WHtR, Cols: High_Lipid):")
print(pd.crosstab(df["High_WHtR"], df["High_Lipid"], normalize="all", margins=True).round(4))
print("\nP(A) by Sex:")
print(df.groupby("Sex")["High_Lipid"].agg(["count", "mean"]).round(4))
print("\nP(A) by Age Group:")
print(df.groupby("Age_Group", observed=False)["High_Lipid"].agg(["count", "mean"]).round(4))

p_A_weighted = np.average(df["High_Lipid"], weights=df["WTPH2YR"])
p_B_weighted = np.average(df["High_WHtR"], weights=df["WTPH2YR"])
print(f"\nWeighted P(A) = {p_A_weighted:.4f} (Unweighted = {p_A:.4f})")
print(f"Weighted P(B) = {p_B_weighted:.4f} (Unweighted = {p_B:.4f})\n")

rng = np.random.default_rng(42)
n_sub = 20
n_trials = 1000
event_array = df["High_Lipid"].to_numpy()
counts = np.array([rng.choice(event_array, size=n_sub, replace=False).sum() for _ in range(n_trials)])

print(f"Binomial (n={n_sub}, p={p_A:.4f}):")
print(f"Theoretical Mean = {n_sub * p_A:.4f}, Empirical Mean = {counts.mean():.4f}")
print(f"Theoretical Var  = {n_sub * p_A * (1 - p_A):.4f}, Empirical Var  = {counts.var(ddof=1):.4f}\n")

for var in ["Non_HDL_C", "WHtR"]:
    s = df[var]
    mu, sigma = s.mean(), s.std(ddof=1)
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    outliers = ((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum()
    w1 = ((s >= mu - sigma) & (s <= mu + sigma)).mean() * 100
    w2 = ((s >= mu - 2 * sigma) & (s <= mu + 2 * sigma)).mean() * 100
    w3 = ((s >= mu - 3 * sigma) & (s <= mu + 3 * sigma)).mean() * 100
    print(f"{var}: Mean={mu:.4f}, Sample variance={s.var(ddof=1):.4f}, SD={sigma:.4f}, Skew={s.skew():.4f}, Kurt={s.kurt():.4f}, IQR_Outliers={outliers}")
    print(f"  Within 1SD={w1:.2f}%, 2SD={w2:.2f}%, 3SD={w3:.2f}%")

print("\nCovariance Matrix:")
print(df[["Non_HDL_C", "WHtR", "BMXBMI"]].cov().round(4))

sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
sns.barplot(x=["WHtR < 0.50", "WHtR >= 0.50"], y=[p_A_given_notB, p_A_given_B], ax=axes[0], color="steelblue")
axes[0].set_title("By Central Obesity")
axes[0].set_ylabel("Empirical Probability P(Non-HDL-C >= 160)")

sex_probs = df.groupby("Sex")["High_Lipid"].mean().reset_index()
sns.barplot(data=sex_probs, x="Sex", y="High_Lipid", ax=axes[1], color="teal")
axes[1].set_title("By Sex")
axes[1].set_ylabel("")

age_probs = df.groupby("Age_Group", observed=False)["High_Lipid"].mean().reset_index()
sns.barplot(data=age_probs, x="Age_Group", y="High_Lipid", ax=axes[2], color="coral")
axes[2].set_title("By Age Group")
axes[2].set_ylabel("")

plt.tight_layout()
plt.savefig(ROOT / "figures/fig4_subgroup_probs.png", dpi=300, bbox_inches="tight")
plt.close()

k_vals = np.arange(n_sub + 1)
emp_pmf = np.array([(counts == k).mean() for k in k_vals])
theo_pmf = stats.binom.pmf(k_vals, n_sub, p_A)

plt.figure(figsize=(10, 6))
plt.bar(k_vals, emp_pmf, alpha=0.65, color="skyblue", edgecolor="navy", label="Empirical Subsamples (1,000 draws, n=20)")
plt.plot(k_vals, theo_pmf, "ro-", linewidth=2, markersize=6, label=f"Theoretical Binomial(n=20, p={p_A:.3f})")
plt.xlabel("Count of Adults with Non-HDL-C >= 160 mg/dL (K)")
plt.ylabel("Probability")
plt.title("Empirical Subsample Counts vs. Theoretical Binomial Model")
plt.xticks(k_vals)
plt.legend()
plt.tight_layout()
plt.savefig(ROOT / "figures/fig5_binomial_comparison.png", dpi=300, bbox_inches="tight")
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
x_vals = df["Non_HDL_C"]
x_grid = np.linspace(x_vals.min(), x_vals.max(), 300)
sns.histplot(x_vals, stat="density", kde=True, ax=axes[0], color="skyblue", label="Empirical Density")
axes[0].plot(x_grid, stats.norm.pdf(x_grid, x_vals.mean(), x_vals.std(ddof=1)), "r--", linewidth=2, label="Normal Approximation")
axes[0].set_title("Non-HDL Cholesterol vs. Normal PDF")
axes[0].set_xlabel("Non-HDL Cholesterol (mg/dL)")
axes[0].legend()

stats.probplot(x_vals, dist="norm", plot=axes[1])
axes[1].set_title("Normal Q-Q Plot: Non-HDL Cholesterol")
plt.tight_layout()
plt.savefig(ROOT / "figures/fig6_normal_diagnostics.png", dpi=300, bbox_inches="tight")
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
axes[0].scatter(df["WHtR"], df["Non_HDL_C"], alpha=0.25, s=12, color="steelblue")
axes[0].set_title("Waist-to-Height Ratio vs. Non-HDL Cholesterol")
axes[0].set_xlabel("Waist-to-Height Ratio (WHtR)")
axes[0].set_ylabel("Non-HDL Cholesterol (mg/dL)")

axes[1].scatter(df["BMXBMI"], df["Non_HDL_C"], alpha=0.25, s=12, color="darkorange")
axes[1].set_title("BMI vs. Non-HDL Cholesterol")
axes[1].set_xlabel("Body Mass Index (kg/m^2)")
axes[1].set_ylabel("Non-HDL Cholesterol (mg/dL)")

plt.tight_layout()
plt.savefig(ROOT / "figures/fig7_covariance_scatter.png", dpi=300, bbox_inches="tight")
plt.close()
probabilities = pd.DataFrame([
    ('P(A)', p_A), ('P(B)', p_B), ('P(A and B)', p_AB),
    ('P(A)P(B)', p_A * p_B), ('P(A|B)', p_A_given_B),
    ('P(A|not B)', p_A_given_notB), ('P(B|A) empirical', p_B_given_A_emp),
    ('P(B|A) Bayes', p_B_given_A_bayes),
    ('Weighted P(A)', p_A_weighted), ('Weighted P(B)', p_B_weighted),
], columns=['Quantity', 'Value'])
save_table(probabilities, 'phase2_probabilities')
save_table(pd.crosstab(df.High_WHtR, df.High_Lipid, normalize='all', margins=True), 'phase2_joint', index=True)
subgroups = []
for col in ['High_WHtR', 'Sex', 'Age_Group']:
    for group, part in df.groupby(col, observed=True):
        subgroups.append((col, group, len(part), part.High_Lipid.sum(), part.High_Lipid.mean()))
save_table(pd.DataFrame(subgroups, columns=['Variable', 'Group', 'N', 'Events', 'Probability']), 'phase2_subgroups')
diagnostics = []
for col in ['Non_HDL_C', 'WHtR']:
    x = df[col]
    q1, q3 = x.quantile([.25, .75])
    iqr = q3 - q1
    diagnostics.append((col, x.mean(), x.var(ddof=0), x.var(ddof=1), x.std(ddof=1), x.skew(), x.kurt(), int(((x < q1 - 1.5*iqr) | (x > q3 + 1.5*iqr)).sum())))
save_table(pd.DataFrame(diagnostics, columns=['Variable', 'Empirical_mean', 'Empirical_variance', 'Sample_variance', 'Sample_SD', 'Skewness', 'Excess_kurtosis', 'IQR_outliers']), 'phase2_diagnostics')
save_table(df[['Non_HDL_C', 'WHtR', 'BMXBMI']].cov().rename_axis('Variable'), 'phase2_covariance', index=True)
finite_factor = (len(df) - n_sub) / (len(df) - 1)
save_table(pd.DataFrame([
    ('Binomial', n_sub*p_A, n_sub*p_A*(1-p_A)),
    ('Hypergeometric', n_sub*p_A, n_sub*p_A*(1-p_A)*finite_factor),
    ('Simulation', counts.mean(), counts.var(ddof=1))
], columns=['Distribution', 'Mean', 'Variance']), 'phase2_count_moments')
save_table(pd.DataFrame({'K': k_vals, 'Empirical_PMF': emp_pmf, 'Binomial_PMF': theo_pmf, 'Hypergeometric_PMF': stats.hypergeom.pmf(k_vals, len(df), int(event_array.sum()), n_sub)}), 'phase2_count_pmf')
