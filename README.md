# OpenAI Chat API プロキシサーバー

既存のチャットサーバーをOpenAI API `/v1/chat/completions` 互換のインターフェースでラップするプロキシサーバーです。

## プロジェクト概要

- **目的**: 既存のチャットサーバー（HTTPでJSONリクエストをPOST、Server-Sent Events形式でJSONレスポンスを返却）をOpenAI API互換にする
- **利用者**: 1人での利用を想定（多数の同時接続は不要）
- **開発言語**: Python 3.11+
- **フレームワーク**: Flask（Phase 1）

## 機能

### 対応エンドポイント

- `POST /v1/chat/completions` - OpenAI API互換のチャット完了エンドポイント
- `GET /health` - ヘルスチェックエンドポイント

### サポートパラメータ

**必須**:
- `model`: モデル名
- `messages`: メッセージ配列（role, content）

**オプション**:
- `temperature`: 温度パラメータ（デフォルト: 1.0）
- `max_tokens`: 最大トークン数
- `stream`: ストリーミング有効/無効（デフォルト: false）
- `stop`: 停止文字列

## インストールと起動

### 1. 仮想環境のセットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 環境変数の設定（オプション）

```bash
export EXISTING_SERVER_URL="http://your-chat-server.com/chat"
export REQUEST_TIMEOUT="30"
export HOST="localhost"
export PORT="8000"
export DEBUG="false"
export LOG_LEVEL="INFO"
export DEFAULT_MODEL="gpt-3.5-turbo"
```

### 3. アプリケーションの起動

```bash
python app_flask.py
```

サーバーは `http://localhost:8000` で起動します。

## 使用例

### 非ストリーミングチャット

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello, world!"}
    ],
    "temperature": 0.7
  }'
```

### ストリーミングチャット

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Hello, world!"}
    ],
    "stream": true
  }'
```

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

## プロジェクト構造

```
.
├── app_flask.py           # Flask版メインアプリケーション
├── config.py              # 設定管理
├── core/                  # 共通ビジネスロジック
│   ├── __init__.py
│   ├── client.py          # 既存サーバー通信クライアント
│   ├── converter.py       # データ変換ロジック
│   └── models.py          # データ構造定義
├── requirements.txt       # 依存関係
├── requirements/
│   └── flask.txt          # Flask版依存関係
└── tests/                 # テストファイル
    ├── test_app_flask.py
    ├── test_client.py
    ├── test_config.py
    ├── test_converter.py
    └── test_models.py
```

## テスト実行

```bash
# 全テスト実行
python -m pytest tests/ -v

# 特定のテストファイル実行
python -m pytest tests/test_app_flask.py -v
```

## 設定可能な環境変数

| 環境変数 | デフォルト値 | 説明 |
|----------|-------------|------|
| EXISTING_SERVER_URL | http://localhost:3000/chat | 既存チャットサーバーのURL |
| REQUEST_TIMEOUT | 30 | リクエストタイムアウト（秒） |
| HOST | localhost | サーバーのホスト |
| PORT | 8000 | サーバーのポート |
| DEBUG | false | デバッグモード |
| LOG_LEVEL | INFO | ログレベル |
| DEFAULT_MODEL | gpt-3.5-turbo | デフォルトモデル名 |

## エラーハンドリング

- 既存サーバーへの接続失敗: 503 Service Unavailable
- リクエストタイムアウト: 504 Gateway Timeout
- 無効なリクエスト形式: 400 Bad Request
- その他のエラー: 500 Internal Server Error

## 開発・デバッグ

### デバッグモードで起動

```bash
export DEBUG="true"
python app_flask.py
```

### ログレベルの変更

```bash
export LOG_LEVEL="DEBUG"
python app_flask.py
```

## ライセンス

使用ライブラリはすべて商用利用可能です：
- Flask: BSD-3-Clause
- requests: Apache-2.0