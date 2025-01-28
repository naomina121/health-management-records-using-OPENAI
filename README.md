# health-management-records-using-OPENAI

OPENAIを使用した健康管理記録

こちらは、これまで作成してきた CSV データをもとに分析し、レポート・画像を出力する Python スクリプトの概要仕様書です。以下の項目を満たすように設計しています。

---

## 1. 前提情報

※　入力済みの情報のみ取り扱う
例）スプレッドシートから記録をCSVに出力

![image](https://github.com/user-attachments/assets/a10146a8-00e5-490b-9620-947bed9ba89c)


- **対象 CSV データ**: スプレッドシートからエクスポートされる、以下のような形式の CSV ファイル

  ```csv
  日付,朝の気分度合,夜の気分度合い,朝のストレス度,夜のストレス度合い,睡眠時間,就寝時間,起床時間,食事内容,運動内容や回数,マインドフルネス・深呼吸,日記
  2025/01/25,6,8,2,6,0:00:00,0:00:00,0:00:00,お弁当,軽い散歩、通院,深呼吸,躁状態により活動が活発化している反面、できないことが増えている一方で、睡眠欲求が減ってしまった。音楽を聴く、自分の気持ちの言語化をすることで脳の疲労を防ぐことができているのかもしれないが、頑張りすぎてしまう。
  2025/01/26,7,8,6,9,10:59:30,20:45:26,7:44:56,〃,なし,深呼吸,寝不足が続くためいつもより就寝時間を早めにしてみることにする。
  2025/01/27,3,5,1,1,7:52:15,21:51:35,5:43:50,〃,なし,なし,躁状態が長引くということはなく途中疲れを認識し睡眠に入れた。日中も眠気から、違和感を感じた部分もあるが（少し焦り？）、眠ったら、落ち着いてきた。
  ```

- **Python バージョン**: 3.9 以上を想定

- **ライブラリ**

  - `pandas` (CSVの読み込みやデータ変換)
  - `matplotlib`, `seaborn` (グラフ作成)
  - `wordcloud` (ワードクラウド生成)
  - `openai` (API を使用した感情分析) ※ ただし、クォータの管理とバージョンに注意

---

## 2. スクリプトの概要

1. **CSVファイル読み込み**
   - `./data` ディレクトリに保存された CSVファイルのうち、最も更新日時が新しいものを取得。
   - それを `pandas` で読み込み、各列に応じてデータを格納。
2. **データの前処理**
   - 日付列 (`日付`) の型を日時型 (`datetime`) に変換。
   - 時間形式の列（例: `睡眠時間`）は `to_timedelta` 等で時間数値 (float) に変換。
3. **感情分析 (OpenAI API)**
   - `日記` 列の文章を OpenAI ChatCompletions API (最新ライブラリの場合: `openai.chat.completions.create`) へ送信し、ポジティブ / ネガティブ / ニュートラル等の判定結果を取得。
   - 取得した感情をスコア化（例: ポジティブ=1, ネガティブ=-1, ニュートラル=0）。
4. **可視化**
   - 気分度合いやストレス度を時系列でプロットしたグラフを出力。
   - 睡眠時間を折れ線グラフで表示。
   - 相関ヒートマップを作成し、各変数(気分度合, ストレス度, 睡眠時間, 感情スコアなど) の相関係数を視覚化。
   - ワードクラウドを生成し、`日記` 欄で使用される単語の頻出度を可視化。
5. **レポート生成**
   - 感情分析の結果件数(ポジティブ, ネガティブ, ニュートラル) を集計。
   - テキストファイルとしてレポートを出力。考察や傾向を記載。

---

## 3. 出力先のディレクトリ構成

```plaintext
output_results
├─ graphs
│  ├─ mood_stress_time_series.png
│  ├─ sleep_time_series.png
│  ├─ correlation_heatmap.png
│  ├─ wordcloud.png
│  └─ sentiment_time_series.png
└─ reports
   └─ sentiment_report.txt
```

- `graphs` フォルダに各種グラフを画像として保存
- `reports` フォルダに感情分析レポートを保存

### 画像の仮置き場所

- 仮に、**imgur** のような画像ホスティングサービスを利用する場合は、以下の流れを想定：

  1. `output_results/graphs` に保存されたPNGファイルを手動・またはAPI経由でアップロード。
  2. 生成されたURLリンクを共有先に貼り付ける。

- S3 (AWS) や自前のサーバーを使用する場合も同様の手順でアップロードしてURLを共有します。

画像例

![wordcloud](https://github.com/user-attachments/assets/23afef00-7f13-4085-8e3a-10cf78ed8aa5)

![sleep_time_series](https://github.com/user-attachments/assets/7dd026b7-a62a-4b42-a9ad-d8d5d477c648)

![sentiment_time_series](https://github.com/user-attachments/assets/38d6ad42-8b78-47d2-984c-e75366616a33)

![mood_stress_time_series](https://github.com/user-attachments/assets/e6201ceb-d892-403e-be85-72f35f3fc362)

![correlation_heatmap](https://github.com/user-attachments/assets/b452287b-6d9e-4e65-a365-7fc732ea7419)

### 感情分析レポート

```

    ## 感情分析レポート
    - ポジティブな日: 0日
    - ニュートラルな日: 1日
    - ネガティブな日: 2日

    ## 傾向と考察
    - ポジティブな日が多いほど、ストレスレベルは低下傾向にあります。
    - ネガティブな日が多い場合、睡眠時間の乱れが影響している可能性があります。
```

---

## 4. 実行時の注意点

1. **Python環境と依存ライブラリ**
   - `pip install -r requirements.txt` 等で必要なライブラリをインストールしてから実行してください。
2. **OpenAI API キーの設定**
   - 環境変数 `OPENAI_API_KEY` にキーをセット、またはコード内で `openai.api_key = "sk-xxxxx"` のように直接記述。
3. **レート制限およびクォータ**
   - OpenAI API の無料枠や課金設定を行い、クォータを超えないよう注意してください。
4. **時差 / タイムゾーン**
   - 日付・日時を取り扱う際にタイムゾーンが考慮されているか確認。
5. **感情分析の精度**
   - ChatGPTのモデルは万能ではないため、誤分類も起こりうる。参考程度に活用してください。

---



## 5. 今後の拡張案（参考程度に）

1. **機械学習モデルとの連携**
   - Pythonの機械学習ライブラリ（scikit-learn など）を用いて、気分度合・ストレス度と睡眠時間や感情スコアの関係を回帰分析してみる。
2. **自動レポーティング**
   - 自動でPDFやMarkdown形式にまとめ、メール送信・Slack送信などの機能を追加。
3. **ダッシュボード化**
   - PlotlyやStreamlitなどの可視化フレームワークを使って、ブラウザ上でインタラクティブにデータを参照できるようにする。
4. **夜間モードや日付フィルタ機能**
   - GUIツールを導入し、日付の範囲指定や特定条件での可視化などを簡単に行えるようにする。

---

## 6. よくあるエラーと対処

1. **KeyError / FileNotFoundError**
   - CSV列名が一致しない、またはファイルが見つからない。列名を確認し、パスを修正。
2. **module 'openai' has no attribute 'ChatCompletion'**
   - `openai` ライブラリのバージョンが古い/新しい。バージョンを揃える、またはコードをマイグレーションする。
3. **Rate limit / insufficient\_quota**
   - OpenAIのAPIクォータ超過。UsageとBillingを確認し、クレジット追加またはプラン変更。
4. **unhashable type: 'dict'**
   - Python で `{}` (set) と `[]` (list) を混同している。`messages` はリストで指定する。
5. **'ChatCompletion' object is not subscriptable**
   - 新バージョンのOpenAIライブラリで返却されるオブジェクトを辞書扱いしている。`response.choices[0].message.content` のようにドット記法でアクセス。

---

## 7. 実行例

```bash
# PowerShellでの例
$Env:OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxx"
python your_script.py
```

```bash
# CMD.exeでの例
set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
python your_script.py
```

---
