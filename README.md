# Substrate MCP Foundation

<p align="center">
  <strong>🏗️ Production-grade foundation for building MCP servers</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#installation">Installation</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#documentation">Documentation</a> •
  <a href="#examples">Examples</a> •
  <a href="#contributing">Contributing</a>
</p>

## What is Substrate?

Substrate is a foundation framework for building [Model Context Protocol (MCP)](https://modelcontextprotocol.io) servers. It provides a standardized base class with production-grade features that all MCP servers need, eliminating boilerplate and ensuring consistency.

### Why Substrate?

- **🚀 Quick Start**: Inherit from `SubstrateMCP` and focus on your business logic
- **📦 Batteries Included**: Progress tracking, error handling, sampling emulation
- **🔧 Production Ready**: Built-in timeout prevention and comprehensive error types
- **🎯 Consistent**: Standardized response format across all servers
- **🧩 Extensible**: Easy to add custom tools while maintaining standards

## Features

- **Standardized Base Class**: All servers inherit from `SubstrateMCP`
- **Automatic Tool Registration**: Self-documentation and sampling callback tools
- **Progress Tracking**: Prevent timeouts in long operations
- **Sampling Emulation**: Work around Claude Desktop limitations
- **Error Handling**: Comprehensive error types with suggestions
- **Response Standards**: Consistent format across all servers
- **Type Safety**: Full TypeScript-style type hints
- **Async Support**: Built on modern async/await patterns

## Installation

```bash
# Install from source
git clone https://github.com/ivan-saorin/substrate.git
cd substrate
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Quick Start

Create a minimal MCP server in minutes:

```python
from substrate import SubstrateMCP

class MyServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="myserver",
            version="1.0.0",
            description="My awesome MCP server",
            instructions="Use myserver to do awesome things!"
        )
        self._register_tools()
        
    async def get_capabilities(self):
        """Required: Return server capabilities for self-documentation."""
        return {
            "features": ["feature1", "feature2"],
            "version": self.version
        }
    
    def _register_tools(self):
        """Register your custom tools."""
        
        @self.tool(description="Do something useful")
        async def my_tool(self, ctx, param: str):
            """Tool implementation with progress tracking."""
            # Progress tracking prevents timeouts
            await ctx.progress(0.1, "Starting operation...")
            
            # Your business logic here
            result = await self.do_something(param)
            
            await ctx.progress(1.0, "Complete!")
            
            # Standardized response format
            return self.create_response(
                success=True,
                data={"result": result},
                message="Operation completed successfully"
            )

# Run the server
if __name__ == "__main__":
    server = MyServer()
    server.run()  # FastMCP handles the event loop
```

## Documentation

### Core Components

#### SubstrateMCP Base Class

The foundation for all MCP servers:

```python
from substrate import SubstrateMCP, ValidationError, NotFoundError

class MyServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="myserver",          # Server name (used for tool naming)
            version="1.0.0",          # Semantic versioning
            description="...",        # Human-readable description
            instructions="..."        # Optional LLM instructions
        )
```

#### Progress Tracking

Prevent MCP timeouts during long operations:

```python
async with self.progress_context("operation") as progress:
    await progress(0.1, "Initializing...")
    data = await fetch_data()
    
    await progress(0.5, "Processing...")
    results = await process_data(data)
    
    await progress(0.9, "Finalizing...")
    output = await generate_output(results)
    
    await progress(1.0, "Complete!")
    return output
```

#### Error Handling

Comprehensive error types with user-friendly suggestions:

```python
from substrate import ValidationError, NotFoundError

# Validation errors with field information
if not email.contains("@"):
    raise ValidationError(
        "Invalid email format", 
        field="email",
        suggestions=["Check email format", "Use name@example.com"]
    )

# Not found errors with alternatives
campaign = storage.get(campaign_id)
if not campaign:
    raise NotFoundError(
        "Campaign",                    # Resource type
        campaign_id,                   # Resource ID
        suggestions=[
            "List campaigns with 'list_campaigns'",
            "Check campaign ID format"
        ]
    )
```

#### Sampling Emulation

Request clarification or suggestions from the LLM:

```python
# In your tool implementation
if not constraints and self.sampling_manager.should_request_sampling("constraints"):
    response = self.create_response(
        success=True,
        data={"status": "need_input"},
        message="Would you like me to suggest constraints?"
    )
    
    # Add sampling request
    response["_sampling_request"] = self.sampling_manager.create_request(
        "The user wants to compare prompts. What constraints (max_tokens, "
        "temperature, etc.) would you suggest for this comparison?"
    )
    
    return response
```

#### Response Building

Consistent response format across all tools:

```python
# Success response
return self.create_response(
    success=True,
    data={"results": results},
    message="Operation completed"
)

# Error response (handled automatically by error types)
return self.create_response(
    success=False,
    error="Operation failed",
    suggestions=["Try this", "Or this"]
)

# Paginated response
return self.response_builder.paginated(
    items=campaigns,
    page=1,
    page_size=10,
    total=100,
    message="Found 100 campaigns"
)

# Comparison result (for A/B testing servers)
return self.response_builder.comparison_result(
    results=comparison_results,
    winner="provider_a",
    metrics={"speed": 0.95, "accuracy": 0.87},
    message="Provider A performed best"
)
```

### Standard Tools

Every Substrate server automatically includes:

1. **Self-documentation tool** (named after your server):
   - Returns server capabilities
   - Shows available features
   - Can trigger sampling for guidance

2. **Sampling callback tool** (`{servername}_sampling_callback`):
   - Handles responses from sampling requests
   - Processes LLM suggestions
   - Integrates with sampling flow

## Examples

### Real Implementation: AKAB

[AKAB](https://github.com/ivan-saorin/akab) is a production A/B testing server built on Substrate:

```python
class AKABServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="akab",
            version="2.0.0",
            description="Open-source A/B testing tool for comparing AI outputs"
        )
        # Initialize AKAB-specific components
        self.provider_manager = ProviderManager()
        self.comparison_engine = ComparisonEngine()
        self._register_tools()
```

### Basic Calculator Server

```python
from substrate import SubstrateMCP
import math

class CalculatorServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="calculator",
            version="1.0.0",
            description="Advanced calculator with progress tracking"
        )
        self._register_tools()
    
    async def get_capabilities(self):
        return {
            "operations": ["basic", "scientific", "statistical"],
            "features": ["progress tracking", "error handling"]
        }
    
    def _register_tools(self):
        @self.tool(description="Calculate factorial with progress")
        async def factorial(self, ctx, n: int):
            if n < 0:
                raise ValidationError("Factorial requires non-negative integer", field="n")
            
            result = 1
            async with self.progress_context("factorial") as progress:
                for i in range(1, n + 1):
                    result *= i
                    await progress(i / n, f"Calculating {i}!")
                    
            return self.create_response(
                success=True,
                data={"result": result, "input": n},
                message=f"{n}! = {result}"
            )
```

## Architecture

```
SubstrateMCP (Base Class)
├── FastMCP Integration
├── Standard Tools
│   ├── {servername} (self-documentation)
│   └── {servername}_sampling_callback
├── Response Builder
│   ├── success()
│   ├── error()
│   ├── paginated()
│   └── comparison_result()
├── Progress Tracker
│   └── progress_context()
├── Sampling Manager
│   ├── should_request_sampling()
│   └── create_request()
└── Error Types
    ├── SubstrateError
    ├── ValidationError
    └── NotFoundError
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ivan-saorin/substrate.git
cd substrate

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=substrate

# Run specific test file
pytest tests/test_base.py
```

### Code Quality

```bash
# Format code
black src/
isort src/

# Lint
ruff check src/

# Type checking
mypy src/
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the [Model Context Protocol](https://modelcontextprotocol.io)
- Inspired by production needs in AI agent development
- Special thanks to the MCP community

## Links

- [Documentation](https://github.com/ivan-saorin/substrate/wiki)
- [Examples](https://github.com/ivan-saorin/substrate/tree/main/examples)
- [AKAB Implementation](https://github.com/ivan-saorin/akab)
- [MCP Protocol Docs](https://modelcontextprotocol.io)
