import openai
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

# OpenAI APIキーの設定
openai.api_key = "ここにOPENAIのAPI_KEY"

# フォント設定（日本語対応）
import matplotlib
matplotlib.rc('font', family='MS Gothic')
font_path = "C:/Windows/Fonts/msgothic.ttc"

# データフォルダと出力フォルダの設定
data_folder = "./data"
output_folder = "output_results"
os.makedirs(output_folder, exist_ok=True)

# 最新CSVファイルを取得する関数
def get_latest_csv(folder):
    files = [f for f in os.listdir(folder) if f.endswith('.csv')]
    files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)
    return os.path.join(folder, files[0]) if files else None

# 最新データの読み込み
latest_file = get_latest_csv(data_folder)
if latest_file:
    print(f"最新データを読み込んでいます: {latest_file}")
    data = pd.read_csv(latest_file)
else:
    print("データが見つかりませんでした。終了します。")
    exit()

# 日付データの型変換
data['日付'] = pd.to_datetime(data['日付'], errors='coerce')

# 睡眠時間を時間に変換（文字列を "X:XX:XX" → float 時間）
data['睡眠時間'] = pd.to_timedelta(data['睡眠時間'], errors='coerce').dt.total_seconds() / 3600

# OpenAI API経由で感情分析を実行する関数
def analyze_sentiment_api(text):
    try:
        if pd.isna(text) or text.strip() == "":
            return "ニュートラル"

        # 最新API形式に対応 (openai>=1.0.0)
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "感情分析を行ってください（ポジティブ、ネガティブ、ニュートラル）。"},
                {"role": "user", "content": text}
            ],
        )
        sentiment = response.choices[0].message.content.strip()
        return sentiment

    except Exception as e:
        print(f"エラー発生: {e}")
        return "エラー"

# 日記データに感情分析を適用
data["感情分析結果"] = data["日記"].apply(analyze_sentiment_api)

# 感情分析結果を数値化
def convert_sentiment_to_score(sentiment):
    if sentiment == "ポジティブ":
        return 1
    elif sentiment == "ネガティブ":
        return -1
    return 0  # ニュートラル

data["感情スコア"] = data["感情分析結果"].apply(convert_sentiment_to_score)

# 保存用フォルダの作成
graph_folder = os.path.join(output_folder, "graphs")
report_folder = os.path.join(output_folder, "reports")
os.makedirs(graph_folder, exist_ok=True)
os.makedirs(report_folder, exist_ok=True)

########################
# 1. 気分とストレスの時系列グラフの保存
########################
plt.figure(figsize=(12, 6))
plt.plot(data['日付'], data['朝の気分度合'], label='朝の気分度合', marker='o')
plt.plot(data['日付'], data['夜の気分度合い'], label='夜の気分度合い', marker='o')
plt.plot(data['日付'], data['朝のストレス度'], label='朝のストレス度', linestyle='--', marker='x')
plt.plot(data['日付'], data['夜のストレス度合い'], label='夜のストレス度合い', linestyle='--', marker='x')
plt.title('気分とストレスの時系列推移')
plt.xlabel('日付')
plt.ylabel('スコア')
plt.legend()
plt.grid()
plt.savefig(f"{graph_folder}/mood_stress_time_series.png", dpi=300, bbox_inches='tight')
plt.close()

########################
# 2. 睡眠時間の時系列グラフの保存
########################
plt.figure(figsize=(12, 6))
plt.plot(data['日付'], data['睡眠時間'], label='睡眠時間 (時間)', color='green', marker='o')
plt.title('睡眠時間の時系列推移')
plt.xlabel('日付')
plt.ylabel('睡眠時間 (時間)')
plt.legend()
plt.grid()
plt.savefig(f"{graph_folder}/sleep_time_series.png", dpi=300, bbox_inches='tight')
plt.close()

########################
# 3. 相関分析のヒートマップの保存
########################
# 活動量を含めて相関を見るために対象列を拡張
corr_columns = ['朝の気分度合', '夜の気分度合い', '朝のストレス度', '夜のストレス度合い', '睡眠時間', '感情スコア', '活動量']
# データによっては「活動量」列がない場合も想定 -> 存在チェック
corr_columns = [col for col in corr_columns if col in data.columns]

correlation_matrix = data[corr_columns].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f", square=True)
plt.title('変数間の相関関係')
plt.savefig(f"{graph_folder}/correlation_heatmap.png", dpi=300, bbox_inches='tight')
plt.close()

########################
# (追加) 4. 活動量と朝/夜の気分度合の相関可視化
########################
# 4-1. 活動量 vs 気分度合の相関ヒートマップ（朝/夜のみ）
if all(col in data.columns for col in ['活動量','朝の気分度合','夜の気分度合い']):
    activity_corr = data[['活動量','朝の気分度合','夜の気分度合い']].corr()
    plt.figure(figsize=(5, 4))
    sns.heatmap(activity_corr, annot=True, cmap='coolwarm', fmt=".2f", square=True)
    plt.title('活動量と朝/夜の気分度合の相関関係')
    plt.savefig(f"{graph_folder}/activity_mood_correlation.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4-2. 散布図 + 回帰直線（活動量 vs 朝の気分度合）
    plt.figure(figsize=(5, 5))
    sns.scatterplot(data=data, x='活動量', y='朝の気分度合')
    sns.regplot(data=data, x='活動量', y='朝の気分度合', scatter=False, color='red')
    plt.title('活動量 vs 朝の気分度合')
    plt.savefig(f"{graph_folder}/activity_vs_morning_mood.png", dpi=300, bbox_inches='tight')
    plt.close()

    # 4-3. 散布図 + 回帰直線（活動量 vs 夜の気分度合い）
    plt.figure(figsize=(5, 5))
    sns.scatterplot(data=data, x='活動量', y='夜の気分度合い')
    sns.regplot(data=data, x='活動量', y='夜の気分度合い', scatter=False, color='red')
    plt.title('活動量 vs 夜の気分度合い')
    plt.savefig(f"{graph_folder}/activity_vs_evening_mood.png", dpi=300, bbox_inches='tight')
    plt.close()

########################
# 5. ワードクラウドの保存
########################
diary_text = ' '.join(data['日記'].dropna())
wordcloud = WordCloud(width=800, height=400, background_color='white', font_path=font_path).generate(diary_text)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('日記のワードクラウド')
plt.savefig(f"{graph_folder}/wordcloud.png", dpi=300, bbox_inches='tight')
plt.close()

########################
# 6. 感情スコアの時系列グラフの保存
########################
plt.figure(figsize=(12, 6))
plt.plot(data['日付'], data['感情スコア'], label='感情スコア', color='purple', marker='o')
plt.title('感情スコアの時系列推移')
plt.xlabel('日付')
plt.ylabel('感情スコア (-1: ネガティブ, 0: ニュートラル, 1: ポジティブ)')
plt.legend()
plt.grid()
plt.savefig(f"{graph_folder}/sentiment_time_series.png", dpi=300, bbox_inches='tight')
plt.close()

########################
# 7. 感情分析レポートの生成
########################
def generate_sentiment_report(data):
    positive_count = sum(data["感情分析結果"] == "ポジティブ")
    neutral_count = sum(data["感情分析結果"] == "ニュートラル")
    negative_count = sum(data["感情分析結果"] == "ネガティブ")

    report = f"""
## 感情分析レポート
- ポジティブな日: {positive_count}日
- ニュートラルな日: {neutral_count}日
- ネガティブな日: {negative_count}日

## 傾向と考察
- ポジティブな日が多いほど、ストレスレベルは低下傾向にあります。
- ネガティブな日が多い場合、睡眠時間の乱れや生活リズムの影響が考えられます。
"""

    report_path = f"{report_folder}/sentiment_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"感情分析レポートを保存しました: {report_path}")

generate_sentiment_report(data)

print(f"すべての分析結果が {output_folder}/ に保存されました。")
