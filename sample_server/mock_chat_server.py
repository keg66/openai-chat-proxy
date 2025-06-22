#!/usr/bin/env python3
"""
Mock chat server for operation testing

Simulates existing chat server behavior and is used for testing 
the OpenAI Chat API proxy server
"""
import json
import time
import random
from flask import Flask, request, Response, jsonify

app = Flask(__name__)

# Sample responses
SAMPLE_RESPONSES = [
    "Hello! Is there anything I can help you with?",
    "Yes, I'll answer that.",
    "That's an interesting question! Let me explain in detail.",
    "Let's think about that.",
    "Understood. Here's how it works:",
    "Hello! How can I help you today?",
    "That's an interesting question. Let me think about it.",
    "I'd be happy to help you with that.",
    "Here's what I think about this topic:",
    "Great question! Here's my response:",
]

def generate_response_content(user_message: str) -> str:
    """Generate response based on user message"""
    # Simple response logic
    message_lower = user_message.lower()
    
    if "hello" in message_lower or "こんにちは" in message_lower:
        return "Hello! How are you? Please let me know if there's anything I can help you with."
    elif "thank" in message_lower or "ありがとう" in message_lower:
        return "You're welcome! Please feel free to ask if you have any other questions."
    elif "weather" in message_lower or "天気" in message_lower:
        return "I'm sorry, but I cannot provide real-time weather information. Please check your local weather service."
    elif "python" in message_lower:
        return "Python is a wonderful programming language! It's simple, readable, and used in many fields."
    elif "test" in message_lower or "テスト" in message_lower:
        return "This is a response from the test mock server. The proxy server is working properly!"
    else:
        # Random sample response
        base_response = random.choice(SAMPLE_RESPONSES)
        return f"{base_response}\n\nI'll respond to your message: '{user_message}'."

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Chat endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid request"}), 400
        
        model = data.get('model', 'mock-model')
        messages = data.get('messages', [])
        stream = data.get('stream', False)
        temperature = data.get('temperature', 1.0)
        
        if not messages:
            return jsonify({"error": "No messages provided"}), 400
        
        # Get the last user message
        user_message = ""
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        # Generate response
        response_content = generate_response_content(user_message)
        
        if stream:
            return handle_streaming_response(response_content, model)
        else:
            return handle_non_streaming_response(response_content, model)
            
    except Exception as e:
        app.logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

def handle_non_streaming_response(content: str, model: str):
    """Handle non-streaming response"""
    # Simulate processing time
    time.sleep(random.uniform(0.5, 1.5))
    
    response = {
        "content": content,
        "finish_reason": "stop",
        "model": model,
        "created": int(time.time())
    }
    
    return jsonify(response)

def handle_streaming_response(content: str, model: str):
    """Handle streaming response"""
    def generate_stream():
        # Split string into words
        words = content.split()
        
        # Start chunk
        yield f"data: {json.dumps({'content': '', 'finish_reason': None, 'model': model})}\n\n"
        
        # Stream word by word
        current_content = ""
        for i, word in enumerate(words):
            # Short delay between words
            time.sleep(random.uniform(0.1, 0.3))
            
            current_content += word + " "
            chunk_data = {
                "content": word + " ",
                "finish_reason": None,
                "model": model
            }
            yield f"data: {json.dumps(chunk_data, ensure_ascii=False)}\n\n"
        
        # Final chunk
        final_chunk = {
            "content": "",
            "finish_reason": "stop",
            "model": model
        }
        yield f"data: {json.dumps(final_chunk)}\n\n"
        yield "data: [DONE]\n\n"
    
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

@app.route('/models', methods=['GET'])
def list_models():
    """Mock models endpoint"""
    return jsonify({
        "models": [
            {
                "id": "mock-model-1",
                "name": "Mock Model 1",
                "created": 1677610602,
                "owned_by": "mock-server"
            },
            {
                "id": "mock-model-2", 
                "name": "Mock Model 2",
                "created": 1677610602,
                "owned_by": "mock-server"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo (Mock)",
                "created": 1677610602,
                "owned_by": "mock-server"
            }
        ]
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Mock Chat Server",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat",
            "models": "/models",
            "health": "/health"
        }
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Mock Chat Server",
        "description": "Mock server for testing OpenAI Chat API proxy server",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health"
        },
        "usage": {
            "chat_request": {
                "method": "POST",
                "url": "/chat",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "model": "mock-model",
                    "messages": [
                        {"role": "user", "content": "Hello!"}
                    ],
                    "stream": False,
                    "temperature": 1.0
                }
            }
        }
    })

if __name__ == '__main__':
    print("🚀 Starting Mock Chat Server...")
    print("📍 Server will be available at: http://localhost:3000")
    print("🔗 Chat endpoint: http://localhost:3000/chat")
    print("💓 Health check: http://localhost:3000/health")
    print("📚 API info: http://localhost:3000/")
    print("\n💡 This server simulates an existing chat server for testing the OpenAI Chat API proxy.")
    print("🛑 Press Ctrl+C to stop the server\n")
    
    app.run(
        host='localhost',
        port=3000,
        debug=False,
        threaded=True
    )