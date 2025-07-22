# System Design - MCP v2.0 Architecture

Version: 2.0-OS  
Last Updated: 2025-01-20  
Location: substrate/docs/system-design-v2.md

## Overview

This document describes the v2.0 architecture for building MCP-based systems using feature-based hybrid architecture. It demonstrates the patterns through substrate (foundation layer) and akab (example implementation).

## Core Components

### 1. Substrate - Foundation Layer

**Type**: Core Framework  
**Purpose**: Provides base functionality and shared components for MCP servers

**Features**:
- `documentation` - System and component documentation
- `references` - Reference content management  
- `execution` - Pattern execution engine
- `workflow_navigation` - Guided workflow system

**Shared Components**:
- `ModelRegistry` - Loads models from .env
- `ResponseBuilder` - Standardized responses
- `ReferenceManager` - Content storage
- `PromptLoader` - YAML prompt loading
- `ClearHermes` - API client abstraction

### 2. AKAB - A/B Testing Framework (Example Implementation)

**Type**: Standalone Server  
**Purpose**: Demonstrates feature-based architecture with real functionality

**Features**:
- `quick_compare` - Level 1: No blinding, immediate results
- `campaigns` - Level 2: Execution blinding, unlockable
- `experiments` - Level 3: Triple blinding, statistical significance
- `reporting` - Cost analysis and campaign listing

**Core Components**:
- `hermes` - Blinded API execution
- `laboratory` - Test execution engine
- `vault` - Result storage and archiving

### 3. Krill - Storage System

**Type**: Directory Structure  
**Purpose**: Secure storage for test results and experimental data

**Structure**:
```
/krill/
├── campaigns/        # All campaign levels
│   ├── quick/       # Level 1 results
│   ├── standard/    # Level 2 campaigns
│   └── experiments/ # Level 3 campaigns
├── results/         # Raw execution data
└── archive/         # Completed work
```

## Architecture Patterns

### Feature-Based Hybrid Architecture

Every server follows this structure:

```
server/
├── src/
│   └── server_name/
│       ├── server.py              # <200 lines
│       ├── features/
│       │   ├── feature1/
│       │   │   ├── tool.py        # Tool registration
│       │   │   ├── handler.py     # Business logic
│       │   │   └── prompts.yaml   # YAML prompts
│       │   └── feature2/
│       └── shared/
│           └── (imported from substrate)
```

### YAML-First Configuration

All prompts and patterns are externalized to YAML:

```yaml
# Example: features/quick_compare/prompts.yaml
version: 1.0
prompts:
  comparison:
    content: |
      Compare the following responses:
      Prompt: {prompt}
      
      Focus on these criteria:
      - {criteria}
```

### Model Configuration

Models are configured via environment variables:

```bash
# .env file
ANTHROPIC_XS=claude-3-haiku-20240307
ANTHROPIC_S=claude-3-5-haiku-20241022
ANTHROPIC_M=claude-3-5-sonnet-20241022
# ... etc
```

## Integration Architecture

### Standard Response Format

All tools return consistent responses:

```python
{
    "data": {...},           # Tool-specific data
    "metadata": {
        "server": "akab",
        "timestamp": 1234567
    },
    "suggestions": [         # Next steps
        {
            "tool": "next_tool",
            "reason": "Why to use it",
            "params": {...}
        }
    ],
    "message": "Operation complete"
}
```

### Self-Documenting Servers

Every server responds to its own name with documentation:

```python
# Call "substrate" → Get substrate documentation
# Call "akab" → Get AKAB documentation
```

## Implementation Example: AKAB

AKAB demonstrates the architecture patterns:

### Feature Organization
```
akab/
├── features/
│   ├── quick_compare/     # Level 1 testing
│   ├── campaigns/         # Level 2 testing  
│   ├── experiments/       # Level 3 testing
│   └── reporting/         # Cost and results
└── core/
    ├── hermes/           # API abstraction
    ├── laboratory/       # Execution engine
    └── vault/            # Result storage
```

### Using Substrate Components

```python
# In akab/server.py
from substrate.shared.models import ModelRegistry
from substrate.shared.response import ResponseBuilder

class AKABServer:
    def __init__(self):
        self.models = ModelRegistry()
        self.response_builder = ResponseBuilder(self)
```

## Deployment

### Docker Setup

Build from root directory containing all servers:

```dockerfile
# substrate/Dockerfile
FROM python:3.12-slim
WORKDIR /app

# Copy substrate
COPY . /app

# Install dependencies
RUN pip install -e .

CMD ["python", "-m", "substrate"]
```

```dockerfile
# akab/Dockerfile  
FROM python:3.12-slim
WORKDIR /app

# Copy substrate first
COPY substrate /substrate

# Copy AKAB
COPY akab /app

# Install both
RUN pip install -e /substrate && pip install -e .

CMD ["python", "-m", "akab"]
```

### Environment Configuration

```yaml
# docker-compose.yml
services:
  substrate:
    build:
      context: .
      dockerfile: substrate/Dockerfile
    environment:
      - PYTHONUNBUFFERED=1
      
  akab:
    build:
      context: .
      dockerfile: akab/Dockerfile
    env_file: ./akab/.env
    volumes:
      - ./krill:/krill
    depends_on:
      - substrate
```

## Creating Your Own MCP

### 1. Project Structure

```
your-mcp/
├── src/
│   └── your_mcp/
│       ├── server.py
│       ├── features/
│       │   └── your_feature/
│       └── __main__.py
├── Dockerfile
├── pyproject.toml
└── README.md
```

### 2. Use Substrate Components

```python
# your_mcp/server.py
from fastmcp import FastMCP
from substrate.shared.response import ResponseBuilder
from substrate.shared.models import ModelRegistry

mcp = FastMCP("your_mcp")
response_builder = ResponseBuilder(mcp)
models = ModelRegistry()
```

### 3. Implement Features

```python
# features/your_feature/tool.py
def register_your_feature_tools(mcp, response_builder):
    @mcp.tool()
    async def your_tool(param: str):
        handler = YourHandler()
        result = await handler.process(param)
        return response_builder.success(
            data=result,
            message="Process complete"
        )
```

## Best Practices

### 1. Feature Independence
- Each feature self-contained
- No cross-feature dependencies
- Shared code only in substrate

### 2. YAML Management
- All prompts in YAML files
- Version control friendly
- Include metadata

### 3. Error Handling
- Use ResponseBuilder for errors
- Include suggestions
- Fail loudly, not silently

### 4. Testing
- External test scripts only
- No test code in production
- Test each feature in isolation

## Extension Points

### Adding Features
1. Create feature directory
2. Implement handler
3. Add YAML files
4. Register tools

### Adding Servers
1. Follow substrate patterns
2. Use shared components
3. Define clear purpose
4. Document all tools

## Conclusion

The v2.0 architecture provides:
- Clean separation of concerns
- Reusable components
- YAML-based configuration
- Easy testing and extension
- Production-grade patterns

Use substrate as your foundation and akab as an implementation example to build your own MCP servers.