# 第三方資料來源與權利聲明

## 來源

| 項目 | 說明 |
|---|---|
| 資料集名稱 | Sleep Efficiency Dataset |
| Kaggle 發布者 | Equilibriumm（發布者身分不等同已確認的原始著作權人） |
| 資料集頁面 | https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency |
| 發布者頁面 | https://www.kaggle.com/equilibriumm |
| 原始資料檔名 | `Sleep_Efficiency.csv` |
| 官方 License 欄位原文 | **Data files © Original Authors** |
| 查核日期 | 2026-10-18 |

查核時已直接查看 Kaggle 資料集的 Data Card 與展開後的 Metadata → License，兩處均顯示上述文字。頁面未提供 CC0、CC BY、MIT 等明確的標準授權名稱或相應法律條款連結，亦未在所查閱內容中提供明確的 CSV 再散布許可。因此，本文件保留原權利聲明與來源，**不將這份資料宣稱為公有領域或已獲開放授權**。

## 本包涵蓋的資料檔案

| 檔案 | 內容與處理 |
|---|---|
| `Linear Regression/Sleep_Efficiency.csv` | 本專案使用的完整資料副本：452 筆、15 欄。未於本次文件整理中修改；未另行下載並驗證與 Kaggle 當前版本逐位元相同。 |
| `EDA/Sleep_Efficiency_train_v2.csv` | 從完整資料衍生的訓練子集：316 筆、15 欄。經逐列核對，所有資料均可依 ID 對應至上述完整檔，且全部欄位值相同。 |

本機檔案的 SHA-256（用於辨識本包版本）：

```text
Linear Regression/Sleep_Efficiency.csv
1e2a1c44f992c49b18b31fc53e268601f1a8c940a270282e0e11d7739cc92793

EDA/Sleep_Efficiency_train_v2.csv
44902c464df701783820d063fefbee6be4fdff5d4d58fc209e2e0f467d91f453
```

分析程式會在記憶體中進行時間轉換、分組、缺失值處理與特徵工程，並產生圖表及統計摘要。訓練子集的製作或這些分析處理不代表本組取得了原始資料的著作權，也不構成新的第三方資料授權。

## 權利與使用限制

> Data files © Original Authors

隨附資料的相關權利仍屬原權利人。本包為 NYCU Data Mining Group 06 的 HW1 分析專案；此用途說明本身不構成教育用途豁免或再散布許可，也不表示原作者、發布者或 Kaggle 為本專案背書。

目前查得的「Data files © Original Authors」標示不足以確認公開再散布 CSV 的具體授權範圍。**引用來源、保留此聲明，或資料可免費下載，均不能單獨視為已取得再散布許可。** 公開發布或再散布含完整資料或訓練子集的版本前，應確認原權利人的明確許可或其他適用依據；若無法確認，應改提供原資料集下載連結，由使用者自行取得資料。

本文件是資料來源及權利狀態的紀錄，不是原權利人授予的授權契約，也不新增、擴張或取代原資料的使用許可。不得以本組程式或文件未來可能採用的開源授權，概括覆蓋這些第三方資料。

## 建議引用

以下格式用於標明本專案實際取得資料的來源，不將 Kaggle 發布者推定為原始研究作者：

```text
Equilibriumm (Kaggle publisher). Sleep Efficiency Dataset [Data set]. Kaggle.
https://www.kaggle.com/datasets/equilibriumm/sleep-efficiency
Accessed 2026-10-18.
License field: Data files © Original Authors.
```

若後續取得原權利人的授權文件，應保存該文件並更新本說明。
