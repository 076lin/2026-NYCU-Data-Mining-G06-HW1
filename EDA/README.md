# EDA 訓練資料重跑結果

資料來源：Sleep_Efficiency_train_v2.csv，316 筆、15 欄。
輸入檔 SHA-256：44902c464df701783820d063fefbee6be4fdff5d4d58fc209e2e0f467d91f453

## 開啟結果

- EDA_report.html：包含完整執行輸出與圖表，可直接用瀏覽器開啟。
- data_mining_hw1_caffeine_binary_interaction.ipynb：已清除舊輸出並逐格重新執行的 Notebook。
- univariate_eda/：單變量 EDA 圖表與統計表。
- interaction_results_fixed/：12 個交互作用檢定、FDR 校正、分組斜率與樣本數。
- notebook_results/：Notebook 的獨立 PNG、描述統計、Box-Cox 參數、咖啡因二元交互作用檢定與分組斜率。
- time_fig*.png 與 time_eda_console_output.txt：時間欄位驗證與 5 張圖。
- figures/：依原壓縮檔結構，放置 4 張本次重新生成的圖表副本。
- run_manifest.json：來源雜湊、執行紀錄、套件版本及調整清單。
- *.py.log 與 notebook_console_output.txt：本次執行紀錄。

## 本次結果

- Sleep duration 與修正跨夜日期後的 Wakeup time − Bedtime 相符：316/316 筆。
- Notebook 共完成 9 個咖啡因二元交互作用檢定。
- 原始 p < 0.05 的特徵：Alcohol consumption, Age, Gender, Bedtime_Category。
- BH-FDR < 0.05 的特徵：Alcohol consumption, Age, Gender, Bedtime_Category。
- 獨立交互作用程式完成 12 個檢定，各模型依所需欄位排除缺失值。
- 共輸出 38 張 PNG（含 figures/ 的 4 張副本）。

## 執行調整

保留原始分析方法與分組邊界，只將資料來源指向指定 CSV；停用 Notebook 自動安裝與 Kaggle 下載。
設定 NumPy 隨機種子為 42，並增加獨立圖表與統計表匯出。
原 Notebook 靜默忽略模型錯誤的程式已改為報錯，以確保沒有漏跑。
原 Notebook 最後的固定結論改為依本次結果生成，未校正 p 值與 FDR 結果分別列示。
Notebook 使用原本的三組 Bedtime 分組；獨立 interaction_tests_fixed.py 使用原本的四組分法，兩者保留不同設定。
原壓縮檔完整內容另存於工作目錄 original_archive/，不混入本次產出。

## 再次執行

安裝 requirements.txt 所列套件後，可執行：

```powershell
python EDA.py
python univariate_eda.py --csv Sleep_Efficiency_train_v2.csv --output-dir univariate_eda
python interaction_tests_fixed.py --csv Sleep_Efficiency_train_v2.csv --output-dir interaction_results_fixed
```

Notebook 的所有分析格可在 Jupyter 依序執行；若沒有 eda-local 核心，選擇安裝上述套件的 Python 核心。
這些統計結果描述觀察資料中的關聯，不代表因果；原程式以未校正 p < 0.05 選圖，請同時參考 FDR 欄位。
