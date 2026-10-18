# 2026 National Yang Ming Chiao Tung University Data Mining — Group 06 / HW1

以睡眠與生活習慣資料進行探索性資料分析（EDA）、交互作用檢定，以及睡眠效率（`Sleep efficiency`）的迴歸預測。本專案包含分析程式、Jupyter Notebook、CSV 資料與已產出的 EDA 圖表及報告。

本專案使用 Kaggle 上由 **Equilibriumm** 發布的 [Sleep Efficiency Dataset](https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency)。**資料集的官方授權欄位標示為「Data files © Original Authors」；隨附資料的權利與散布限制請見 [DATA_LICENSE.md](DATA_LICENSE.md)。**

## 組員與工作分配

| 姓名 | 學號 | 工作分配 |
|---|---|---|
| 王裕昕 | 315554006 | EDA、基準模型（baselines）、特徵工程 |
| 林李奕 | 315553025 | EDA、特徵工程 |
| 林群佑 | 315554038 | EDA、第 2 節撰寫、投影片 |
| 林庠安 | 315551119 | EDA、特徵工程、報告撰寫 |
| 林景玄 | 315551127 | EDA、特徵工程、投影片 |
| 顏丞硯 | 315554021 | EDA、Sleep duration 分析、報告與投影片撰寫 |
| 林程亮 | 112550125 | EDA、報告的相關研究（related work） |
| 郭佳翰 | 315551137 | 基準模型（baselines）、特徵工程 |

## 專案內容

```text
2026-NYCU-Data-Mining-G06-HW1/
├── README.md
├── DATA_LICENSE.md                      # 第三方資料來源、權利聲明與使用限制
├── EDA/
│   ├── README.md                        # EDA 重跑紀錄與詳細說明
│   ├── requirements.txt                 # EDA 環境的套件版本紀錄
│   ├── Sleep_Efficiency_train_v2.csv     # 316 筆訓練資料、15 欄
│   ├── data_mining_hw1_caffeine_binary_interaction.ipynb
│   ├── EDA.py                           # 時間欄位驗證與視覺化
│   ├── univariate_eda.py                # 單變量分析
│   ├── interaction_tests_fixed.py       # HC3 交互作用檢定與 BH-FDR 校正
│   ├── EDA_report.html                  # 可直接開啟的完整 EDA 報告
│   ├── notebook_results/                # Notebook 圖表與統計表
│   ├── univariate_eda/                  # 單變量圖表與摘要
│   ├── interaction_results_fixed/       # 交互作用檢定結果與分組斜率
│   ├── figures/                         # 部分圖表副本
│   ├── time_fig*.png                    # 時間欄位分析圖表
│   ├── run_manifest.json                # 資料雜湊、版本與執行紀錄
│   └── verification.json                # 隨附的 EDA 驗證紀錄
└── Linear Regression/
    ├── README.md                        # 模型方法與詳細結果
    ├── requirements.txt
    ├── Sleep_Efficiency.csv             # 452 筆完整資料、15 欄
    └── Sleep_Efficiency_v2.ipynb          # 前處理、特徵工程、調參與評估
```

只想查看已有結果時，可先開啟 [EDA 報告](EDA/EDA_report.html)，或在 Jupyter 中查看兩份 Notebook 的既有輸出。`Linear Regression/eda_plots/` 與 `Linear Regression/results/` 會在重新執行模型 Notebook 時產生，目前這包未附這兩個目錄。

## 資料與分析目標

預測目標 `Sleep efficiency` 是在床時間中實際睡著的比例，以 0–1 表示。資料欄位如下：

| 類型 | 欄位 |
|---|---|
| 識別與人口統計 | `ID`、`Age`、`Gender` |
| 時間與睡眠 | `Bedtime`、`Wakeup time`、`Sleep duration`、`Sleep efficiency`、`Awakenings` |
| 睡眠階段比例 | `REM sleep percentage`、`Deep sleep percentage`、`Light sleep percentage` |
| 生活習慣 | `Caffeine consumption`、`Alcohol consumption`、`Smoking status`、`Exercise frequency` |

`Linear Regression/Sleep_Efficiency.csv` 含 452 筆資料；`EDA/Sleep_Efficiency_train_v2.csv` 含其中 316 筆。訓練檔的 316 筆均可依 `ID` 對應到完整檔，且全部欄位值相同。

| 缺失欄位 | 完整資料（452 筆） | EDA 訓練資料（316 筆） |
|---|---:|---:|
| Awakenings | 20 | 14 |
| Caffeine consumption | 25 | 16 |
| Alcohol consumption | 14 | 8 |
| Exercise frequency | 6 | 6 |

模型排除 `ID`、原始時間字串、`Wakeup time` 與三個睡眠階段比例，將 `Bedtime` 轉換為相對午夜的小時數。時間 EDA 另外檢查跨夜日期：若起床時間不晚於就寢時間，計算時加上一天；在隨附的 316 筆訓練資料中，修正後的時間差皆與 `Sleep duration` 相符。這是本資料的數值檢查結果，欄位意義仍應搭配原始資料說明理解。

## 執行方式

以下命令從專案根目錄執行，使用 Windows PowerShell。建議使用 Python 3.13，以接近子目錄所記錄的環境；套件的實際 Python 版本需求仍以各套件為準。

### 1. 建立環境

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r "EDA/requirements.txt" -r "Linear Regression/requirements.txt"
```

`EDA/requirements.txt` 固定了原執行環境的版本，模型目錄則使用套件版本下限；安裝時需要套件來源提供相應版本。兩份 Notebook 均讀取隨附的 CSV，不需要 Kaggle API 金鑰。

### 2. 重跑 EDA

```powershell
Set-Location EDA
..\.venv\Scripts\python.exe EDA.py
..\.venv\Scripts\python.exe univariate_eda.py --csv Sleep_Efficiency_train_v2.csv --output-dir univariate_eda
..\.venv\Scripts\python.exe interaction_tests_fixed.py --csv Sleep_Efficiency_train_v2.csv --output-dir interaction_results_fixed
..\.venv\Scripts\python.exe -m notebook data_mining_hw1_caffeine_binary_interaction.ipynb
```

在 Jupyter 選擇此環境的 Python 核心，依序執行所有儲存格。Notebook 內原本關於自動下載的開頭文字仍有保留，但目前載入程式實際使用 `Sleep_Efficiency_train_v2.csv`。

如需更新 HTML 報告，先在 Jupyter 執行並儲存 Notebook，再從 `EDA/` 執行：

```powershell
..\.venv\Scripts\python.exe -m jupyter nbconvert --to html data_mining_hw1_caffeine_binary_interaction.ipynb --output EDA_report
```

這些操作會更新同名圖表、統計表、日誌或報告；既有的 `run_manifest.json`、`verification.json` 是隨附執行的紀錄，以上命令不會自動重建它們。

### 3. 重跑迴歸模型

若接續前一步，先回到根目錄，再進入模型目錄：

```powershell
Set-Location ..
Set-Location "Linear Regression"
..\.venv\Scripts\python.exe -m notebook Sleep_Efficiency_v2.ipynb
```

在 Jupyter 選擇此環境的 Python 核心，執行 **Restart Kernel and Run All Cells**。請保留 CSV 與 Notebook 位於同一目錄。輸出包含 `eda_plots/` 圖表及 `results/` 內的評估、消融實驗、係數與顯著性檢定結果。

## 方法與既有結果

### EDA

- 以 316 筆訓練資料分析分布、缺失值、時間欄位及生活習慣與睡眠效率的關聯。
- Notebook 將咖啡因分為 `0 mg` 與 `>0 mg`，進行 9 個 HC3 robust Wald 交互作用檢定，並提供 BH-FDR 校正結果。
- 隨附結果中，`Alcohol consumption`、`Age`、`Gender`、`Bedtime_Category` 的交互作用在 FDR 校正後仍達 0.05 顯著水準。
- 獨立程式另外提供 12 個檢定，包含不同咖啡因定義的敏感度分析；Notebook 與獨立程式的就寢時間分組邊界不同，詳見 [EDA 說明](EDA/README.md)。

### 迴歸模型

Notebook 使用 `random_state=20261010` 做 70/30 切分，得到 316 筆訓練資料與 136 筆測試資料，並以訓練集的 10-fold CV MAE 選擇超參數。缺失值填補、特徵工程、標準化及適用的特徵選擇放在 pipeline 中處理。

比較 OLS、Ridge、LASSO、Elastic Net，以及平均值、單變量 OLS、Random Forest、Gradient Boosting 基準。Set C 包含覺醒次數截頂、年齡平方、飲酒／運動門檻及吸菸與飲酒交互作用，最終共 13 個特徵。

以下數值摘自隨附 Notebook 的已儲存輸出：

| 模型 | CV MAE（平均 ± 標準差） | Test MAE | Test RMSE | Test R² |
|---|---:|---:|---:|---:|
| 平均值基準 | 0.1149 ± 0.0149 | 0.1146 | 0.1336 | −0.0017 |
| 單變量 OLS（Awakenings） | 0.0905 ± 0.0122 | 0.0901 | 0.1082 | 0.3431 |
| Set A：OLS（原始特徵） | 0.0808 ± 0.0093 | 0.0739 | 0.0927 | 0.5177 |
| Set B：OLS（CV 選擇 top-6） | 0.0797 ± 0.0089 | 0.0743 | 0.0932 | 0.5125 |
| **Set C：Elastic Net** | **0.0686 ± 0.0090** | **0.0630** | **0.0812** | **0.6301** |
| Random Forest | 0.0611 ± 0.0062 | 0.0591 | 0.0776 | 0.6617 |
| Gradient Boosting | 0.0644 ± 0.0092 | 0.0606 | 0.0791 | 0.6484 |

MAE 與 RMSE 越低越好；例如 MAE 0.0630 約為睡眠效率 6.3 個百分點的平均絕對誤差。上述結果屬觀察資料上的預測與關聯分析，不支持因果推論。

## 資料來源與版權

- 資料集：[Sleep Efficiency Dataset — Equilibriumm / Kaggle](https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency)。
- 官方 License 欄位原文：**Data files © Original Authors**（查核日期：2026-10-18）。
- 本包的完整 CSV 與訓練子集均源自該資料集；原資料的權利屬原權利人，不能因隨附於作業而視為由本組重新授權。

詳見 [DATA_LICENSE.md](DATA_LICENSE.md)，其中列出適用檔案、來源及查核範圍。本包目前未另行指定本組程式與文件的開源授權；資料權利聲明僅說明第三方資料的權利狀態。
