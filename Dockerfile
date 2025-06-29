# Python 3.11ベースイメージを使用
FROM python:3.11-slim

# curlをインストール（ヘルスチェック用）
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# ポート8000を開放
EXPOSE 8000

# app_flask.pyを実行
CMD ["python", "app_flask.py"]