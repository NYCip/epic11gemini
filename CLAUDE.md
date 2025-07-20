# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Information
- **Repository:** epic11gemini
- **Main Branch:** master

## Development Commands

### Frontend (Next.js)
- `cd frontend && npm run dev` - Start development server
- `cd frontend && npm run build` - Build for production
- `cd frontend && npm test` - Run unit tests
- `cd frontend && npm run test:e2e` - Run Playwright e2e tests
- `cd frontend && npm run lint` - Lint code
- `cd frontend && npm run type-check` - TypeScript type checking

### Backend Services
- `docker-compose up -d` - Start all services
- `docker-compose down` - Stop all services
- `docker-compose logs <service>` - View logs for specific service
- `docker-compose build <service>` - Rebuild specific service

### Individual Service Development
- `cd agno_service && python -m uvicorn workspace.main:app --reload` - AGNO service dev
- `cd control_panel_backend && python -m uvicorn app.main:app --reload` - Control panel dev
- `cd mcp_server && python main.py` - MCP server dev

## Architecture Overview

EPIC V11 is a comprehensive AI system with multiple coordinated services:

### Core Services
- **AGNO Service** (`agno_service/`) - Board of Directors AI agents using PhiData framework
- **Control Panel Backend** (`control_panel_backend/`) - FastAPI authentication and system management
- **Frontend** (`frontend/`) - Next.js React dashboard with NextAuth authentication
- **MCP Server** (`mcp_server/`) - Model Context Protocol server for agent tool access
- **Donna Protection Service** (`donna_protection_service/`) - Security and override protection

### Key Components
- **Agent Factory** (`agno_service/workspace/agent_factory.py`) - Creates and configures AI agents
- **Risk Management** (`agno_service/workspace/risk_management.py`) - System risk assessment
- **Board Members** (`agno_service/workspace/board_members/`) - Individual AI agent configurations
- **MCP Tools** (`agno_service/workspace/tools/`) - Tool integrations for agents

### Data Layer
- PostgreSQL with pgvector extension for vector storage
- Redis for caching and message brokering
- Langfuse for LLM observability and monitoring

### Infrastructure
- Traefik reverse proxy with SSL termination
- Docker Compose orchestration
- n8n workflow automation
- Health checks for all services

## Security Architecture
- Edward Override system for emergency halts (`EDWARD_OVERRIDE_STATUS` in Redis)
- Multi-level authentication (NextAuth + JWT)
- Service isolation via Docker networks
- TLS termination at Traefik layer

## Development Notes
- Services communicate via internal Docker network (`epic_network`)
- All services depend on PostgreSQL and Redis health checks
- Environment variables configured via `.env` file
- API endpoints follow `/control` prefix for backend routes
- Frontend uses server-side rendering with authentication middleware