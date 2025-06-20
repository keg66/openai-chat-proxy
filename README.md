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

### アダプターアーキテクチャ

- **環境変数ベース設定**: 様々な既存サーバーに対応するため、フィールドマッピングを環境変数で設定可能
- **ネストフィールド対応**: `response.choices[0].message.content` のような複雑な構造に対応
- **複数ストリーミング形式**: Server-Sent Events、JSON Lines、カスタム形式をサポート
- **カスタムヘッダー**: 認証やAPI キーなどのヘッダーを追加可能
- **フィールド無効化**: 既存サーバーが対応していないパラメータは送信しないよう設定可能

### サポートパラメータ

**必須**:
- `model`: モデル名
- `messages`: メッセージ配列（role, content）

**オプション**:
- `temperature`: 温度パラメータ（デフォルト: 1.0）
- `max_tokens`: 最大トークン数
- `stream`: ストリーミング有効/無効（デフォルト: false）
- `stop`: 停止文字列

## クイックスタート

### 簡単な動作確認

付属のモックサーバーを使って、すぐにプロキシサーバーをテストできます：

```bash
# 1. 仮想環境のセットアップ
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 自動デモの実行
cd sample_server
./start_demo.sh
```

これにより、モックサーバーとプロキシサーバーが自動で起動し、包括的なテストが実行されます。

### 手動テスト

個別にサーバーを起動してテストする場合：

```bash
# ターミナル1: モックサーバーを起動
source venv/bin/activate
python sample_server/mock_chat_server.py

# ターミナル2: プロキシサーバーを起動  
source venv/bin/activate
python app_flask.py

# ターミナル3: テストを実行
source venv/bin/activate
python sample_server/test_demo.py
# または
./sample_server/curl_examples.sh
```

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
│   ├── adapter_config.py  # アダプター設定管理
│   ├── adapters/          # アダプターアーキテクチャ
│   │   ├── __init__.py
│   │   ├── base.py        # ベースアダプタークラス
│   │   ├── configurable.py # 設定可能アダプター
│   │   └── factory.py     # アダプターファクトリー
│   ├── client.py          # 既存サーバー通信クライアント
│   ├── converter.py       # データ変換ロジック
│   └── models.py          # データ構造定義
├── requirements.txt       # 依存関係
├── requirements/
│   └── flask.txt          # Flask版依存関係
├── sample_server/         # 動作確認用サンプル
│   ├── mock_chat_server.py  # 模擬チャットサーバー
│   ├── test_demo.py         # 自動テストスクリプト
│   ├── start_demo.sh        # 自動デモ起動スクリプト
│   ├── curl_examples.sh     # プロキシサーバー用cURLサンプル
│   ├── test_mock_server.sh  # モックサーバー単体テスト
│   └── quick_test.sh        # モックサーバークイックテスト
└── tests/                 # テストファイル
    ├── test_adapter_config.py  # アダプター設定テスト
    ├── test_adapters.py         # アダプター機能テスト
    ├── test_app_flask.py
    ├── test_client.py
    ├── test_config.py
    ├── test_converter.py
    └── test_models.py
```

## テスト実行

```bash
# 全テスト実行（87テスト）
python -m pytest tests/ -v

# 特定のテストファイル実行
python -m pytest tests/test_app_flask.py -v      # Flask アプリケーション
python -m pytest tests/test_adapters.py -v       # アダプター機能
python -m pytest tests/test_adapter_config.py -v # アダプター設定

# アダプター関連テストのみ実行
python -m pytest tests/test_adapter*.py -v
```

## アダプター設定

プロキシサーバーは、様々な既存サーバーの入出力形式に対応するため、アダプターアーキテクチャを採用しています。環境変数で簡単に設定できます。

### 基本設定

```bash
# アダプタータイプ（通常は変更不要）
export ADAPTER_TYPE="openai_compatible"

# リクエストフィールドマッピング
export REQUEST_MODEL_FIELD="model"          # モデル名フィールド
export REQUEST_MESSAGES_FIELD="messages"    # メッセージ配列フィールド（必須）
export REQUEST_TEMPERATURE_FIELD="temperature"  # 温度パラメータフィールド
export REQUEST_MAX_TOKENS_FIELD="max_tokens"    # 最大トークン数フィールド
export REQUEST_STREAM_FIELD="stream"            # ストリーミングフラグフィールド
export REQUEST_STOP_FIELD="stop"                # 停止文字列フィールド

# レスポンスフィールドマッピング
export RESPONSE_CONTENT_FIELD="content"         # コンテンツフィールド（必須）
export RESPONSE_FINISH_FIELD="finish_reason"    # 完了理由フィールド
export RESPONSE_MODEL_FIELD="model"             # モデル名フィールド
export RESPONSE_CREATED_FIELD="created"         # 作成時刻フィールド
```

### 高度な設定

```bash
# ストリーミング設定
export STREAMING_FORMAT="sse"              # sse, jsonlines, none
export STREAMING_DATA_PREFIX="data: "      # SSE用データプレフィックス
export STREAMING_DONE_MARKER="[DONE]"      # 完了マーカー

# カスタムヘッダー（JSON形式）
export CUSTOM_HEADERS='{"Authorization": "Bearer your-token", "X-API-Key": "your-key"}'

# デバッグ設定
export ADAPTER_DEBUG="false"               # アダプターデバッグログの有効化
```

### カスタム既存サーバー対応例

#### 例1: ネストしたレスポンス構造

```bash
# 既存サーバーが response.choices[0].message.content 形式でレスポンスを返す場合
export RESPONSE_CONTENT_FIELD="response.choices[0].message.content"
export RESPONSE_FINISH_FIELD="response.choices[0].finish_reason"
```

#### 例2: 異なるフィールド名

```bash
# 既存サーバーが独自のフィールド名を使用する場合
export REQUEST_MODEL_FIELD="engine"         # model → engine
export REQUEST_MESSAGES_FIELD="conversation" # messages → conversation
export REQUEST_TEMPERATURE_FIELD="randomness" # temperature → randomness
export RESPONSE_CONTENT_FIELD="response_text"  # content ← response_text
export RESPONSE_FINISH_FIELD="status"          # finish_reason ← status
```

#### 例3: フィールドの無効化

```bash
# 既存サーバーが特定のフィールドをサポートしない場合
export REQUEST_MAX_TOKENS_FIELD=""          # max_tokensを送信しない
export REQUEST_STOP_FIELD=""                # stopを送信しない
export RESPONSE_MODEL_FIELD=""              # モデル名をレスポンスから取得しない
```

#### 例4: JSON Lines ストリーミング

```bash
# Server-Sent Events以外のストリーミング形式を使用する場合
export STREAMING_FORMAT="jsonlines"
export STREAMING_DATA_PREFIX=""
export STREAMING_DONE_MARKER=""
```

### アダプター設定の検証

設定が正しく適用されているかを確認できます：

```python
from core.adapter_config import AdapterConfig

# 設定情報の表示
info = AdapterConfig.get_adapter_info()
print(info)

# 設定の妥当性チェック
try:
    AdapterConfig.validate()
    print("✓ 設定は有効です")
except Exception as e:
    print(f"✗ 設定エラー: {e}")
```

## 設定可能な環境変数

### サーバー設定

| 環境変数 | デフォルト値 | 説明 |
|----------|-------------|------|
| EXISTING_SERVER_URL | http://localhost:3000/chat | 既存チャットサーバーのURL |
| REQUEST_TIMEOUT | 30 | リクエストタイムアウト（秒） |
| HOST | localhost | サーバーのホスト |
| PORT | 8000 | サーバーのポート |
| DEBUG | false | デバッグモード |
| LOG_LEVEL | INFO | ログレベル |
| DEFAULT_MODEL | gpt-3.5-turbo | デフォルトモデル名 |

### アダプター設定（詳細は上記参照）

| 環境変数 | デフォルト値 | 説明 |
|----------|-------------|------|
| ADAPTER_TYPE | openai_compatible | アダプタータイプ |
| REQUEST_MESSAGES_FIELD | messages | メッセージフィールド（必須） |
| RESPONSE_CONTENT_FIELD | content | レスポンスコンテンツフィールド（必須） |
| STREAMING_FORMAT | sse | ストリーミング形式 |
| CUSTOM_HEADERS | {} | カスタムヘッダー（JSON） |
| ADAPTER_DEBUG | false | アダプターデバッグログ |

## サンプルサーバー

動作確認のため、既存チャットサーバーを模擬するサンプルサーバーが含まれています。

### 機能

- **非ストリーミング・ストリーミング対応**: OpenAI Chat APIプロキシサーバーの両方のモードをテスト可能
- **インテリジェントな応答**: ユーザーメッセージの内容に応じて適切な応答を生成
- **エラーハンドリング**: 無効なリクエストに対する適切なエラー処理
- **ヘルスチェック**: `/health`エンドポイントでサーバーの状態を確認

### 使用方法

```bash
# 単独で起動
python sample_server/mock_chat_server.py

# 自動デモで起動（推奨）
cd sample_server && ./start_demo.sh

# モックサーバー単体テスト
./sample_server/test_mock_server.sh    # 包括的テスト
./sample_server/quick_test.sh          # クイックテスト
```

### API エンドポイント

- `POST /chat` - チャットエンドポイント
- `GET /health` - ヘルスチェック
- `GET /` - API情報表示

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