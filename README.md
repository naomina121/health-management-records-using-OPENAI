# Health Management Records Using OPENAI - 健康管理記録

OPENAIを使用した健康管理記録

こちらは、これまで作成してきた CSV データをもとに分析し、レポート・画像を出力する Python スクリプトの概要仕様書です。以下の項目を満たすように設計しています。

---

## 1. 前提情報

- **対象 CSV データ**: スプレッドシートからエクスポートされる、以下のような形式の CSV ファイル

```
日付,朝の気分度合,夜の気分度合い,朝のストレス度,夜のストレス度合い,睡眠時間,日記,活動量
2025/01/25,6,8,2,6,6:30:00,"躁状態により活動が活発化している...",100
2025/01/26,7,8,6,9,5:45:00,"寝不足が続くためいつもより...",80
```

- **Python バージョン**: 3.9 以上を想定
- **ライブラリ**
  - pandas (CSVの読み込みやデータ変換)
  - matplotlib, seaborn (グラフ作成)
  - wordcloud (ワードクラウド生成)
  - openai (API を使用した感情分析)

---

## 2. スクリプトの概要

1. **CSVファイル読み込み**
   - ./data ディレクトリに保存された CSVファイルのうち、最も更新日時が新しいものを取得。
   - pandas で読み込み、各列に応じてデータを格納。
2. **データの前処理**
   - 日付列 (日付) の型を日時型 (datetime) に変換。
   - 時間形式の列（例: 睡眠時間）は to_timedelta 等で時間数値 (float) に変換。
3. **感情分析 (OpenAI API)**
   - 日記列の文章を OpenAI ChatCompletions API へ送信し、ポジティブ / ネガティブ / ニュートラル等の判定結果を取得。
   - 取得した感情をスコア化（例: ポジティブ=1, ネガティブ=-1, ニュートラル=0）。
4. **可視化**
   - 気分度合いやストレス度を時系列でプロットしたグラフを出力。
   - 睡眠時間を折れ線グラフで表示。
   - 相関ヒートマップを作成し、気分度合・ストレス度・睡眠時間・感情スコア・活動量の相関係数を視覚化。
   - ワードクラウドを生成し、日記 欄で使用される単語の頻出度を可視化。
   - (追加) 活動量と朝/夜の気分度合の相関可視化（ヒートマップおよび散布図＋回帰直線）。
5. **レポート生成**
   - 感情分析の結果件数(ポジティブ, ネガティブ, ニュートラル) を集計。
   - テキストファイルとしてレポートを出力。考察や傾向を記載。

---

## 6. よくあるエラーと対処

1. **KeyError / FileNotFoundError**
   - CSV列名が一致しない、またはファイルが見つからない。列名を確認し、パスを修正。
2. **module 'openai' has no attribute 'ChatCompletion'**
   - openai ライブラリのバージョンが古い/新しい。バージョンを揃える、またはコードをマイグレーションする。
3. **Rate limit / insufficient_quota**
   - OpenAIのAPIクォータ超過。UsageとBillingを確認し、クレジット追加またはプラン変更。
4. **unhashable type: 'dict'**
   - Python で {} (set) と [] (list) を混同している。messages はリストで指定する。
5. **'ChatCompletion' object is not subscriptable**
   - 新バージョンのOpenAIライブラリで返却されるオブジェクトを辞書扱いしている。response.choices[0].message.content のようにドット記法でアクセス。

---

## 7. 今後の拡張案(あくまで参考程度に)

1. **機械学習モデルとの連携**
   - `cikit-learn` などを活用し、睡眠時間・気分度合・ストレス度と感情スコアの関係を回帰分析。
2. **自動レポーティング**
   - PDFやMarkdown形式にまとめ、メール・Slack送信機能の追加。
3. **ダッシュボード化**
   - `Streamlit` や `Plotly` を使ってブラウザ上でインタラクティブにデータを参照可能に。

---

## 8. 画像出力結果（サンプル）

![sentiment_time_series](https://github.com/user-attachments/assets/08c11432-e1a5-4fe5-b40d-1f9e11ccf4b4)
![mood_stress_time_series](https://github.com/user-attachments/assets/bab8c793-3c9f-449b-901a-09897675ce24)
![correlation_heatmap](https://github.com/user-attachments/assets/599d7d31-2b04-46cf-ac9d-73668d8cc422)
![activity_vs_morning_mood](https://github.com/user-attachments/assets/9aee9ef7-e7f3-43ad-aa01-4c6a93c6f3f1)
![activity_vs_evening_mood](https://github.com/user-attachments/assets/8bfcdbe8-2c48-4de4-88a6-58a1dfd55398)
![activity_mood_correlation](https://github.com/user-attachments/assets/f4a61202-f4c9-4a88-972d-2925938e2c9b)
![wordcloud](https://github.com/user-attachments/assets/de82d1c8-ab15-445a-9d76-5cab95ec9785)
![sleep_time_series](https://github.com/user-attachments/assets/a5d9ecc2-3ac4-4442-b204-449f48de9307)

---


