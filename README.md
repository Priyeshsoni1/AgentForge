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
