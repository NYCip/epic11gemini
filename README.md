# EPIC V11 - Three Amigos Development Framework

[![CI Pipeline](https://github.com/NYCip/epic11gemini/actions/workflows/ci.yml/badge.svg)](https://github.com/NYCip/epic11gemini/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/NYCip/epic11gemini/actions/workflows/cd.yml/badge.svg)](https://github.com/NYCip/epic11gemini/actions/workflows/cd.yml)
[![Security Scan](https://img.shields.io/badge/security-trivy-green)](https://github.com/aquasecurity/trivy)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

EPIC V11 is a comprehensive AI-powered system featuring multi-agent architecture with PhiData, secure authentication, and advanced risk management capabilities.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        EPIC V11 System                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Frontend   │  │ Control Panel │  │ AGNO Service │        │
│  │   (Next.js)  │  │   (FastAPI)   │  │  (PhiData)   │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │  MCP Server  │  │ Donna Service │  │   Database   │        │
│  │   (Tools)    │  │ (Protection)  │  │ (PostgreSQL) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+
- PostgreSQL with pgvector extension

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/NYCip/epic11gemini.git
   cd epic11gemini
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Run tests**
   ```bash
   ./scripts/test-local.sh
   ```

## 🔄 CI/CD Pipeline

### Continuous Integration
- **Trigger:** Push to master or pull requests
- **Tests:** Frontend, backend, integration, security
- **Build:** Multi-arch Docker images
- **Registry:** GitHub Container Registry (ghcr.io)

### Continuous Deployment
- **Staging:** Automatic on master branch
- **Production:** Tag-based (v*) deployments
- **Rollback:** Automated rollback on failure

### Local Testing
```bash
# Run full CI/CD test locally
./scripts/test-local.sh

# Deploy to environment
./scripts/deploy.sh staging
```

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm install
npm run dev        # Development server
npm run build      # Production build
npm test          # Run tests
npm run lint      # Lint code
```

### Backend Development
```bash
# Control Panel
cd control_panel_backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# AGNO Service
cd agno_service
pip install -r requirements.txt
python -m uvicorn workspace.main:app --reload
```

### Docker Development
```bash
# Build specific service
docker-compose build frontend

# View logs
docker-compose logs -f agno_service

# Run tests in container
docker-compose -f docker-compose.test.yml up
```

## 📦 Services

### Frontend (Next.js)
- **Port:** 3000
- **Features:** React 18, NextAuth, TypeScript, Tailwind CSS
- **Testing:** Jest, React Testing Library, Playwright

### Control Panel Backend (FastAPI)
- **Port:** 8000
- **Endpoints:** /control/*
- **Auth:** JWT-based authentication
- **Database:** PostgreSQL with SQLAlchemy

### AGNO Service (PhiData)
- **Port:** 8000
- **AI Agents:** Board of Directors pattern
- **LLMs:** OpenAI, Anthropic, Google
- **Tools:** MCP integration

### MCP Server
- **Port:** 9000
- **Protocol:** Model Context Protocol
- **Tools:** File operations, web access

### Database
- **PostgreSQL 16** with pgvector extension
- **Redis 7** for caching and messaging

## 🔒 Security

### Authentication
- Multi-factor authentication
- Role-based access control
- Session management

### Emergency Controls
- Edward Override system
- Donna Protection service
- Audit logging

### Security Scanning
- Trivy vulnerability scanning
- Secret detection
- SAST/DAST integration

## 🚀 Deployment

### GitHub Actions Secrets Required

Configure these secrets in your GitHub repository:

```yaml
# Staging Environment
STAGING_SSH_KEY      # SSH key for staging server
STAGING_USER         # SSH username
STAGING_HOST         # Staging server hostname
STAGING_URL          # https://staging.epic.pos.com

# Production Environment  
PRODUCTION_SSH_KEY   # SSH key for production server
PRODUCTION_USER      # SSH username
PRODUCTION_HOST      # Production server hostname
PRODUCTION_URL       # https://epic.pos.com

# Notifications
SLACK_WEBHOOK        # Slack webhook for notifications
```

### Manual Deployment
```bash
# Deploy to staging
ssh user@staging.host
cd /opt/epic11gemini
git pull origin master
docker-compose up -d

# Deploy to production (with tag)
git tag -a v11.0.1 -m "Release v11.0.1"
git push origin v11.0.1
```

## 📊 Monitoring

### Health Endpoints
- Frontend: `https://epic.pos.com/api/auth/providers`
- API: `https://epic.pos.com/health`
- MCP: `http://localhost:9000/health`

### Observability
- **Langfuse:** LLM monitoring and tracing
- **n8n:** Workflow automation
- **Traefik:** API gateway metrics

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`./scripts/test-local.sh`)
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Code Standards
- TypeScript/JavaScript: ESLint + Prettier
- Python: Black + Flake8 + isort
- Commits: Conventional Commits
- Tests: Minimum 80% coverage

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation:** [CLAUDE.md](CLAUDE.md)
- **Issues:** [GitHub Issues](https://github.com/NYCip/epic11gemini/issues)
- **Discussions:** [GitHub Discussions](https://github.com/NYCip/epic11gemini/discussions)

## 🙏 Acknowledgments

- PhiData for the AI agent framework
- Anthropic for Claude AI integration
- The open-source community

---

**EPIC V11** - Building the future of AI-powered systems 🚀