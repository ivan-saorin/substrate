# Atlas - MCP Development Methodology v2.0

Version: 2.0-OS  
Last Updated: 2025-01-20  
Location: substrate/docs/atlas-v2.md

## Purpose

This document defines HOW to build, maintain, and evolve MCP-based systems using the v2.0 feature-based architecture. It demonstrates the methodology through substrate (foundation) and akab (example implementation).

## Core Principles

### 1. Feature-Based Hybrid Architecture

**Definition**: Each server is composed of isolated feature modules with shared components.

**Structure**:
```
server/
├── src/
│   └── server_name/
│       ├── server.py          # <200 lines MCP setup
│       ├── features/          # Business capabilities
│       │   ├── feature_name/
│       │   │   ├── tool.py    # MCP tool registration
│       │   │   ├── handler.py # Business logic
│       │   │   └── prompts.yaml
│       │   └── .../
│       └── shared/            # Cross-cutting concerns
│           ├── models/        # Model registry
│           ├── storage/       # Persistence
│           └── response/      # Standard responses
```

### 2. YAML Everywhere

**Definition**: All configuration, prompts, patterns, and templates are YAML files.

**Rationale**:
- Version control friendly
- No code changes for content updates
- Clear separation of logic and data
- Easy to understand and modify

**Example**:
```yaml
# features/quick_compare/prompts.yaml
version: 1.0
prompts:
  comparison:
    content: |
      Compare responses to: {prompt}
      Focus on: {criteria}
```

### 3. Single Source of Truth

**Definition**: The .env file is the only source for model configuration.

**Implementation**:
- No models.json files
- No hardcoded model mappings
- All servers use substrate ModelRegistry
- Registry reads from environment variables

### 4. Production-Grade Only

**Definition**: Every feature must actually work with real implementations.

**This Means**:
- Real API calls, not mocks
- Actual results, not stubs
- Working features, not placeholders
- Loud failures, not silent errors

## Architecture Overview

### Core Components

1. **substrate** - Foundation layer
   - Provides base functionality
   - Shared components (models, storage, response)
   - Documentation and reference management
   - Workflow navigation system

2. **akab** - A/B Testing Framework (Example Implementation)
   - Demonstrates feature-based architecture
   - Three levels of testing rigor
   - Statistical analysis capabilities
   - Integration with substrate components

3. **krill** - Storage System
   - Secure result storage
   - Campaign and experiment data
   - Implemented as directory structure
   - Archive system for completed work

### Key Architectural Decisions

**ADR-11**: Feature-based hybrid architecture  
**ADR-12**: Prompts as YAML data  
**ADR-13**: Model registry from .env  
**ADR-14**: No backward compatibility  
**ADR-15**: Standard response format  
**ADR-16**: Substrate-level workflow navigation  
**ADR-17**: Self-documenting servers

## Development Workflow

### Creating a New Feature

1. **Define the Feature**
   ```
   features/my_feature/
   ├── __init__.py
   ├── tool.py       # Tool registration
   ├── handler.py    # Business logic
   └── prompts.yaml  # YAML prompts
   ```

2. **Register Tools**
   ```python
   # tool.py
   def register_my_feature_tools(server):
       @server.tool()
       async def my_tool(param: str):
           handler = MyHandler()
           return await handler.process(param)
   ```

3. **Implement Business Logic**
   ```python
   # handler.py
   class MyHandler:
       async def process(self, param: str):
           # Real implementation
           return server.response_builder.success(
               data=result,
               suggestions=[...]
           )
   ```

4. **Define Prompts/Patterns**
   ```yaml
   # prompts.yaml
   version: 1.0
   prompts:
     main:
       content: |
         Process this: {param}
   ```

### Using Substrate Components

All servers should use substrate's shared components:

```python
from substrate.shared.models import ModelRegistry
from substrate.shared.response import ResponseBuilder
from substrate.shared.storage import ReferenceManager

# In your server
self.models = ModelRegistry()
self.response_builder = ResponseBuilder(self)
self.storage = ReferenceManager()
```

## Example: AKAB Implementation

AKAB demonstrates the architecture with real functionality:

### Feature Structure
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

### Integration with Krill
```python
# AKAB stores results in /krill directory
/krill/
├── campaigns/
│   ├── quick/
│   ├── standard/
│   └── experiments/
├── results/
└── archive/
```

## Best Practices

### 1. Feature Isolation
- Each feature completely self-contained
- No dependencies between features
- Shared components only in /shared

### 2. YAML Management
- Version all YAML files
- Include metadata (author, date, effectiveness)
- Use clear, descriptive names

### 3. Error Handling
- Use ResponseBuilder for consistent errors
- Include actionable suggestions
- Never fail silently

### 4. Documentation
- Self-documenting servers (respond to their name)
- Clear tool descriptions
- Examples in docstrings

## Testing Approach

### External Testing Only
- No test code in production
- Test features in isolation
- Use separate test projects

### Integration Testing
- Test workflows between servers
- Verify YAML loading
- Check error scenarios

## Creating Your Own MCP

1. **Start with Substrate**
   ```python
   # Use substrate components
   from substrate.shared.response import ResponseBuilder
   ```

2. **Follow Feature Pattern**
   - Create feature directories
   - Implement handlers
   - Define YAML configurations

3. **Integrate with Others**
   - Use tool calls for integration
   - Follow response format standards
   - Document your tools

## Deployment

### Docker Setup
```dockerfile
FROM python:3.12-slim
WORKDIR /app

# Copy substrate
COPY substrate /substrate

# Copy your server
COPY . /app

# Install dependencies
RUN pip install -e /substrate && pip install -e .

CMD ["python", "-m", "your_server"]
```

### Configuration
- Use .env for API keys and model configuration
- Volume mounts for data persistence
- Environment variables for runtime config

## Extension Points

### Adding New Features
1. Create feature directory
2. Implement handler and tools
3. Add YAML configurations
4. Register in server.py

### Creating New Servers
1. Follow substrate patterns
2. Use shared components
3. Define clear purpose
4. Integrate through tool calls

## Conclusion

The v2.0 architecture provides:
- Clean separation through features
- Configuration through YAML
- Consistent patterns across servers
- Easy extension and maintenance
- Production-grade reliability

This open source release includes substrate (foundation) and akab (example). Use these as templates for building your own cognitive manipulation tools.