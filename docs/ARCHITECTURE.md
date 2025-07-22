# Atlas Architecture Documentation

## Overview

Atlas is a multi-service MCP (Model Context Protocol) system with a shared substrate foundation. The architecture consists of:

1. **Substrate** - The foundation layer providing shared components
2. **Service Layers** - Independent services built on substrate:
   - **AKAB** - A/B Testing Framework with scientific rigor
   - **Synapse** - Prompt enhancement and optimization
   - **Tloen** - Testing and orchestration
   - **Uqbar** - Knowledge and documentation management

## Directory Structure

```
atlas/
├── substrate/          # Shared foundation layer
│   ├── src/
│   │   └── substrate/
│   │       ├── shared/     # Shared components
│   │       │   ├── api/        # ClearHermes API wrapper
│   │       │   ├── models/     # Model registry
│   │       │   ├── prompts/    # Prompt management
│   │       │   ├── response/   # Response builders
│   │       │   └── storage/    # Reference management
│   │       └── features/   # Substrate-specific features
│   ├── Dockerfile
│   └── requirements.txt
│
├── akab/              # A/B Testing service
│   ├── src/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── synapse/           # Prompt enhancement service
├── tloen/             # Testing service
└── uqbar/             # Documentation service
```

## Building Services

### 1. Substrate First

Substrate must be built before any dependent services:

```bash
cd atlas/substrate
docker build -t substrate-mcp:latest .
```

### 2. Individual Services

Each service has its own Dockerfile that:
- Copies substrate into the container
- Installs substrate as a dependency
- Adds service-specific code

Example for AKAB:
```bash
cd atlas/akab
docker build -t akab-mcp:latest -f Dockerfile ..
```

## Dependency Management

### Substrate Dependencies

Substrate uses `requirements.txt` for its core dependencies:
- `fastmcp` - MCP server framework
- `pyyaml` - YAML configuration
- `anthropic`, `openai`, `google-generativeai` - LLM providers (optional)
- `numpy`, `scipy` - Scientific computing (for services like AKAB)

### Service Dependencies

Each service uses `pyproject.toml` and should:
1. **NOT** include hardcoded paths to substrate
2. Install substrate from the container path: `/substrate`
3. Add service-specific dependencies

Example `pyproject.toml`:
```toml
[project]
dependencies = [
    "fastmcp>=0.1.0",
    # Service-specific deps
]
```

## Docker Build Strategy

### Multi-Stage Builds

For production optimization, use multi-stage builds:

```dockerfile
# Builder stage
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Production stage
FROM python:3.12-slim
COPY --from=builder /root/.local /root/.local
# ... rest of Dockerfile
```

### Build Context

When building services that depend on substrate, use the parent directory as context:

```dockerfile
# akab/Dockerfile
# Copy substrate first
COPY substrate /substrate

# Copy service code
COPY akab /app

# Install dependencies
RUN cd /substrate && pip install -e .
RUN pip install -e .
```

Build command:
```bash
docker build -t service-name -f service/Dockerfile .
```

## Environment Variables

### Common Variables

All services should support:
- `LOG_LEVEL` - Logging level (default: INFO)
- `PYTHONUNBUFFERED=1` - For proper logging in containers
- `MCP_TRANSPORT=stdio` - MCP transport method

### API Keys

For services using LLM providers:
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GROQ_API_KEY`

### Model Definitions (for AKAB Level 3)

```env
# Model definitions for scrambling
ANTHROPIC_XS_MODEL=claude-3-haiku-20240307
ANTHROPIC_S_MODEL=claude-3-5-haiku-20241022
# ... etc
```

## Shared Components (Substrate)

### 1. Model Registry

```python
from substrate.shared.models import get_model_registry

registry = get_model_registry()
model = registry.get("anthropic_xl")
```

### 2. ClearHermes API

```python
from substrate.shared.api import ClearHermes

hermes = ClearHermes()
result = await hermes.complete(model, prompt)
```

### 3. Response Builder

```python
from substrate.shared.response import ResponseBuilder

builder = ResponseBuilder("service-name")
return builder.success(data={...})
```

### 4. Reference Manager

```python
from substrate.shared.storage import ReferenceManager

manager = ReferenceManager()
ref = await manager.create_ref("name", content)
```

## Best Practices

### 1. Dependency Isolation

- Each service should gracefully handle missing optional dependencies
- Use try/except blocks for imports that might not be available
- Provide clear error messages when required dependencies are missing

### 2. Configuration

- Use environment variables for configuration
- Provide sensible defaults
- Document all required environment variables

### 3. Logging

- Use structured logging with service name prefix
- Log to stderr for Docker compatibility
- Include request IDs for tracing

### 4. Error Handling

- Use the ResponseBuilder for consistent error responses
- Include helpful error messages and suggestions
- Log errors with full stack traces

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure substrate is installed first in Dockerfile
   - Check that all dependencies are in requirements.txt/pyproject.toml
   - Verify Docker build context includes all needed directories

2. **Path Issues**
   - Don't use Windows paths in Docker containers
   - Use relative imports within services
   - Install packages in editable mode (`pip install -e .`)

3. **API Key Errors**
   - Check that .env file is mounted or env vars are set
   - Verify API keys are valid
   - Some services may work without all providers configured

### Rebuilding After Changes

When substrate changes affect multiple services:

1. Rebuild substrate first
2. Rebuild dependent services in order
3. Test each service independently
4. Update version tags if needed

## Future Considerations

1. **Versioning**: Consider semantic versioning for substrate
2. **CI/CD**: Automate builds when substrate changes
3. **Testing**: Add integration tests between services
4. **Monitoring**: Add health checks and metrics
