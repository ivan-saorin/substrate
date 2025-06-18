# Substrate

Foundation layer for AI applications providing:
- MCP (Model Context Protocol) implementation
- Multi-provider LLM support (OpenAI, Anthropic, Google, etc.)
- Evaluation engine for scoring AI responses
- Filesystem utilities for async file operations

## Building

```bash
docker build -t substrate:latest .
```

## Usage

This is a base Docker image meant to be used with `FROM substrate:latest` in other projects.

## Components

- **MCP Server**: FastMCP implementation for tool/resource registration
- **Providers**: Unified interface for multiple LLM providers
- **Evaluation**: Scoring engine for innovation, coherence, practicality
- **Filesystem**: Async file operations with metadata support
