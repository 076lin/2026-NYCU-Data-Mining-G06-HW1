# Predicting Nightly Sleep Efficiency with Linear Regression

NYCU Data Mining 2026 — HW1 · Group 06

<!-- TODO: fill in team members -->
| Name | Student ID |
|---|---|
| | |

## Task

Estimate a night's **sleep efficiency** (proportion of time in bed spent asleep, 0–1) from lifestyle and sleep-diary variables: age, sex, sleep duration, bedtime, awakenings, caffeine, alcohol, smoking and exercise.
Sleep-stage percentages (REM / deep / light) are **excluded by design**.

The final model is a **linear regression** (Elastic Net) on 9 raw inputs plus 5 engineered features. Non-linear models are used only as baselines.

## Repository structure

```
.
├── README.md                    # this file
├── Sleep_Efficiency.csv         # dataset (452 nights × 15 columns)
├── Sleep_Efficiency_v2.ipynb    # full pipeline: preprocessing, features, CV tuning, evaluation, analysis
└── requirements.txt             # Python dependencies
```

Running the notebook creates two output folders:

| Folder | Contents |
|---|---|
| `eda_plots/` | training-set EDA figures |
| `results/` | ablation, tuning curves, coefficient plot, diagnostics, and CSV tables (`main_results.csv`, `fe_ablation_ladder.csv`, `significance_tests.csv`, `ols_coefficients_setC.csv`) |

## How to run

```bash
pip install -r requirements.txt
jupyter notebook Sleep_Efficiency_v2.ipynb   # then: Kernel → Restart & Run All
```

Keep `Sleep_Efficiency.csv` in the same folder as the notebook. A full run takes a few minutes on a laptop.

## Method in brief

1. **Preprocessing**: drop ID, sleep-stage percentages and wake-up time (it equals bedtime + sleep duration). Convert bedtime to signed hours from midnight. Encode Gender (Male = 0, Female = 1) and Smoking (No = 0, Yes = 1).
2. **Split**: random 70/30 hold-out (seed `20261010`) gives 316 training and 136 test nights. The test set is evaluated **once**, at the end.
3. **Inside every CV fold**: mean/mode imputation → feature engineering → standardisation → model. Nothing is fitted on validation or test rows.
4. **Engineered features (Set C)**

   | Feature | Definition |
   |---|---|
   | `Awak_cap2` | min(awakenings, 2); replaces the raw count |
   | `Age_sq` | (age − 40)² |
   | `Alc_heavy` | 1 if alcohol ≥ 2, else 0 |
   | `Ex_any` | 1 if exercise ≥ 1, else 0 |
   | `Smk_x_AlcHeavy` | smoking × `Alc_heavy` |

5. **Models**: OLS, Ridge, LASSO and Elastic Net. `alpha` and `l1_ratio` are tuned by 10-fold CV MAE on the training set only.
6. **Baselines**: training mean, single-feature OLS (awakenings), Random Forest and Gradient Boosting.
7. **Analysis**: paired t-test and Wilcoxon test across folds; standardised OLS coefficients with 95% CI, p-value and VIF; test-set error analysis.

## Main results

| Model | CV MAE (mean ± s.d.) | Test MAE | Test RMSE | Test R² |
|---|---|---|---|---|
| Trivial (training mean) | 0.115 ± 0.015 | 0.115 | 0.134 | −0.00 |
| Simple OLS (awakenings) | 0.091 ± 0.012 | 0.090 | 0.108 | 0.34 |
| Set A: OLS, raw inputs | 0.081 ± 0.009 | 0.074 | 0.093 | 0.52 |
| Set B: OLS, top-6 inputs | 0.080 ± 0.009 | 0.074 | 0.093 | 0.51 |
| **Set C: Elastic Net (ours)** | **0.069 ± 0.009** | **0.063** | **0.081** | **0.63** |
| Random Forest (baseline) | 0.061 ± 0.006 | 0.059 | 0.078 | 0.66 |
| Gradient Boosting (baseline) | 0.064 ± 0.009 | 0.061 | 0.079 | 0.65 |

- Set C lowers per-fold MAE by 0.012 relative to Set A (paired t-test, p < 0.001).
- The non-linear baselines remain better; Random Forest beats Set C by 0.0075 MAE per fold (p = 0.009).
- Largest effects (standardised β): awakenings −0.066; smoking × heavy drinking −0.042.

All numbers above are produced by the notebook with seed `20261010`.

## Data

`Sleep_Efficiency.csv` is the Kaggle *Sleep Efficiency* dataset: <https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency>.
It contains 452 rows and 15 columns; four columns have missing values (Awakenings 20, Caffeine 25, Alcohol 14, Exercise 6).
Kaggle’s official License field states **Data files © Original Authors** (checked 2026-10-18). The page does not provide explicit standard open-license terms or a clear grant to redistribute the CSV. Credit and this notice alone do not establish redistribution permission; confirm permission or another applicable basis before publishing bundled data. See [DATA_LICENSE.md](../DATA_LICENSE.md) for provenance, covered files, and rights limitations. The dataset is not relicensed by this project.
