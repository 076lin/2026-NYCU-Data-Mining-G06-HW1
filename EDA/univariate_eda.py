"""Consolidated single-feature EDA from the six supplied files.

Each explanatory feature is analyzed separately against Sleep efficiency;
REM/Deep/Light sleep percentage, interactions, and adjusted models are excluded.

Usage: python univariate_eda.py --csv Sleep_Efficiency.csv --output-dir univariate_eda
Dependencies: pandas numpy scipy matplotlib seaborn statsmodels
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf

TARGET = 'Sleep efficiency'
EXCLUDED = {'REM sleep percentage', 'Deep sleep percentage', 'Light sleep percentage'}
NUMERIC = ['Age', 'Sleep duration', 'Awakenings', 'Caffeine consumption',
           'Alcohol consumption', 'Exercise frequency', 'Bedtime hour', 'Wakeup hour']
CATEGORICAL = ['Gender', 'Smoking status']
COUNT_LIKE = {'Awakenings', 'Caffeine consumption', 'Alcohol consumption', 'Exercise frequency'}
sns.set_theme(style='whitegrid')


def save(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=250, bbox_inches='tight')
    plt.close(fig)


def pvalue(test):
    return float(test.pvalue)


def numeric_eda(df, feature, out):
    data = df[[feature, TARGET]].dropna().copy()
    if len(data) < 4 or data[feature].nunique() < 2:
        return None
    x, y = data[feature], data[TARGET]
    pearson = stats.pearsonr(x, y)
    spearman = stats.spearmanr(x, y)
    model = smf.ols(f'Q("{TARGET}") ~ Q("{feature}")', data=data).fit(cov_type='HC3')
    term = f'Q("{feature}")'
    row = {'Feature': feature, 'Type': 'numeric', 'N': len(data),
           'Missing': int(df[feature].isna().sum()), 'Mean_X': x.mean(),
           'Median_X': x.median(), 'SD_X': x.std(),
           'Pearson_r': float(pearson.statistic), 'Pearson_p': pvalue(pearson),
           'Spearman_rho': float(spearman.statistic), 'Spearman_p': pvalue(spearman),
           'HC3_slope': float(model.params[term]), 'HC3_p': float(model.pvalues[term]),
           'R2': float(model.rsquared)}
    fig, ax = plt.subplots(figsize=(7, 4.5))
    if feature in COUNT_LIKE and x.nunique() <= 20:
        counts = df[feature].value_counts(dropna=False).sort_index()
        ax.bar([str(v) if pd.notna(v) else 'Missing' for v in counts.index], counts.values)
        ax.set_xlabel(feature)
        ax.set_ylabel('Count')
    else:
        sns.histplot(df[feature].dropna(), bins=15, kde=(x.nunique() > 5), ax=ax)
        ax.set_xlabel(feature)
    ax.set_title(f'Distribution: {feature}')
    save(fig, out / f'{feature.replace(" ", "_")}_distribution.png')

    fig, ax = plt.subplots(figsize=(7, 4.5))
    if feature in COUNT_LIKE and x.nunique() <= 20:
        sns.boxplot(data=data, x=feature, y=TARGET, showfliers=False, ax=ax)
        sns.stripplot(data=data, x=feature, y=TARGET, color='gray', alpha=.25, size=2.5, ax=ax)
    else:
        sns.regplot(data=data, x=feature, y=TARGET, ci=95,
                    scatter_kws={'alpha': .28, 's': 16}, ax=ax)
        if feature == 'Age':  # original age EDA also overlays LOWESS
            sns.regplot(data=data, x=feature, y=TARGET, lowess=True, scatter=False,
                        line_kws={'color': 'darkorange', 'label': 'LOWESS'}, ax=ax)
            ax.legend()
    ax.set_title(f'{feature} vs. {TARGET} | Spearman ρ={row["Spearman_rho"]:.3f}')
    save(fig, out / f'{feature.replace(" ", "_")}_vs_efficiency.png')
    if feature == 'Exercise frequency':
        groups = [d[TARGET].values for _, d in data.groupby(feature) if len(d)]
        row['Kruskal_p'] = float(stats.kruskal(*groups).pvalue) if len(groups) >= 2 else np.nan
    if feature == 'Age':
        z = data.copy()
        z['age_centered'] = z[feature] - z[feature].mean()
        quadratic = smf.ols(f'Q("{TARGET}") ~ age_centered + I(age_centered ** 2)',
                            data=z).fit(cov_type='HC3')
        row['Quadratic_p'] = float(quadratic.pvalues['I(age_centered ** 2)'])
    return row


def categorical_eda(df, feature, out):
    data = df[[feature, TARGET]].dropna().copy()
    if data[feature].nunique() < 2:
        return None
    summary = data.groupby(feature)[TARGET].agg(['count','mean','median','std'])
    summary.to_csv(out / f'{feature.replace(" ", "_")}_group_summary.csv')
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sns.countplot(data=df, x=feature, ax=axes[0])
    sns.boxplot(data=data, x=feature, y=TARGET, showfliers=False, ax=axes[1])
    sns.stripplot(data=data, x=feature, y=TARGET, color='gray', size=2.5, alpha=.25, ax=axes[1])
    fig.suptitle(f'{feature} and {TARGET}')
    save(fig, out / f'{feature.replace(" ", "_")}_distribution_and_efficiency.png')
    groups = [d[TARGET].values for _, d in data.groupby(feature)]
    row = {'Feature': feature, 'Type': 'categorical', 'N': len(data),
           'Missing': int(df[feature].isna().sum())}
    if len(groups) == 2:
        row['Welch_p'] = float(stats.ttest_ind(*groups, equal_var=False).pvalue)
        row['Mann_Whitney_p'] = float(stats.mannwhitneyu(*groups, alternative='two-sided').pvalue)
        pooled = np.sqrt(((len(groups[0])-1)*np.var(groups[0], ddof=1) +
                          (len(groups[1])-1)*np.var(groups[1], ddof=1)) / (len(data)-2))
        row['Cohen_d_group2_minus_group1'] = ((np.mean(groups[1])-np.mean(groups[0])) / pooled
                                               if pooled > 0 else np.nan)
    else:
        row['Kruskal_p'] = float(stats.kruskal(*groups).pvalue)
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', default='Sleep_Efficiency.csv')
    ap.add_argument('--output-dir', default='univariate_eda')
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.csv)
    df.columns = df.columns.str.strip()
    if TARGET not in df:
        raise ValueError(f'Missing target column: {TARGET}')
    if any(c in df for c in EXCLUDED):
        print('Excluded sleep stages:', ', '.join(sorted(EXCLUDED)))
    # Original time EDA: represent clock time as an hour, avoiding raw datetime regression.
    for source, dest in [('Bedtime', 'Bedtime hour'), ('Wakeup time', 'Wakeup hour')]:
        if source in df:
            dt = pd.to_datetime(df[source], errors='coerce')
            df[dest] = dt.dt.hour + dt.dt.minute / 60
    if {'Bedtime', 'Wakeup time', 'Sleep duration'}.issubset(df.columns):
        bedtime = pd.to_datetime(df['Bedtime'], errors='coerce')
        wakeup = pd.to_datetime(df['Wakeup time'], errors='coerce')
        wake_fixed = wakeup.where(wakeup > bedtime, wakeup + pd.Timedelta(days=1))
        calculated = (wake_fixed - bedtime).dt.total_seconds() / 3600
        valid = calculated.notna() & df['Sleep duration'].notna()
        match = np.isclose(calculated[valid], df.loc[valid, 'Sleep duration'], atol=1e-4)
        pd.DataFrame([{'Compared_rows': int(valid.sum()), 'Matching_rows': int(match.sum()),
                       'Matching_fraction': float(match.mean()) if len(match) else np.nan}]) \
            .to_csv(out / 'duration_validation.csv', index=False)
    rows = []
    for c in NUMERIC:
        if c in df:
            r = numeric_eda(df, c, out)
            if r is not None: rows.append(r)
    for c in CATEGORICAL:
        if c in df:
            r = categorical_eda(df, c, out)
            if r is not None: rows.append(r)
    if 'Alcohol consumption' in df:
        a = df[['Alcohol consumption', TARGET]].dropna().copy()
        a['Has alcohol'] = a['Alcohol consumption'] > 0
        a.groupby('Has alcohol')[TARGET].agg(['count','mean','median','std']).to_csv(out / 'Alcohol_yes_no_summary.csv')
    if 'Caffeine consumption' in df:
        c = df[['Caffeine consumption', TARGET]].dropna().copy()
        c['Caffeine group'] = pd.cut(c['Caffeine consumption'], [-.001, 0, 50, np.inf],
                                      labels=['None', 'Low', 'High'])
        c.groupby('Caffeine group', observed=True)[TARGET].agg(['count','mean','median','std']) \
            .to_csv(out / 'Caffeine_group_summary.csv')
    result = pd.DataFrame(rows)
    result.to_csv(out / 'univariate_summary.csv', index=False)
    print(result.to_string(index=False))
    print(f'\nSaved tables and figures to: {out.resolve()}')


if __name__ == '__main__':
    main()
