# Atlas - MCP Development Methodology

Version: 1.0-OS
Last Updated: 2025-01-13
Location: substrate/docs/atlas.md

## Purpose

This document defines HOW to build, maintain, and evolve MCP-based systems. It provides a methodology for creating production-grade Model Context Protocol servers.

## Core Principles

### 1. Production-Grade Only

**Definition**: Code that actually works in production environments.

**This Means**:

- Real API calls, not mocks
- Actual results, not stubs
- Working features, not placeholders
- Loud failures, not silent errors

**Example**:

```python
# WRONG - Mock implementation
async def execute(self, prompt):
    return {"text": "mock response", "tokens": 100}

# RIGHT - Real implementation
async def execute(self, prompt):
    response = await client.messages.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}]
    )
    return {"text": response.content, "tokens": response.usage.total_tokens}
```

### 2. Clear Separation of Concerns

Each MCP should have a single, well-defined purpose.

**Good Separation**:

- substrate: System documentation and base classes
- akab: A/B testing and model comparison
- krill: Result storage and analysis

**Bad Separation**:

- One MCP doing both testing AND storage
- Mixing concerns within a single service

### 3. Explicit Over Implicit

Every decision must be documented and every interface must be clear.

**Examples**:

```python
# WRONG - Implicit behavior
def process(self, data):
    # Silently filters some data
    filtered = [d for d in data if d.get('valid')]
    return filtered

# RIGHT - Explicit behavior
def process(self, data, filter_invalid=True):
    """Process data with optional filtering.
    
    Args:
        data: Input data
        filter_invalid: If True, removes invalid entries
    """
    if filter_invalid:
        return [d for d in data if d.get('valid')]
    return data
```

## Development Workflow

### Phase 1: Design First

1. **Define the Problem**
   - What specific need does this MCP address?
   - What are the constraints?
   - What does success look like?

2. **Create Design Document**
   - Clear purpose statement
   - Tool definitions
   - Interface specifications
   - Error handling strategy

3. **Review Design**
   - Does it solve the problem?
   - Is it the simplest solution?
   - Are interfaces clear?

### Phase 2: Implementation

1. **Setup Project Structure**

   ```text
   your-mcp/
   ├── src/
   │   └── your_mcp/
   │       ├── __init__.py
   │       ├── server.py
   │       └── tools.py
   ├── tests/           # External tests
   ├── Dockerfile
   ├── pyproject.toml
   └── README.md
   ```

2. **Implement Following Design**
   - No deviations without discussion
   - No additional features
   - No stubs or workarounds

3. **Handle Unknowns**
   - If not specified → ASK
   - If unclear → CLARIFY
   - If impossible → DISCUSS alternatives

### Phase 3: Testing

1. **Test Outside Project**

   ```bash
   # Create test directory
   mkdir test_your_mcp
   cd test_your_mcp
   
   # Test functionality
   python test_real_api.py
   
   # Clean up after testing
   cd ..
   rm -rf test_your_mcp
   ```

2. **Validate All Paths**
   - Success cases
   - Error cases
   - Edge cases

### Phase 4: Integration

1. **Docker Build**

   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   
   # Copy substrate if dependent
   COPY substrate /substrate
   
   # Copy your MCP
   COPY . /app
   
   # Install dependencies
   RUN pip install -e /substrate && pip install -e .
   
   CMD ["python", "-m", "your_mcp"]
   ```

2. **Environment Configuration**

   ```bash
   # .env file
   YOUR_API_KEY=xxx
   DATA_DIR=/data
   ```

## MCP Implementation Rules

### Rule 1: Always Use Substrate Base

```python
from substrate import SubstrateMCP

class YourServer(SubstrateMCP):
    def __init__(self):
        super().__init__(
            name="your_mcp",
            version="1.0.0",
            description="Clear description"
        )
```

### Rule 2: Structured Responses

```python
return self.create_response(
    success=True,
    data={"result": processed_data},
    message="Operation completed successfully",
    metadata={"duration": 1.23, "items": 10}
)
```

### Rule 3: Proper Error Handling

```python
try:
    result = await self.process(data)
except ValidationError as e:
    return self.create_error_response(
        error=str(e),
        error_type="validation",
        suggestions=["Check input format", "Verify API key"]
    )
except Exception as e:
    # Log to stderr, not stdout!
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return self.create_error_response(
        error="Internal error occurred",
        error_type="internal"
    )
```

### Rule 4: Clean Tool Registration

```python
def _register_tools(self):
    @self.tool()
    async def my_tool(ctx, param1: str, param2: int = 10):
        """Clear description of what this tool does.
        
        Args:
            param1: Description of param1
            param2: Description of param2 (default: 10)
        """
        # Implementation
        return self.create_response(...)
```

## Common Patterns

### Pattern 1: Configuration Loading

```python
def load_config(self):
    """Load configuration from environment"""
    self.api_key = os.environ.get("API_KEY")
    if not self.api_key:
        raise ValueError("API_KEY environment variable required")
    
    self.data_dir = Path(os.environ.get("DATA_DIR", "/data"))
    self.data_dir.mkdir(exist_ok=True)
```

### Pattern 2: Progress Tracking

```python
async with self.progress_context("long_operation") as progress:
    await progress(0.1, "Starting...")
    # Do work
    await progress(0.5, "Halfway done...")
    # More work
    await progress(1.0, "Complete!")
```

### Pattern 3: Intelligent Assistance

```python
if need_help:
    return self.create_response(
        data={"status": "need_input"},
        _sampling_request={
            "prompt": "User needs help with X",
            "context": {"current_state": state}
        }
    )
```

## Best Practices

### 1. Logging

- Always log to stderr, never stdout
- Use structured logging with proper levels
- Include context in error messages

### 2. File Storage

- Use JSON for configuration and simple data
- Create clear directory structures
- Implement proper cleanup procedures

### 3. API Integration

- Always validate API keys on startup
- Handle rate limits gracefully
- Provide clear error messages for API failures

### 4. Docker Considerations

- Keep images small and focused
- Use multi-stage builds when needed
- Always specify resource limits

## Common Pitfalls

### 1. Stdout Pollution

**Problem**: Any non-JSON output to stdout breaks MCP protocol

**Solution**: Configure logging to use stderr:

```python
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr  # Critical!
)
```

### 2. AsyncIO Conflicts

**Problem**: Using `asyncio.run()` when FastMCP manages the event loop

**Solution**: Use synchronous main function:

```python
def main():
    server = YourServer()
    server.run()  # FastMCP handles async
```

### 3. Import-Time Initialization

**Problem**: Creating instances at module import time

**Solution**: Only create instances in main():

```python
# WRONG
server = MyServer()  # At module level

# RIGHT
def main():
    server = MyServer()
```

## Conclusion

This methodology emphasizes:

- Production-grade implementations
- Clear separation of concerns
- Explicit interfaces and behaviors
- Proper testing and validation

Following these principles leads to maintainable, reliable MCP servers that work correctly in production environments.
