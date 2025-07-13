# Substrate - MCP Foundation Layer

Substrate provides the foundation for building production-grade Model Context Protocol (MCP) servers. It includes base classes, documentation, and patterns that ensure consistent, reliable implementations.

## Overview

Substrate is:

- **Foundation Layer**: Base classes and interfaces for all MCP servers
- **Documentation Server**: Serves methodology and architecture documentation
- **Pattern Library**: Common patterns for MCP implementation
- **Passive Component**: Provides structure but no active functionality

## Features

- **Base MCP Class**: Standard patterns for all MCP servers
- **Response Builders**: Structured response creation
- **Error Handling**: Consistent error patterns
- **Progress Tracking**: Real-time operation feedback
- **Sampling Support**: Intelligent assistance integration
- **Documentation Loading**: Flexible documentation system

## Installation

### As a Dependency

For use in your MCP server:

```bash
pip install substrate-mcp
```

Or in your `pyproject.toml`:

```toml
dependencies = [
    "substrate-mcp>=1.0.0",
    "fastmcp>=0.1.0"
]
```

### For Development

```bash
git clone https://github.com/your-org/substrate
cd substrate
pip install -e .
```

## Usage

### Creating an MCP Server

```python
from substrate import SubstrateMCP

class YourServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="your_mcp",
            version="1.0.0",
            description="Your MCP description"
        )
        self._register_tools()
    
    def _register_tools(self):
        @self.tool()
        async def your_tool(ctx, param: str):
            """Tool description"""
            result = await self.process(param)
            return self.create_response(
                success=True,
                data=result
            )
```

### Running Substrate Server

```bash
# Run the documentation server
python -m substrate

# Or with custom docs
SUBSTRATE_DOCS_DIR=/path/to/docs python -m substrate
```

### Docker Usage

```dockerfile
FROM python:3.12-slim

# Copy substrate
COPY substrate /substrate

# Copy your MCP
COPY your-mcp /app

WORKDIR /app

# Install both
RUN pip install -e /substrate && pip install -e .

CMD ["python", "-m", "your_mcp"]
```

## Documentation System

Substrate can serve different documentation sets:

1. **Bundled Docs**: Default examples included with substrate
2. **Custom Docs**: Your own methodology and architecture

### Custom Documentation

Mount your documentation at runtime:

```bash
# Docker
docker run -v ./my-docs:/substrate-docs substrate-mcp

# Local
export SUBSTRATE_DOCS_DIR=./my-docs
python -m substrate
```

Your documentation directory should contain:

- `atlas.md` - Development methodology
- `system-design.md` - System architecture
- `component-map.json` - Component registry

## Base Classes

### SubstrateMCP

The foundation for all MCP servers:

```python
class SubstrateMCP(FastMCP):
    """Base class providing:
    - Response building
    - Error handling
    - Progress tracking
    - Sampling support
    """
```

### Response Patterns

```python
# Success response
return self.create_response(
    success=True,
    data={"result": value},
    message="Operation completed"
)

# Error response
return self.create_error_response(
    error="Clear error message",
    error_type="validation",
    suggestions=["Try this", "Check that"]
)
```

### Progress Tracking

```python
async with self.progress_context("operation") as progress:
    await progress(0.1, "Starting...")
    # ... work ...
    await progress(0.5, "Halfway...")
    # ... more work ...
    await progress(1.0, "Complete!")
```

## Integration with AKAB

Substrate is designed to work with [AKAB](https://github.com/your-org/akab) for A/B testing:

```python
# In your MCP
result = await ctx.call_tool(
    "akab_quick_compare",
    prompt="Your prompt",
    providers=["anthropic_m", "openai_l"]
)
```

## Best Practices

1. **Production-Grade Only**: Real implementations, no mocks
2. **Clear Separation**: Each MCP does one thing well
3. **Explicit Interfaces**: No implicit behaviors
4. **Structured Errors**: Always provide actionable feedback
5. **Clean Logging**: Use stderr, never stdout

## Common Issues

### Stdout Pollution

MCP uses JSON-RPC over stdio. Any print() breaks the protocol.

**Solution**: Log to stderr

```python
logging.basicConfig(stream=sys.stderr)
```

### AsyncIO Conflicts

FastMCP manages its own event loop.

**Solution**: Don't use `asyncio.run()`

```python
def main():
    server = YourServer()
    server.run()  # Let FastMCP handle async
```

## Examples

See the included example documentation:

- `docs/atlas.md` - Example development methodology
- `docs/system-design.md` - Example system architecture
- `docs/component-map.json` - Example component structure

## Contributing

1. Follow the Atlas methodology
2. Ensure all tests pass
3. Update documentation as needed
4. Submit PR with clear description

## License

MIT License - see LICENSE file for details
