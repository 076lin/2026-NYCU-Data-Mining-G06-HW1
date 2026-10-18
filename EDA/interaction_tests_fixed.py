"""Exploratory interaction tests for the Kaggle Sleep Efficiency dataset.

Run:
    python interaction_tests.py --csv Sleep_Efficiency.csv

Dependencies: pandas numpy scipy statsmodels
Outputs: interaction_results/interaction_tests.csv, group_slopes.csv,
         group_counts.csv, interaction_report.txt

All tests use complete cases per model and HC3 robust standard errors.
These are observational, unadjusted exploratory associations, not causal effects.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

Y = 'Sleep efficiency'
CAFF = 'Caffeine consumption'
ALC = 'Alcohol consumption'
NUMERIC = ['Age', 'Sleep duration', 'Awakenings', 'Exercise frequency']


def interaction_test(df, label, formula, terms, group_for_slopes=None, x=None):
    """Fit HC3 OLS and perform joint Wald test for all interaction coefficients."""
    fit = smf.ols(formula, data=df).fit(cov_type='HC3')
    names = list(fit.params.index)
    hits = [t for t in names if any(token in t for token in terms)]
    if not hits:
        raise RuntimeError(f'No interaction coefficients found for {label}. Params: {names}')
    R = np.zeros((len(hits), len(names)))
    for i, t in enumerate(hits):
        R[i, names.index(t)] = 1.0
    test = fit.wald_test(R, scalar=True)
    ci = fit.conf_int()
    output = {'Test':label, 'N':int(fit.nobs), 'Formula':formula,
              'Interaction_terms':'; '.join(hits), 'Joint_Wald_chi2':float(test.statistic),
              'Wald_df':len(hits), 'Interaction_p':float(test.pvalue),
              'R2':float(fit.rsquared)}
    slopes = []
    for t in hits:
        output['Coef_'+t] = float(fit.params[t])
        output['P_'+t] = float(fit.pvalues[t])
        output['CI_low_'+t] = float(ci.loc[t, 0])
        output['CI_high_'+t] = float(ci.loc[t, 1])
    if x is not None and group_for_slopes is not None:
        from patsy import build_design_matrices, dmatrix
        design_info = getattr(fit.model.data, "design_info", None)
        if design_info is None:
            # Recover Patsy encoding when the installed statsmodels does not retain it.
            design_info = dmatrix(formula.split("~", 1)[1], df, return_type="dataframe").design_info
        for group in pd.unique(group_for_slopes.dropna()):
            # Contrast of the slope at chosen group, using an explicit design matrix via predict.
            # The intercept / other terms cancel when x changes from 0 to 1.
            frame = pd.DataFrame({x:[0.0, 1.0], group_for_slopes.name:[group, group]})
            dm = build_design_matrices([design_info], frame)[0]
            vec = np.asarray(dm[1] - dm[0]).ravel()
            effect = fit.t_test(vec)
            interval = effect.conf_int()[0]
            slopes.append({'Test': label, 'Group':str(group), 'Slope':float(effect.effect.item()),
                           'CI_low':float(interval[0]), 'CI_high':float(interval[1]),
                           'Slope_p':float(effect.pvalue)})
    return output, slopes


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', default='Sleep_Efficiency.csv')
    p.add_argument('--output-dir', default='interaction_results')
    args = p.parse_args()
    path = Path(args.output_dir)
    path.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.csv)
    df.columns = df.columns.str.strip()
    required = [Y, CAFF, ALC, 'Bedtime', 'Sleep duration', *NUMERIC]
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise SystemExit('Missing columns: ' + ', '.join(missing))
    for col in [Y, CAFF, ALC, *NUMERIC]:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Two caffeine definitions. These refer to consumption in the data, NOT coffee use.
    df['Caffeine_binary'] = np.where(df[CAFF].isna(), np.nan, (df[CAFF] > 0).astype(int))
    # Secondary three-level grouping: 0, (0,50], >50 mg.
    df['Caffeine_3level'] = pd.cut(df[CAFF], [-0.001, 0, 50, np.inf],
                                    labels=['None','Low (0-50 mg]','High (>50 mg)'])
    bed = pd.to_datetime(df['Bedtime'], errors='coerce')
    hour = bed.dt.hour + bed.dt.minute/60 + bed.dt.second/3600
    # Do not classify 07:00 or 14:00 as 'late-night'; create explicit daytime group.
    df['Bedtime_group'] = pd.Categorical(np.select(
        [hour.ge(18) & hour.lt(23), hour.ge(23), hour.ge(0) & hour.lt(6), hour.ge(6) & hour.lt(18)],
        ['Early (18:00-22:59)', 'Regular (23:00-23:59)', 'Late (00:00-05:59)', 'Daytime (06:00-17:59)'],
        default='Missing'),
        categories=['Early (18:00-22:59)', 'Regular (23:00-23:59)',
                    'Late (00:00-05:59)', 'Daytime (06:00-17:59)'])
    df.loc[hour.isna(), 'Bedtime_group'] = np.nan

    results, slopes, counts = [], [], []
    def group_counts(frame, name, group, extra=None):
        for k, n in frame.groupby(group, observed=True).size().items():
            counts.append({'Test': name, 'Group':str(k), 'N':int(n)})

    # 1. Main question: Does alcohol slope differ for caffeine users/nonusers?
    label='Alcohol x caffeine (binary >0 mg)'
    subset=df[[Y, ALC,'Caffeine_binary']].dropna().copy()
    group_counts(subset,label,'Caffeine_binary')
    f='Q("Sleep efficiency") ~ Q("Alcohol consumption") * C(Caffeine_binary)'
    row, sl=interaction_test(subset,label,f,['Q("Alcohol consumption"):C(Caffeine_binary)'],
                            subset['Caffeine_binary'], ALC)
    results.append(row);slopes.extend(sl)

    # 2. Sensitivity: original continuous mg, and three-level categories.
    label='Alcohol x caffeine (continuous mg)'
    subset=df[[Y, ALC,CAFF]].dropna().copy()
    f='Q("Sleep efficiency") ~ Q("Alcohol consumption") * Q("Caffeine consumption")'
    row,sl=interaction_test(subset,label,f,['Q("Alcohol consumption"):Q("Caffeine consumption")'])
    results.append(row)

    label='Alcohol x caffeine (3 levels)'
    subset=df[[Y,ALC,'Caffeine_3level']].dropna().copy()
    group_counts(subset,label,'Caffeine_3level')
    f='Q("Sleep efficiency") ~ Q("Alcohol consumption") * C(Caffeine_3level)'
    row,sl=interaction_test(subset,label,f,['Q("Alcohol consumption"):C(Caffeine_3level)'],
                            subset['Caffeine_3level'], ALC)
    results.append(row);slopes.extend(sl)

    # 3. Duration x bedtime: joint test across all time groups, including daytime.
    label='Sleep duration x bedtime (4 groups)'
    subset=df[[Y,'Sleep duration','Bedtime_group']].dropna().copy()
    group_counts(subset,label,'Bedtime_group')
    f='Q("Sleep efficiency") ~ Q("Sleep duration") * C(Bedtime_group)'
    row,sl=interaction_test(subset,label,f,['Q("Sleep duration"):C(Bedtime_group)'],
                            subset['Bedtime_group'], 'Sleep duration')
    results.append(row);slopes.extend(sl)

    # 4. Further exploratory screens against binary/three-level caffeine.
    for x in NUMERIC:
        for var,tag in [('Caffeine_binary','binary'), ('Caffeine_3level','3 levels')]:
            label=f'{x} x caffeine ({tag})'
            subset=df[[Y,x,var]].dropna().copy()
            group_counts(subset,label,var)
            f=f'Q("Sleep efficiency") ~ Q("{x}") * C({var})'
            row,sl=interaction_test(subset,label,f,[f'Q("{x}"):C({var})'],
                                    subset[var],x)
            results.append(row);slopes.extend(sl)

    report=pd.DataFrame(results)
    report['BH_FDR_q'] = multipletests(report['Interaction_p'], method='fdr_bh')[1]
    report.to_csv(path/'interaction_tests.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(slopes).to_csv(path/'group_slopes.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(counts).to_csv(path/'group_counts.csv',index=False,encoding='utf-8-sig')

    lines=['Exploratory HC3-robust OLS interaction tests',
           'Wald p-values test interaction coefficients jointly equal zero.',
           'BH-FDR q-values adjust across ALL tests in this report.',
           'Each test uses its own complete-case dataset; varying N is expected.',
           'Caffeine binary means >0 mg vs 0 mg; it does not imply coffee drinking.',
           'Bedtime bins: early 18-23, regular 23-24, late 00-06, daytime 06-18.',
           'Observational associations are not causal conclusions.', '',
           f'Input rows: {len(df)}', '',
           report[['Test','N','Joint_Wald_chi2','Wald_df','Interaction_p','BH_FDR_q']].to_string(index=False,float_format=lambda z:f'{z:.6g}'),
           '', 'Group counts:', pd.DataFrame(counts).to_string(index=False),
           '', 'Group-specific slopes and HC3 95% CIs:',
           pd.DataFrame(slopes).to_string(index=False,float_format=lambda z:f'{z:.6g}')]
    (path/'interaction_report.txt').write_text('\n'.join(lines),encoding='utf-8')
    print('\n'.join(lines))
    print(f'\nSaved files to: {path.resolve()}')

if __name__=='__main__':
    main()
