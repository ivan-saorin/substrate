# System Design - MCP Architecture

Version: 1.0-OS  
Last Updated: 2025-01-13  
Location: substrate/docs/system-design.md

## Overview

This document provides a reference architecture for building MCP-based systems. It demonstrates how to structure multiple MCPs that work together while maintaining clean separation of concerns.

## Design Constraints

- **Single user**: No multi-tenancy concerns
- **Dockerized**: All MCPs run in containers
- **Remote**: Accessed via MCP protocol
- **Production-grade**: No tests in code, only working solutions

## CRITICAL: Production-Grade Means ACTUALLY WORKING

⚠️ **PRODUCTION-GRADE DEFINITION** ⚠️

Production-grade means:
1. **ACTUALLY EXECUTES** - Makes real API calls, processes real data
2. **REAL RESULTS** - Returns actual LLM responses, not mocks or stubs
3. **WORKING FEATURES** - If it says "A/B testing," it ACTUALLY compares models
4. **NO PLACEHOLDERS** - Every feature listed must be fully implemented
5. **NO SILENT FAILURES** - If something fails, it must fail loudly

**Examples of NOT Production-Grade:**
- Silent ImportError catching that makes features "disappear"
- Marking tests as "successful" with empty responses
- Returning zero metrics when execution failed
- "Mock" implementations that go through motions without doing work

**The Test:** If you claim akab does A/B testing, you should see:
- REAL API calls to Anthropic/OpenAI
- ACTUAL responses with content
- REAL metrics (tokens used, costs, execution times)
- ACTUAL statistical analysis of real data

If any of these are fake, mocked, or silently failing, it's NOT production-grade!

## Core Architecture Components

### 1. Substrate - Foundation Layer

**Purpose**: Provides base classes, interfaces, and documentation for all MCPs.

**Key Features**:
- Base MCP class with standard patterns
- Response builders and error handling
- Progress tracking and sampling support
- Documentation server capabilities
- HermesExecutor interface for execution strategies

**No Active Functionality**: Substrate is passive - it provides structure but doesn't implement business logic.

### 2. AKAB - A/B Testing Framework

**Purpose**: Scientific A/B testing and model comparison with multiple levels of rigor.

**Three Testing Levels**:
1. **Level 1 - Quick Compare**: No blinding, immediate results, for exploration
2. **Level 2 - Campaign**: Execution blinding, unlockable, for standard A/B tests
3. **Level 3 - Experiment**: Complete blinding, statistical significance required

**Key Features**:
- Real API calls to LLM providers
- Statistical analysis with trimmed means
- Dynamic success criteria and winner selection
- Cost tracking and reporting
- Secure storage in `/krill/` directory
- Fire-and-forget scrambling for Level 3
- Unified unlock and archiving system

### 3. Krill - Results Storage

**Purpose**: Secure storage for test results and experimental data.

**Implementation**: Currently implemented as a directory structure within AKAB:
```
/krill/
├── scrambling/      # Session-based model mappings
├── campaigns/       # All campaign levels
│   ├── quick/       # Level 1 results
│   ├── standard/    # Level 2 campaigns
│   └── experiments/ # Level 3 campaigns
├── experiments/     # Experiment definitions
├── results/         # Raw execution data
└── archive/         # Completed work
    └── <id>/
        ├── blinded/     # State before unlock
        ├── clear/       # State after unlock
        └── metadata.json
```

## Implementation Patterns

### MCP Structure

Every MCP should follow this structure:
```python
from substrate import SubstrateMCP

class YourServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="your_mcp",
            version="1.0.0",
            description="What this MCP does"
        )
        self._setup()
        self._register_tools()
```

### Tool Registration

```python
def _register_tools(self):
    @self.tool()
    async def your_tool(ctx, param: str):
        """Tool description"""
        try:
            result = await self.process(param)
            return self.create_response(
                success=True,
                data=result
            )
        except Exception as e:
            return self.create_error_response(
                error=str(e),
                suggestions=["Try X", "Check Y"]
            )
```

### Clear Interfaces

```python
# In substrate
class HermesExecutor(ABC):
    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        pass

# In akab
class BlindedHermes(HermesExecutor):
    """Implementation with model ID blinding"""
    
# In your MCP
class YourExecutor(HermesExecutor):
    """Your custom execution strategy"""
```

## Critical Implementation Details

### MCP Communication Protocol (CRITICAL)

⚠️ **STDOUT MUST BE PURE JSON** ⚠️

When running as an MCP server, everything printed to stdout must be valid JSON. This is a CRITICAL requirement that gets violated repeatedly.

**The Problem:**
- MCP servers communicate via JSON-RPC over stdio
- ANY non-JSON output to stdout breaks the protocol
- Common culprits: `print()` statements, logging to stdout, debug output

**Solution:**
```python
# CORRECT - Use proper logging
import logging
import sys

logger = logging.getLogger(__name__)

# Configure logging to stderr (not stdout!)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # CRITICAL: Use stderr, not stdout!
)

# Now safe to log
logger.info("Processing item")
logger.error(f"Error occurred: {e}", exc_info=True)
```

### MCP Server Implementation Pattern

#### Server Entry Point (CRITICAL)
**NEVER use asyncio.run() in MCP servers!** FastMCP manages its own event loop.

```python
# CORRECT __main__.py pattern:
import sys
from .server import YourServer

def main():
    """Main entry point"""
    try:
        server = YourServer()
        server.run()  # FastMCP handles async internally
    except KeyboardInterrupt:
        print("\nShutting down...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Module Import Safety
**NEVER create instances at module import time!**

```python
# WRONG - in server.py:
server = MyServer()  # Creates at import time!

# CORRECT - create only when running:
def main():
    server = MyServer()
    server.run()
```

## Docker Build Patterns

### Dockerfile Template for MCPs

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# System dependencies if needed
RUN apt-get update && apt-get install -y \
    gcc && rm -rf /var/lib/apt/lists/*

# Copy substrate first (with docs!)
COPY substrate /substrate

# Copy your MCP
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -e /substrate && \
    pip install --no-cache-dir -e .

# Create data directory
RUN mkdir -p /data

# Environment
ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/data

CMD ["python", "-m", "your_mcp"]
```

### Build Context (CRITICAL)

All Docker builds MUST be run from the root directory containing all MCPs:
```bash
# From system root
docker build -t your-mcp -f your-mcp/Dockerfile .
```

### Docker Compose Configuration

```yaml
services:
  substrate:
    build:
      context: .
      dockerfile: substrate/Dockerfile
    volumes:
      - ./custom-docs:/substrate-docs:ro  # Optional
      
  akab:
    build:
      context: .
      dockerfile: akab/Dockerfile
    env_file: ./akab/.env
    volumes:
      - ./krill:/krill
    depends_on:
      - substrate
      
  your-mcp:
    build:
      context: .
      dockerfile: your-mcp/Dockerfile
    environment:
      - YOUR_CONFIG=value
    depends_on:
      - substrate
```

## MCP Advanced Patterns

### 1. Simulated Sampling for Intelligent Assistance

Since Claude Desktop doesn't support native sampling, we emulate it:

```python
# When help is needed, inject _sampling_request in response:
response = self.create_response(
    data={"status": "need_constraints"},
    message="Would you like constraint suggestions?",
    _sampling_request=self.sampling_manager.create_request(
        "User wants to A/B test X. Suggest appropriate constraints.",
        context={"prompt": prompt, "providers": providers}
    )
)

# Claude processes and calls back:
tool_name_sampling_callback(request_id="uuid", response="I suggest...")
```

### 2. Response Annotations

```python
response = self.create_response(
    data=analysis_results,
    annotations={
        "priority": 0.9,           # 0-1, importance level
        "audience": ["user"],      # Who sees this
        "tone": "confident",       # How to present
        "visualization": "chart"   # Preferred display format
    }
)
```

### 3. Progress Tracking

```python
async with self.progress_context("operation_name") as progress:
    await progress(0.1, "Starting...")
    # ... do work ...
    await progress(0.5, "Processing item 5/10...")
    # ... more work ...
    await progress(1.0, "Complete!")
```

### 4. Structured Errors

```python
raise ValidationError(
    "Unknown provider: anthropic_xxl",
    field="provider",
    suggestions=["anthropic_xs", "anthropic_m", "anthropic_xl"],
    recovery_options=["use_default", "skip", "ask_user"]
)
```

## Example System Architecture

Here's how you might structure a complete MCP system:

```
your-system/
├── substrate/       # Foundation (this package)
├── akab/           # A/B testing
├── your-mcp-1/     # Your domain-specific MCP
├── your-mcp-2/     # Another domain MCP
├── krill/          # Data storage
└── docker-compose.yml
```

### Integration Example

To use AKAB for testing in your MCP:
```python
# In your MCP, call AKAB for comparisons
result = await ctx.call_tool(
    "akab_quick_compare",
    prompt="Your prompt",
    providers=["anthropic_m", "openai_l"]
)
```

## Custom Documentation

Substrate can load custom documentation. Mount your docs:

```bash
docker run -v ./my-docs:/substrate-docs substrate-mcp
```

Your documentation directory should contain:
- `atlas.md` - Your development methodology
- `system-design.md` - Your system architecture
- `component-map.json` - Your component registry

## Common Implementation Errors to Avoid

1. **AsyncIO Conflicts**
   - Error: "Already running asyncio in this thread"
   - Cause: Using `asyncio.run()` when FastMCP already manages the event loop
   - Fix: Use synchronous main() that calls server.run()

2. **Import-Time Initialization**
   - Error: "Documentation directory not found"
   - Cause: Creating server instances at module import time
   - Fix: Only create instances in main() or when explicitly called

3. **Missing Substrate Docs**
   - Error: Substrate can't find its documentation files
   - Cause: Docs not copied in Dockerfile
   - Fix: Ensure Dockerfile copies entire substrate directory including docs

4. **Build Context Errors**
   - Error: "failed to compute cache key: '/substrate': not found"
   - Cause: Building from component directory instead of root
   - Fix: Always build from system root directory

5. **Stdout Pollution**
   - Error: "Unexpected token" or "Invalid JSON"
   - Cause: print() statements or logging to stdout
   - Fix: Always log to stderr, never stdout

## Error Handling Philosophy

- **Errors as part of results** (not exceptions):
  - Provider failures recorded in result with error field
  - Execution continues for other providers
  - Analysis includes success/failure rates
- All errors return structured responses
- No exceptions leak to user
- Each MCP handles its own errors
- Errors include actionable suggestions
- Can trigger sampling for error recovery

## Anti-Patterns to Avoid

1. **Feature Creep**: Don't add features during implementation
2. **Stub Creation**: Always use proper dependencies
3. **Cross-Contamination**: Keep MCP responsibilities separate
4. **Over-Engineering**: File storage is fine for single user
5. **Under-Documentation**: Always update this document
6. **Silent Failures**: NEVER catch ImportError silently
7. **Fake Success**: NEVER mark failed API calls as successful
8. **Mock Implementations**: ALWAYS make real API calls

## What Success Looks Like

- Clean separation of concerns
- No code duplication
- Scientific rigor in testing
- Easy to understand and maintain
- Each component does one thing well
- Production-grade reliability
- Clear error messages
- Proper documentation

## Extending the System

### Adding New MCPs

1. **Define Clear Purpose**: What specific problem does this MCP solve?
2. **Use Substrate Base**: Inherit from `SubstrateMCP`
3. **Follow Patterns**: Use standard response formats and error handling
4. **Document Tools**: Clear descriptions for each tool
5. **Test Separately**: Create external test scripts
6. **Integrate Properly**: Use other MCPs through tool calls, not imports

### Best Practices

1. **Single Responsibility**: Each MCP does one thing well
2. **Clear Interfaces**: Explicit contracts between MCPs
3. **Proper Separation**: No cross-contamination of concerns
4. **Real Implementations**: No mocks or stubs in production
5. **Structured Data**: Use JSON for storage and configuration
6. **Loud Failures**: Always fail with clear error messages
7. **Documentation First**: Update docs before implementing

## Conclusion

This architecture provides:
- Clean separation of concerns
- Reusable components
- Scientific testing capabilities
- Production-grade reliability
- Easy extensibility

Start with substrate and AKAB as your foundation, then build your domain-specific MCPs following these patterns. Remember: production-grade means it actually works!