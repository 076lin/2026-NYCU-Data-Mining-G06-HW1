import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# 設定論文級風格樣式
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False


# ==========================================
# 0. Console 雙重輸出設定 (Console Logger)
# ==========================================
class ConsoleLogger:

  def __init__(self, filename='time_eda_console_output.txt'):
    self.terminal = sys.stdout
    self.log = open(filename, 'w', encoding='utf-8')

  def write(self, message):
    self.terminal.write(message)
    self.log.write(message)

  def flush(self):
    self.terminal.flush()
    self.log.flush()


sys.stdout = ConsoleLogger('time_eda_console_output.txt')

print('==================================================')
print('  Sleep Efficiency - Time Features EDA Report')
print('==================================================\n')

# ==========================================
# 1. 載入資料 (請確認檔案路徑)
# ==========================================
csv_filename = 'Sleep_Efficiency_train_v2.csv'
df = pd.read_csv(csv_filename)

print(f'總資料筆數: {len(df)}\n')

# ==========================================
# 2. 時間解析與邏輯驗證
# ==========================================
bed_dt = pd.to_datetime(df['Bedtime'])
wake_dt = pd.to_datetime(df['Wakeup time'])

# A. 統計 Bedtime 字面時間早於 Wakeup time 的筆數
bed_earlier_count = (bed_dt < wake_dt).sum()
bed_equal_count = (bed_dt == wake_dt).sum()
bed_later_count = (bed_dt > wake_dt).sum()

print('=== 1. Bedtime 與 Wakeup time 時間先後統計 ===')
print(f'1. Bedtime 早於 Wakeup time 筆數: {bed_earlier_count}')
print(f'2. Bedtime 與 Wakeup time 完全相同筆數: {bed_equal_count}')
print(
    f'3. Bedtime 晚於 Wakeup time 筆數 (跨夜未+1天Bug): {bed_later_count}'
)
print(
    f'   -> 跨夜未+1天筆數佔總資料比例: {(bed_later_count / len(df)) * 100:.2f}%\n'
)

# B. 修正跨夜日期 Bug：若 Wakeup time <= Bedtime，自動加上 1 天 (24 小時)
wake_dt_fixed = np.where(
    wake_dt <= bed_dt, wake_dt + pd.Timedelta(days=1), wake_dt
)
wake_dt_fixed = pd.to_datetime(wake_dt_fixed)

# 計算修復後的實際在床時間 (Time in Bed, 單位：小時)
calculated_duration = (
    wake_dt_fixed - bed_dt
).dt.total_seconds() / 3600.0

# C. 檢查 Sleep duration 是否完全等於 (Wakeup time - Bedtime)
diff = np.abs(df['Sleep duration'] - calculated_duration)
exact_match_count = (diff < 1e-4).sum()

print('=== 2. Sleep duration 關係式驗證 ===')
print(
    f'Sleep duration == (Wakeup time - Bedtime) 符合筆數: {exact_match_count}'
    f' / {len(df)}'
)
print(f'符合率: {(exact_match_count / len(df)) * 100:.2f}%')

if exact_match_count == len(df):
  print(
      '\n【重要結論】原始欄位 Sleep duration 實質為「躺在床上的總時間 (Time in'
      ' Bed)」，\n且 100% 由 Wakeup time - Bedtime 算得。'
  )

# ==========================================
# 3. 分開繪製並儲存 5 張獨立 EDA 圖表
# ==========================================
print('\n=== 3. 分別繪製並儲存 5 張 EDA 圖表... ===')

# --- 圖 1: 算得時數 vs 原始 Sleep duration (對角線吻合圖) ---
plt.figure(figsize=(6, 5))
plt.scatter(
    calculated_duration,
    df['Sleep duration'],
    color='#2b5c8f',
    alpha=0.7,
)
plt.plot(
    [calculated_duration.min(), calculated_duration.max()],
    [calculated_duration.min(), calculated_duration.max()],
    'r--',
    linewidth=2,
    label='Y = X (100% Match)',
)
plt.title(
    'Calculated Duration vs. Raw Sleep Duration', fontsize=12, fontweight='bold'
)
plt.xlabel('Calculated (Wakeup - Bedtime) [Hours]', fontsize=11)
plt.ylabel('Raw Sleep Duration Field [Hours]', fontsize=11)
plt.legend()
plt.tight_layout()
plt.savefig('time_fig1_duration_match.png', dpi=300)
plt.close()

# --- 圖 2: 上床小時 (Bedtime Hour) 分佈直方圖 ---
plt.figure(figsize=(6, 5))
bed_hours = bed_dt.dt.hour
sns.countplot(x=bed_hours, palette='Blues_d')
plt.title('Distribution of Bedtime Hours', fontsize=12, fontweight='bold')
plt.xlabel('Bedtime Hour (0~23)', fontsize=11)
plt.ylabel('Count', fontsize=11)
plt.tight_layout()
plt.savefig('time_fig2_bedtime_hour.png', dpi=300)
plt.close()

# --- 圖 3: 睡眠時數 (Sleep duration) 分佈圖 ---
plt.figure(figsize=(6, 5))
sns.histplot(
    df['Sleep duration'],
    kde=True,
    color='#2ecc71',
    bins=15,
)
plt.title('Distribution of Sleep Duration', fontsize=12, fontweight='bold')
plt.xlabel('Sleep Duration [Hours]', fontsize=11)
plt.ylabel('Density / Count', fontsize=11)
plt.tight_layout()
plt.savefig('time_fig3_duration_dist.png', dpi=300)
plt.close()

# --- 圖 4: 上床小時 (Bedtime Hour) vs 睡眠效率 (Sleep Efficiency) 箱形圖 ---
plt.figure(figsize=(6, 5))
sns.boxplot(x=bed_hours, y=df['Sleep efficiency'], palette='Blues_d')
plt.title('Bedtime Hour vs. Sleep Efficiency', fontsize=12, fontweight='bold')
plt.xlabel('Bedtime Hour (0~23)', fontsize=11)
plt.ylabel('Sleep Efficiency', fontsize=11)
plt.tight_layout()
plt.savefig('time_fig4_bedtime_vs_efficiency.png', dpi=300)
plt.close()

# --- 圖 5: 睡眠時數 (Sleep Duration) vs 睡眠效率 (Sleep Efficiency) 箱形圖 ---
plt.figure(figsize=(6, 5))
# 將連續型的 Sleep duration 依照數值繪製 Boxplot
sns.boxplot(
    x=df['Sleep duration'],
    y=df['Sleep efficiency'],
    palette='Greens_d',
)
plt.title('Sleep Duration vs. Sleep Efficiency', fontsize=12, fontweight='bold')
plt.xlabel('Sleep Duration [Hours]', fontsize=11)
plt.ylabel('Sleep Efficiency', fontsize=11)
plt.tight_layout()
plt.savefig('time_fig5_duration_vs_efficiency.png', dpi=300)
plt.close()

print('已順利輸出以下 5 張獨立圖表：')
print('  1. time_fig1_duration_match.png (算得時數 vs 原始欄位吻合圖)')
print('  2. time_fig2_bedtime_hour.png (上床小時數分佈圖)')
print('  3. time_fig3_duration_dist.png (睡眠時數分佈圖)')
print('  4. time_fig4_bedtime_vs_efficiency.png (上床小時 vs 睡眠效率箱形圖)')
print('  5. time_fig5_duration_vs_efficiency.png (睡眠時數 vs 睡眠效率箱形圖)')
print('\nConsole Log 已成功儲存至: time_eda_console_output.txt')
print('==================================================')