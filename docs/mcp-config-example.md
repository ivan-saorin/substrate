# Example MCP configuration for Atlas with self-documenting servers

## Claude Desktop config.json excerpt

```json
{
  "mcpServers": {
    "atlas": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "atlas-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "-e", "INSTANCE_TYPE=atlas",
        "-e", "INSTANCE_DESCRIPTION=Master orchestrator of the cognitive manipulation system",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/substrate/data:/app/data",
        "substrate-mcp:latest"
      ]
    },
    "substrate": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "substrate-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "-e", "INSTANCE_TYPE=substrate",
        "-e", "INSTANCE_DESCRIPTION=System architecture and documentation server",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/substrate/data:/app/data",
        "substrate-mcp:latest"
      ]
    },
    "tloen": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "tloen-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "-e", "INSTANCE_TYPE=tloen",
        "-e", "INSTANCE_DESCRIPTION=Site format transformation service",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/tloen/data:/app/data",
        "substrate-mcp:latest"
      ]
    },
    "uqbar": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "uqbar-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "-e", "INSTANCE_TYPE=uqbar",
        "-e", "INSTANCE_DESCRIPTION=Persona and component composition service",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/uqbar/data:/app/data",
        "substrate-mcp:latest"
      ]
    },
    "synapse": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "synapse-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/synapse/data:/app/data",
        "synapse-mcp:latest"
      ]
    },
    "akab": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "--name", "akab-mcp-claude",
        "-e", "PYTHONUNBUFFERED=1",
        "-e", "MCP_TRANSPORT=stdio",
        "--env-file", "C:/projects/atlas/akab/.env",
        "-v", "C:/projects/atlas/akab/data:/app/data",
        "akab-mcp:latest"
      ]
    }
  }
}
```

## Key Changes

1. **Atlas Instance**: New master orchestrator that knows about all servers
2. **Self-Documenting**: Each server responds to its own name with documentation
3. **Consistent Naming**: Server name = tool name for discovery

## Usage Examples

### Discovery Pattern
- User: "How do I use tloen?"
- LLM calls: `tloen` 
- Gets: Full documentation with examples

### Master Overview
- User: "What is Atlas?"
- LLM calls: `atlas`
- Gets: Complete system overview with all servers

### Workflow Discovery
- User: "Show me Atlas workflows"
- LLM calls: `atlas_show_workflows`
- Gets: All available workflows

## Benefits

1. **Natural Discovery**: "Use tloen" → calls `tloen` → gets docs
2. **Self-Contained**: Each server knows how to explain itself
3. **Navigation**: Suggestions guide between servers
4. **Master View**: Atlas provides system-wide perspective
