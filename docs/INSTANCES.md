# Substrate Instance Architecture

## Overview

Substrate serves as both a standalone MCP server and a foundation for instance-based services. This allows multiple specialized services to share the same codebase while providing different functionality through configuration.

## Instance Types

### 1. Substrate (Default)
- **Purpose**: Full cognitive manipulation substrate
- **Features**: All substrate features enabled
- **Usage**: `docker run -e INSTANCE_TYPE=substrate atlas/substrate:latest`

### 2. Tloen Instance
- **Purpose**: Site-specific content formatting
- **Features**: Reddit, StackOverflow, Twitter formatters
- **Usage**: `docker run -e INSTANCE_TYPE=tloen atlas/substrate:latest`

### 3. Uqbar Instance  
- **Purpose**: Persona and component composition
- **Features**: Writing styles, reusable components
- **Usage**: `docker run -e INSTANCE_TYPE=uqbar atlas/substrate:latest`

## How Instances Work

### Environment Variables

Each instance is configured through environment variables:

```bash
INSTANCE_TYPE=tloen                              # Instance identifier
INSTANCE_NAME=tloen                              # Display name
INSTANCE_DESCRIPTION="Site format transformer"   # Description
```

### Feature Loading

The substrate server checks `INSTANCE_TYPE` and loads appropriate features:

```python
# In server_fastmcp.py
instance_type = os.getenv("INSTANCE_TYPE", "substrate")

if instance_type == "tloen":
    register_tloen_features(mcp)
elif instance_type == "uqbar":
    register_uqbar_features(mcp)
else:
    register_all_substrate_features(mcp)
```

### Data Isolation

Each instance maintains its own data directory:
- Substrate: `/app/data/`
- Tloen: `/app/data/` (mapped to `C:/projects/atlas/tloen/data`)
- Uqbar: `/app/data/` (mapped to `C:/projects/atlas/uqbar/data`)

## Creating New Instances

To add a new instance type:

1. **Define Features**: Create feature modules in `substrate/src/substrate/features/`
2. **Register in Server**: Add instance type check in `server_fastmcp.py`
3. **Update Claude Config**: Add new instance configuration
4. **Create Data Directory**: `mkdir -p atlas/new-instance/data`

Example:
```python
# In server_fastmcp.py
elif instance_type == "new-instance":
    from .features.new_instance import register_new_instance_features
    register_new_instance_features(mcp)
```

## Benefits

1. **Code Reuse**: Shared substrate components
2. **Maintenance**: Single codebase for multiple services
3. **Flexibility**: Easy to add new instance types
4. **Resource Efficiency**: One Docker image serves multiple purposes

## Limitations

1. **Dependencies**: All instances share the same dependencies
2. **Size**: Docker image includes code for all instances
3. **Complexity**: Need to understand which features belong to which instance

## Best Practices

1. **Clear Naming**: Use descriptive instance types
2. **Feature Isolation**: Keep instance-specific features separate
3. **Documentation**: Document what each instance provides
4. **Testing**: Test each instance type independently
