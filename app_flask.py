"""
Flask版 OpenAI Chat API プロキシサーバー
"""
import logging
import json
from flask import Flask, request, Response, jsonify, stream_template_string
from werkzeug.exceptions import BadRequest
from requests.exceptions import RequestException, Timeout, ConnectionError

from config import Config
from core.models import ChatCompletionRequest
from core.converter import DataConverter
from core.client import ExistingServerClient


# ログ設定
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL().upper(), logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
logger = logging.getLogger(__name__)

# 既存サーバークライアントの初期化
existing_client = ExistingServerClient(
    server_url=Config.EXISTING_SERVER_URL(),
    timeout=Config.REQUEST_TIMEOUT()
)

# データコンバーターの初期化
converter = DataConverter()


@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    try:
        server_health = existing_client.health_check()
        return jsonify({
            "status": "healthy" if server_health else "degraded",
            "existing_server": {
                "url": Config.EXISTING_SERVER_URL(),
                "healthy": server_health
            },
            "config": Config.get_config_dict()
        }), 200 if server_health else 503
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI互換のチャット完了エンドポイント"""
    try:
        # リクエストデータの検証
        if not request.is_json:
            return jsonify(DataConverter.create_error_response(
                "Request must be JSON",
                "invalid_request_error"
            )), 400
        
        try:
            request_data = request.get_json()
        except Exception:
            return jsonify(DataConverter.create_error_response(
                "Invalid JSON",
                "invalid_request_error"
            )), 400
        
        if request_data is None:
            return jsonify(DataConverter.create_error_response(
                "Empty request body",
                "invalid_request_error"
            )), 400
        
        # 必須フィールドの検証
        if 'model' not in request_data:
            return jsonify(DataConverter.create_error_response(
                "Missing required parameter: model",
                "invalid_request_error"
            )), 400
        
        if 'messages' not in request_data:
            return jsonify(DataConverter.create_error_response(
                "Missing required parameter: messages",
                "invalid_request_error"
            )), 400
        
        if not isinstance(request_data['messages'], list) or len(request_data['messages']) == 0:
            return jsonify(DataConverter.create_error_response(
                "Messages must be a non-empty array",
                "invalid_request_error"
            )), 400
        
        # ChatCompletionRequestオブジェクトを作成
        try:
            openai_request = ChatCompletionRequest.from_dict(request_data)
        except Exception as e:
            return jsonify(DataConverter.create_error_response(
                f"Invalid request format: {str(e)}",
                "invalid_request_error"
            )), 400
        
        logger.info(f"Processing request: model={openai_request.model}, stream={openai_request.stream}, messages_count={len(openai_request.messages)}")
        
        # 既存サーバー形式に変換
        existing_request = converter.openai_to_existing_server(openai_request)
        
        # ストリーミングの場合
        if openai_request.stream:
            return handle_streaming_request(existing_request, openai_request)
        
        # 非ストリーミングの場合
        return handle_non_streaming_request(existing_request, openai_request)
        
    except Exception as e:
        logger.error(f"Unexpected error in chat_completions: {e}")
        return jsonify(DataConverter.create_error_response(
            "Internal server error",
            "internal_error"
        )), 500


def handle_non_streaming_request(existing_request, openai_request):
    """非ストリーミングリクエストを処理"""
    try:
        # 既存サーバーにリクエスト送信
        server_response = existing_client.send_request_dict(existing_request)
        
        # OpenAI形式に変換
        openai_response = converter.existing_server_to_openai(server_response, openai_request)
        
        # レスポンスを辞書に変換
        response_dict = {
            "id": openai_response.id,
            "object": openai_response.object,
            "created": openai_response.created,
            "model": openai_response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                } for choice in openai_response.choices
            ],
            "usage": {
                "prompt_tokens": openai_response.usage.prompt_tokens,
                "completion_tokens": openai_response.usage.completion_tokens,
                "total_tokens": openai_response.usage.total_tokens
            } if openai_response.usage else None
        }
        
        logger.info(f"Non-streaming response sent: {len(openai_response.choices[0].message.content)} characters")
        return jsonify(response_dict)
        
    except ConnectionError as e:
        logger.error(f"Connection error: {e}")
        return jsonify(DataConverter.create_error_response(
            "Failed to connect to existing server",
            "service_unavailable"
        )), 503
        
    except Timeout as e:
        logger.error(f"Timeout error: {e}")
        return jsonify(DataConverter.create_error_response(
            "Request to existing server timed out",
            "timeout"
        )), 504
        
    except RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify(DataConverter.create_error_response(
            f"Error from existing server: {str(e)}",
            "upstream_error"
        )), 502


def handle_streaming_request(existing_request, openai_request):
    """ストリーミングリクエストを処理"""
    def generate_stream():
        try:
            chunk_id = f"chatcmpl-{openai_request.model}-stream"
            
            # 開始チャンクを送信
            start_chunk = DataConverter.create_streaming_chunk(
                content="",
                finish_reason="start",
                model=openai_request.model,
                chunk_id=chunk_id
            )
            yield DataConverter.format_sse_chunk(start_chunk)
            
            # 既存サーバーからのストリーミングレスポンスを処理
            for server_data in existing_client.send_streaming_request_dict(existing_request):
                # サーバーデータをチャンクに変換
                content = server_data.get("content", "")
                finish_reason = server_data.get("finish_reason")
                
                chunk = DataConverter.create_streaming_chunk(
                    content=content,
                    finish_reason=finish_reason,
                    model=openai_request.model,
                    chunk_id=chunk_id
                )
                
                yield DataConverter.format_sse_chunk(chunk)
                
                # 完了時はループを終了
                if finish_reason and finish_reason != "start":
                    break
            
            # 最終チャンクを送信
            yield "data: [DONE]\n\n"
            
            logger.info(f"Streaming response completed for model: {openai_request.model}")
            
        except ConnectionError as e:
            logger.error(f"Streaming connection error: {e}")
            error_chunk = {
                "error": {
                    "message": "Failed to connect to existing server",
                    "type": "service_unavailable"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            
        except Timeout as e:
            logger.error(f"Streaming timeout error: {e}")
            error_chunk = {
                "error": {
                    "message": "Request to existing server timed out",
                    "type": "timeout"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            error_chunk = {
                "error": {
                    "message": f"Streaming error: {str(e)}",
                    "type": "internal_error"
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
    
    return Response(
        generate_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }
    )


@app.errorhandler(400)
def bad_request(error):
    """400エラーハンドラー"""
    return jsonify(DataConverter.create_error_response(
        "Bad request",
        "invalid_request_error"
    )), 400


@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラー"""
    return jsonify(DataConverter.create_error_response(
        "Not found",
        "not_found_error"
    )), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラー"""
    logger.error(f"Internal server error: {error}")
    return jsonify(DataConverter.create_error_response(
        "Internal server error",
        "internal_error"
    )), 500


if __name__ == '__main__':
    try:
        # 設定の検証
        Config.validate()
        
        logger.info("Starting Chat Proxy Server (Flask)")
        logger.info(f"Configuration: {Config.get_config_dict()}")
        
        # 既存サーバーのヘルスチェック
        if existing_client.health_check():
            logger.info("Existing server is healthy")
        else:
            logger.warning("Existing server health check failed - server may not be available")
        
        # Flaskアプリケーションを起動
        app.run(
            host=Config.HOST(),
            port=Config.PORT(),
            debug=Config.DEBUG()
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        exit(1)