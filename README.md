# OpenAI Chat API Proxy Server

[![CI](https://github.com/keg66/openai-chat-proxy/workflows/CI/badge.svg)](https://github.com/keg66/openai-chat-proxy/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Security: pip-audit](https://img.shields.io/badge/security-pip--audit-green.svg)](https://github.com/keg66/openai-chat-proxy/actions/workflows/security.yml)
[![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/)

A proxy server that wraps existing chat servers with an OpenAI API `/v1/chat/completions` compatible interface.

## Project Overview

- **Purpose**: Make existing chat servers (POST JSON requests via HTTP, return JSON responses in Server-Sent Events format) compatible with OpenAI API
- **Target Users**: Single-user usage (no need for multiple concurrent connections)
- **Language**: Python 3.9+
- **Framework**: Flask (Phase 1)

## Features

### Supported Endpoints

- `POST /v1/chat/completions` - OpenAI API compatible chat completion endpoint
- `GET /v1/models` - OpenAI API compatible models list endpoint
- `GET /health` - Health check endpoint

### Adapter Architecture

- **Environment Variable Configuration**: Field mapping configurable via environment variables to support various existing servers
- **Nested Field Support**: Supports complex structures like `response.choices[0].message.content`
- **Multiple Streaming Formats**: Supports Server-Sent Events, JSON Lines, and custom formats
- **Custom Headers**: Add authentication or API key headers
- **Field Deactivation**: Configure to not send parameters unsupported by existing servers

### Supported Parameters

**Required**:
- `model`: Model name
- `messages`: Message array (role, content)

**Optional**:
- `temperature`: Temperature parameter (default: 1.0)
- `max_tokens`: Maximum token count
- `stream`: Enable/disable streaming (default: false)
- `stop`: Stop strings

## Quick Start

### Simple Operation Test

Test the proxy server immediately using the included mock server:

```bash
# 1. Virtual environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run automated demo
cd sample_server
./start_demo.sh
```

This automatically starts the mock server and proxy server, then runs comprehensive tests.

### Manual Testing

To start servers individually for testing:

```bash
# Terminal 1: Start mock server
source venv/bin/activate
python sample_server/mock_chat_server.py

# Terminal 2: Start proxy server  
source venv/bin/activate
python app_flask.py

# Terminal 3: Run tests
source venv/bin/activate
python sample_server/test_demo.py
# or
./sample_server/curl_examples.sh
```

## Installation and Setup

### 1. Virtual Environment Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variable Configuration (Optional)

```bash
export EXISTING_SERVER_URL="http://your-chat-server.com/chat"
export REQUEST_TIMEOUT="30"
export HOST="localhost"
export PORT="8000"
export DEBUG="false"
export LOG_LEVEL="INFO"
export DEFAULT_MODEL="gpt-3.5-turbo"
```

### 3. Application Startup

```bash
python app_flask.py
```

The server starts at `http://localhost:8000`.

## Usage Examples

### Non-streaming Chat

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

### Streaming Chat

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

### Models List

```bash
curl http://localhost:8000/v1/models
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Project Structure

```
.
├── app_flask.py           # Flask main application
├── config.py              # Configuration management
├── core/                  # Common business logic
│   ├── __init__.py
│   ├── adapter_config.py  # Adapter configuration management
│   ├── adapters/          # Adapter architecture
│   │   ├── __init__.py
│   │   ├── base.py        # Base adapter class
│   │   ├── configurable.py # Configurable adapter
│   │   └── factory.py     # Adapter factory
│   ├── client.py          # Existing server communication client
│   ├── converter.py       # Data conversion logic
│   └── models.py          # Data structure definitions
├── requirements.txt       # Dependencies
├── requirements/
│   └── flask.txt          # Flask dependencies
├── sample_server/         # Operation test samples
│   ├── mock_chat_server.py  # Mock chat server
│   ├── test_demo.py         # Automated test script
│   ├── start_demo.sh        # Automated demo startup script
│   ├── curl_examples.sh     # cURL samples for proxy server
│   ├── test_mock_server.sh  # Mock server unit test
│   └── quick_test.sh        # Mock server quick test
└── tests/                 # Test files
    ├── test_adapter_config.py  # Adapter configuration tests
    ├── test_adapters.py         # Adapter functionality tests
    ├── test_app_flask.py
    ├── test_client.py
    ├── test_config.py
    ├── test_converter.py
    └── test_models.py
```

## Test Execution

```bash
# Run all tests (104 tests)
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_app_flask.py -v      # Flask application
python -m pytest tests/test_adapters.py -v       # Adapter functionality
python -m pytest tests/test_adapter_config.py -v # Adapter configuration
python -m pytest tests/test_models_api.py -v     # Models API

# Run adapter-related tests only
python -m pytest tests/test_adapter*.py -v

# Run with coverage
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

## CI/CD

This project uses GitHub Actions for continuous integration and security scanning:

### Workflows

- **CI**: Runs on push to main and all pull requests
  - Unit tests across Python 3.9, 3.10, 3.11
  - Integration tests with mock server
  - Code linting with flake8
  - Test coverage reporting

- **PR Check**: Quick validation for pull requests
  - Fast unit test execution
  - Basic syntax validation
  - Configuration validation
  - Changed files summary

- **Security**: Scheduled security scans
  - Dependency vulnerability scanning with `pip-audit`
  - Code security analysis with `bandit`
  - Weekly scheduled runs and on dependency changes

### Status Badges

The README includes status badges showing the current state of:
- [![CI](https://github.com/keg66/openai-chat-proxy/workflows/CI/badge.svg)](https://github.com/keg66/openai-chat-proxy/actions/workflows/ci.yml) - Main CI pipeline status
- [![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/) - Python version requirement
- [![Security: pip-audit](https://img.shields.io/badge/security-pip--audit-green.svg)](https://github.com/keg66/openai-chat-proxy/actions/workflows/security.yml) - Security vulnerability scanning
- [![Code style: flake8](https://img.shields.io/badge/code%20style-flake8-black.svg)](https://flake8.pycqa.org/) - Code quality and style

## Adapter Configuration

The proxy server adopts an adapter architecture to support various existing server input/output formats. Easy configuration via environment variables.

### Basic Configuration

```bash
# Adapter type (usually no change needed)
export ADAPTER_TYPE="openai_compatible"

# Request field mapping
export REQUEST_MODEL_FIELD="model"          # Model name field
export REQUEST_MESSAGES_FIELD="messages"    # Message array field (required)
export REQUEST_TEMPERATURE_FIELD="temperature"  # Temperature parameter field
export REQUEST_MAX_TOKENS_FIELD="max_tokens"    # Max tokens field
export REQUEST_STREAM_FIELD="stream"            # Streaming flag field
export REQUEST_STOP_FIELD="stop"                # Stop string field

# Response field mapping
export RESPONSE_CONTENT_FIELD="content"         # Content field (required)
export RESPONSE_FINISH_FIELD="finish_reason"    # Finish reason field
export RESPONSE_MODEL_FIELD="model"             # Model name field
export RESPONSE_CREATED_FIELD="created"         # Creation time field
```

### Advanced Configuration

```bash
# Streaming configuration
export STREAMING_FORMAT="sse"              # sse, jsonlines, none
export STREAMING_DATA_PREFIX="data: "      # SSE data prefix
export STREAMING_DONE_MARKER="[DONE]"      # Completion marker

# Custom headers (JSON format)
export CUSTOM_HEADERS='{"Authorization": "Bearer your-token", "X-API-Key": "your-key"}'

# Debug configuration
export ADAPTER_DEBUG="false"               # Enable adapter debug logs
```

### Custom Existing Server Support Examples

#### Example 1: Nested Response Structure

```bash
# When existing server returns response in response.choices[0].message.content format
export RESPONSE_CONTENT_FIELD="response.choices[0].message.content"
export RESPONSE_FINISH_FIELD="response.choices[0].finish_reason"
```

#### Example 2: Different Field Names

```bash
# When existing server uses custom field names
export REQUEST_MODEL_FIELD="engine"         # model → engine
export REQUEST_MESSAGES_FIELD="conversation" # messages → conversation
export REQUEST_TEMPERATURE_FIELD="randomness" # temperature → randomness
export RESPONSE_CONTENT_FIELD="response_text"  # content ← response_text
export RESPONSE_FINISH_FIELD="status"          # finish_reason ← status
```

#### Example 3: Field Deactivation

```bash
# When existing server doesn't support specific fields
export REQUEST_MAX_TOKENS_FIELD=""          # Don't send max_tokens
export REQUEST_STOP_FIELD=""                # Don't send stop
export RESPONSE_MODEL_FIELD=""              # Don't get model name from response
```

#### Example 4: JSON Lines Streaming

```bash
# When using streaming formats other than Server-Sent Events
export STREAMING_FORMAT="jsonlines"
export STREAMING_DATA_PREFIX=""
export STREAMING_DONE_MARKER=""
```

### Adapter Configuration Validation

Check if configuration is applied correctly:

```python
from core.adapter_config import AdapterConfig

# Display configuration information
info = AdapterConfig.get_adapter_info()
print(info)

# Validate configuration
try:
    AdapterConfig.validate()
    print("✓ Configuration is valid")
except Exception as e:
    print(f"✗ Configuration error: {e}")
```

## Configurable Environment Variables

### Server Configuration

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| EXISTING_SERVER_URL | http://localhost:3000/chat | Existing chat server URL |
| REQUEST_TIMEOUT | 30 | Request timeout (seconds) |
| HOST | localhost | Server host |
| PORT | 8000 | Server port |
| DEBUG | false | Debug mode |
| LOG_LEVEL | INFO | Log level |
| DEFAULT_MODEL | gpt-3.5-turbo | Default model name |

### Models API Configuration

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| EXISTING_SERVER_MODELS_URL | "" | Existing server models API URL (empty = use config file) |
| MODELS_CONFIG_FILE | models.json | Path to models configuration file |
| MODELS_FALLBACK_ENABLED | true | Enable fallback to config file if server fails |
| MODELS_RESPONSE_MODELS_FIELD | models | Field containing models array in server response |
| MODELS_RESPONSE_ID_FIELD | id | Field containing model ID in server response |
| MODELS_RESPONSE_NAME_FIELD | name | Field containing model name in server response |

### Adapter Configuration (See details above)

| Environment Variable | Default Value | Description |
|---------------------|---------------|-------------|
| ADAPTER_TYPE | openai_compatible | Adapter type |
| REQUEST_MESSAGES_FIELD | messages | Message field (required) |
| RESPONSE_CONTENT_FIELD | content | Response content field (required) |
| STREAMING_FORMAT | sse | Streaming format |
| CUSTOM_HEADERS | {} | Custom headers (JSON) |
| ADAPTER_DEBUG | false | Adapter debug logs |

## Sample Server

A sample server that simulates existing chat servers is included for operation testing.

### Features

- **Non-streaming & Streaming Support**: Test both modes of OpenAI Chat API proxy server
- **Intelligent Responses**: Generate appropriate responses based on user message content
- **Error Handling**: Proper error handling for invalid requests
- **Health Check**: Check server status via `/health` endpoint

### Usage

```bash
# Start standalone
python sample_server/mock_chat_server.py

# Start with automated demo (recommended)
cd sample_server && ./start_demo.sh

# Mock server unit tests
./sample_server/test_mock_server.sh    # Comprehensive test
./sample_server/quick_test.sh          # Quick test
```

### API Endpoints

- `POST /chat` - Chat endpoint
- `GET /models` - Models endpoint (mock)
- `GET /health` - Health check
- `GET /` - API information display

## Models API

The proxy server provides a `/v1/models` endpoint that is compatible with OpenAI's models API. It supports two modes of operation:

### 1. Proxy Mode (Existing Server has Models API)

When the existing server provides a models API:

```bash
# Configure the existing server's models API URL
export EXISTING_SERVER_MODELS_URL="http://your-server.com/models"

# Optional: Configure field mappings if server uses different field names
export MODELS_RESPONSE_MODELS_FIELD="data"  # Field containing models array
export MODELS_RESPONSE_ID_FIELD="model_id"  # Field containing model ID
export MODELS_RESPONSE_NAME_FIELD="model_name"  # Field containing model name
```

The proxy will:
1. Forward requests to the existing server's models API
2. Transform the response to OpenAI format using field mappings
3. Return OpenAI-compatible model list

### 2. Configuration File Mode (No Existing Models API)

When the existing server doesn't have a models API, the proxy loads models from a configuration file:

```bash
# Leave this empty to use config file mode
export EXISTING_SERVER_MODELS_URL=""

# Specify the models configuration file
export MODELS_CONFIG_FILE="models.json"
```

The `models.json` file should contain OpenAI-format model definitions:

```json
{
  "object": "list",
  "data": [
    {
      "id": "custom-model-1",
      "object": "model",
      "created": 1677610602,
      "owned_by": "custom",
      "permission": [],
      "root": "custom-model-1",
      "parent": null
    }
  ]
}
```

### 3. Fallback Behavior

With fallback enabled (default), the proxy will:
1. Try to get models from existing server (if URL configured)
2. Fall back to configuration file if server fails
3. Fall back to default model if config file not found

```bash
# Enable/disable fallback (default: true)
export MODELS_FALLBACK_ENABLED="true"
```

### Example Response

```json
{
  "object": "list",
  "data": [
    {
      "id": "gpt-3.5-turbo",
      "object": "model",
      "created": 1677610602,
      "owned_by": "openai",
      "permission": [],
      "root": "gpt-3.5-turbo",
      "parent": null
    }
  ]
}
```

## Error Handling

- Connection failure to existing server: 503 Service Unavailable
- Request timeout: 504 Gateway Timeout
- Invalid request format: 400 Bad Request
- Other errors: 500 Internal Server Error

## Development & Debugging

### Start in Debug Mode

```bash
export DEBUG="true"
python app_flask.py
```

### Change Log Level

```bash
export LOG_LEVEL="DEBUG"
python app_flask.py
```

## License

All libraries used are commercially available:
- Flask: BSD-3-Clause
- requests: Apache-2.0