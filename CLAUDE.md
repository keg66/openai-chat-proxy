# CLAUDE.md

常に日本語で返答お願いします。

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OpenAI Chat API proxy server that wraps an existing chat server (HTTP JSON POST with Server-Sent Events responses) to provide OpenAI API `/v1/chat/completions` compatible interface.

**Language**: Python 3.11+
**Single user application** - not designed for high concurrency

## Development Strategy

The project follows a phased approach:

- **Phase 1**: Flask prototype for basic functionality and debugging
- **Phase 2**: FastAPI version for performance optimization (if needed)

## Architecture

### Planned Directory Structure
```
chat_proxy/
├── app_flask.py           # Flask main application
├── app_fastapi.py         # FastAPI version (Phase 2)
├── core/                  # Shared business logic
│   ├── converter.py       # Data conversion logic
│   ├── client.py          # Existing server communication
│   └── models.py          # Data structures
└── config.py              # Configuration management
```

### Core Design Principles
- **Separation of concerns**: Framework-specific code separate from shared logic
- **Reusability**: core/ modules can be reused between Flask and FastAPI versions
- **Minimal dependencies**: Keep external packages to minimum

## Key Dependencies

### Phase 1 (Flask):
- Flask 3.0.0
- requests 2.31.0

### Phase 2 (FastAPI):
- FastAPI 0.104.1
- uvicorn 0.24.0  
- httpx 0.25.2

## Commands

### Running the application
```bash
# Phase 1: Flask version
python app_flask.py

# Phase 2: FastAPI version
uvicorn app_fastapi:app --host 0.0.0.0 --port 8000
```

## API Specifications

### Endpoint: `/v1/chat/completions`
OpenAI API compatible endpoint supporting:

**Required parameters**:
- `model`: Model name
- `messages`: Message array (role, content)

**Optional parameters**:
- `temperature`: Temperature parameter (default: 1.0)
- `max_tokens`: Maximum token count
- `stream`: Enable/disable streaming (default: false)
- `stop`: Stop strings

**Response formats**:
- Streaming: Server-Sent Events format
- Non-streaming: JSON format
- Must match OpenAI API structure exactly

### Health check: `/health`
Basic health check endpoint for monitoring

## Core Functionality

### Data Conversion
- **Request conversion**: OpenAI format → existing server format
- **Response conversion**: Existing server format → OpenAI format  
- **Streaming conversion**: SSE → OpenAI chunk format

### Communication
- HTTP communication with existing chat server
- Streaming response handling
- Timeout handling (default: 30 seconds)

## Configuration

Use environment variables for:
- Existing server URL configuration
- Timeout settings
- Debug mode settings

## Error Handling

- Comprehensive error handling for existing server failures
- Appropriate HTTP error responses
- Connection timeout handling
- Detailed logging for debugging

## Implementation Priority

1. **Phase 1 Core**: Basic API compatibility, non-streaming chat, streaming chat, basic error handling
2. **Phase 1 Extensions**: Health check, detailed logging, external configuration
3. **Phase 2**: Performance measurement and FastAPI migration consideration