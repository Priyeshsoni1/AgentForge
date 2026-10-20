# AgentForge

A production-oriented multi-tool AI agent built with Python,
FastAPI, LangGraph, and OpenRouter.

## Current Features

- FastAPI application
- Application configuration
- Health check endpoint
- Interactive API documentation

## Local Development

Install dependencies:

```powershell
uv sync --extra dev
```

Run the application:

```powershell
uv run uvicorn agentforge.main:app --reload --app-dir src
```

API documentation: http://127.0.0.1:8000/docs

Health check: http://127.0.0.1:8000/health

## Phase 3: Custom Tools

- Tavily-powered web search
- AST-based arithmetic calculator
- Docker-isolated Python execution
- Workspace-restricted file reader
- HTTPS REST API caller with host allowlisting
- Unit tests for calculator, file access, and URL validation

## Run Tests

```powershell
uv run pytest -v
```

## Phase 4: LangGraph Agent

- Stateful ReAct workflow using LangGraph StateGraph
- OpenRouter LLM with tool-calling support
- Five integrated custom tools
- Conditional routing between model and tool nodes
- Execution recursion limit
- Agent API at POST /agent/run
- Automated agent endpoint tests

## Phase 5: Streaming API

- Server-Sent Events (SSE) for agent execution
- POST /agent/run/stream
- Public tool-start and tool-completion events
- Final answer and error events
- Client-disconnect cancellation handling
- Automated streaming endpoint tests

## Phase 6: PostgreSQL Persistence

- Supabase PostgreSQL integration
- LangGraph AsyncPostgresSaver checkpoints
- Persistent conversation messages
- Thread-based conversation continuity
- Shared state across normal and streaming endpoints
- Unit tests isolated from the external database

### Continue a Conversation

Send the same `thread_id` with each request to
continue the same conversation. Use a different ID
for a separate conversation.

## Phase 7: Security and Reliability

- API-key authentication
- Per-owner rate limiting
- Redis-backed shared rate limiting
- PostgreSQL conversation ownership
- Protected agent and LLM endpoints
- Request validation and safe public errors
- Security and rate-limiter tests

### Authentication

Protected endpoints require the `X-API-Key` header.

Configure `APP_API_KEYS` in `.env` as a JSON mapping
of owner IDs to strong API keys.

Production deployments require PostgreSQL, Redis,
and API-key configuration.
