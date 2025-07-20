# Architectural Significant Record: Cognitive Manipulation System v2.0 (Definitive)

## Context and Background

**Date**: 2025-01-20  
**Architect**: Ivan (Solution Architect)  
**System**: Atlas - Distributed Cognitive Manipulation Toolkit  
**Phase**: Architecture Refactoring v2.0  
**Updated**: 2025-01-20 (Phase 1 Complete)

## Executive Summary

Major architectural refactoring achieving:

1. **Prompts as YAML data** (not code) ✓
2. **Feature-based hybrid architecture** (no monolithic files) ✓
3. **Single source of truth** (.env for models) ✓
4. **Enhanced workflow navigation** (substrate-level) ✓
5. **No backward compatibility** (clean slate) ✓
6. **Self-documenting servers** (new in implementation) ✓

## Core Principles

### ASR-First Development

The ASR defines the desired state. Implementation follows the ASR, not the other way around.

### Clean Code Standards v2.0

- **NO monolithic files** - Feature modules < 500 lines ✓
- **NO hardcoded prompts** - Everything in YAML ✓
- **NO duplicate configs** - .env is truth ✓
- **NO dead code** - Delete immediately ✓
- **ONE pattern** - Hybrid feature architecture ✓

### YAML Everywhere

- **References**: Already YAML ✓
- **Prompts**: Convert to YAML ✓
- **Patterns**: Convert to YAML ✓
- **Workflows**: Define in YAML ✓
- **Model metadata**: YAML + .env ✓

## Architecture Decisions

### ADR-11: Feature-Based Hybrid Architecture

**Decision**: Adopt hybrid feature-based + shared resources architecture.

**Rationale**:

- Feature isolation for parallel development
- Shared resources for cross-cutting concerns
- Natural boundaries align with cognitive capabilities
- Each feature self-contained with prompts/logic/tests

**Universal Structure**:

```
server/
├── src/
│   └── server_name/
│       ├── __init__.py
│       ├── server.py          # <200 lines MCP setup
│       ├── features/          # Business capabilities
│       │   ├── feature_name/
│       │   │   ├── __init__.py
│       │   │   ├── tool.py    # MCP tool registration
│       │   │   ├── handler.py # Business logic
│       │   │   └── prompts.yaml
│       │   └── .../
│       └── shared/            # Cross-cutting concerns
│           ├── models/        # Model registry
│           ├── storage/       # Persistence
│           └── utils/         # Helpers
```

### ADR-12: Prompts as YAML Data

**Decision**: All prompts, patterns, and templates must be YAML files.

**Format**:

```yaml
# feature/prompts.yaml
version: 1.0
prompts:
  main:
    content: |
      Your prompt template here with {placeholders}
      Multiple lines supported
      Natural formatting preserved
    metadata:
      author: system
      tested: true
      effectiveness: 0.85
      models:
        - anthropic_m
        - anthropic_l
  
  error_handling:
    content: |
      When encountering {error_type}...
```

### ADR-13: Model Registry from .env

**Decision**: Eliminate models.json, use .env as single source.

**Implementation**:

```python
# shared/models/registry.py
from substrate.models import ModelRegistry

# Loads from environment automatically
MODEL_REGISTRY = ModelRegistry()

# Usage
model = MODEL_REGISTRY.get('anthropic_m')
print(model.api_name)  # claude-3-5-sonnet-20241022
```

**Phase 1 Result**: Successfully implemented with 24 models from 4 providers (Anthropic, OpenAI, Google, Groq) loaded from .env.

### ADR-14: No Backward Compatibility

**Decision**: Break compatibility ruthlessly during refactoring.

**Rules**:

- Delete old code immediately
- No adapters or migration paths
- Document breaks in ASR
- Servers can be offline during their phase

### ADR-15: Standard Response Format

**Decision**: All tools return standardized responses with navigation hints.

**Format**:

```python
{
    "data": {...},  # Tool-specific data
    "metadata": {
        "server": "synapse",
        "tool": "enhance_prompt",
        "timestamp": 1737371234.5
    },
    "suggestions": [  # Auto-generated navigation
        {
            "tool": "akab:akab_create_campaign",
            "reason": "Test enhanced vs original prompt",
            "params": {"base_prompt": "$ref"}
        }
    ],
    "message": "Enhancement complete. Saved to temp/enhanced"
}
```

### ADR-16: Substrate-Level Workflow Navigation

**Decision**: Implement workflow discovery and navigation at substrate level.

**Components**:

1. **Workflow patterns** in YAML ✓
2. **Tool metadata** declares relationships ✓
3. **Auto-suggestions** in every response ✓
4. **show_workflows** tool for discovery ✓

**Phase 1 Implementation**: Created 5 workflow patterns:

- `prompt_optimization.yaml` - Complete optimization pipeline
- `content_pipeline.yaml` - Content generation and formatting
- `quick_testing.yaml` - Rapid comparison workflow
- `cross_server_integration.yaml` - Full system demonstration
- `simple_example.yaml` - Template for new workflows

### ADR-17: Self-Documenting Servers (NEW)

**Decision**: Every server responds to its own name with comprehensive documentation.

**Rationale**:

- Natural discovery: "How do I use tloen?" → Call `tloen` → Get docs
- No hidden knowledge required
- Each server fully self-contained
- Better LLM integration

**Implementation**:

```python
# Every server's base tool returns documentation
async def get_server_info() -> Dict[str, Any]:
    return {
        "name": self.instance_type,
        "description": self.instance_description,
        "usage": detailed_usage_instructions,
        "examples": code_examples,
        "available_tools": tool_list,
        "available_resources": format_list,
        "navigation": next_step_suggestions
    }
```

### ADR-18: Single Docker Image Architecture (NEW)

**Decision**: TLOEN and UQBAR are substrate instances, not separate servers.

**Rationale**:

- Simpler deployment
- Shared codebase
- Configuration through environment variables
- Reduced maintenance

**Implementation**:

```bash
# All three using same image
docker run -e INSTANCE_TYPE=substrate substrate-mcp:latest
docker run -e INSTANCE_TYPE=tloen substrate-mcp:latest  
docker run -e INSTANCE_TYPE=uqbar substrate-mcp:latest
```

## Three-Phase Implementation Plan

### Phase 1: Substrate Foundation + Instances ✓ COMPLETE

**Duration**: 2 days (actual)  
**Servers**: substrate, tloen, uqbar

#### What Was Built

**Substrate Core** ✓

```
substrate/
├── src/
│   └── substrate/
│       ├── server.py              # 390 lines
│       ├── features/
│       │   ├── documentation/     # System docs ✓
│       │   ├── references/        # Reference management ✓
│       │   ├── execution/         # Execute pattern ✓
│       │   └── workflow_navigation/
│       │       ├── tool.py        # show_workflows ✓
│       │       └── patterns/      # 5 Workflow YAMLs ✓
│       └── shared/
│           ├── models/
│           │   └── registry.py    # From .env ✓
│           ├── prompts/
│           │   └── loader.py      # YAML loader ✓
│           ├── storage/
│           │   └── reference_manager.py ✓
│           └── response/
│               └── builder.py     # Standard responses ✓
```

**TLOEN as Instance** ✓

- 13 site format templates (Reddit, Twitter, GitHub, etc.)
- Handlebars-style templating
- Full reference management

**UQBAR as Instance** ✓

- 15 personas (technical, casual, creative, characters)
- 17 components (code, citations, structure, etc.)
- Complete style system

#### Key Improvements Over Plan

1. **Single Docker Image**: TLOEN/UQBAR are instances, not separate servers
2. **Self-Documenting**: Each server responds to its name with full docs
3. **Pre-loaded YAMLs**: Professional templates ready to use
4. **Complete Workflows**: 5 workflow patterns implemented

### Phase 2: AKAB Migration

**Duration**: 2 days  
**Note**: AKAB offline during migration

```
akab/
├── src/
│   └── akab/
│       ├── server.py              # <200 lines
│       ├── features/
│       │   ├── quick_compare/     # Level 1
│       │   │   ├── tool.py
│       │   │   ├── comparator.py
│       │   │   └── prompts.yaml
│       │   ├── campaigns/         # Level 2
│       │   │   ├── create/
│       │   │   ├── execute/
│       │   │   ├── analyze/
│       │   │   └── prompts/
│       │   ├── experiments/       # Level 3
│       │   │   ├── create/
│       │   │   ├── reveal/
│       │   │   ├── diagnose/
│       │   │   └── protocols/
│       │   └── reporting/
│       │       ├── cost/
│       │       └── list/
│       └── shared/
│           ├── hermes/            # API management
│           ├── laboratory/        # Execution engine
│           └── vault/             # Result storage
```

### Phase 3: Synapse Evolution

**Duration**: 2-3 days  
**Note**: Synapse offline during migration

```
synapse/
├── src/
│   └── synapse/
│       ├── server.py              # <200 lines
│       ├── features/
│       │   ├── enhance_prompt/
│       │   │   ├── tool.py
│       │   │   ├── enhancer.py
│       │   │   ├── analyzer.py
│       │   │   └── prompts.yaml
│       │   ├── stable_genius/
│       │   │   ├── tool.py
│       │   │   ├── generator.py
│       │   │   └── domains/
│       │   │       ├── technical.yaml
│       │   │       ├── creative.yaml
│       │   │       └── academic.yaml
│       │   ├── pattern_analysis/
│       │   └── experiment_prep/
│       ├── patterns/              # Enhancement library
│       │   ├── self_discovery.yaml
│       │   ├── creative_leap.yaml
│       │   ├── structured_thinking.yaml
│       │   └── model_specific/
│       └── shared/
│           └── enhancement/
│               └── engine.py
```

## Implementation Standards

### Feature Module Template

```python
# features/my_feature/tool.py
def register_my_feature_tools(server) -> List[dict]:
    """Register feature tools on the server"""
    
    async def my_tool(param1: str, param2: int = None) -> Dict[str, Any]:
        """Tool implementation"""
        try:
            # Business logic
            result = await process(param1, param2)
            
            # Build suggestions
            suggestions = [
                server.response_builder.suggest_next(
                    "next_tool",
                    "Reason for suggestion",
                    param=value
                )
            ]
            
            return server.response_builder.success(
                data=result,
                message="Operation complete",
                suggestions=suggestions
            )
        except Exception as e:
            return server.response_builder.error(str(e))
    
    # Register the tool
    server.register_tool(f"{server.instance_type}_my_tool", my_tool)
    
    return [{
        "name": f"{server.instance_type}_my_tool",
        "description": "Tool description"
    }]
```

### Workflow Pattern Template

```yaml
# substrate/features/workflow_navigation/patterns/example.yaml
name: Example Workflow
description: Shows the pattern structure
category: category_name
tags: [tag1, tag2, tag3]
version: 1.0

steps:
  - id: start
    tool: server:tool_name       # Optional for decision points
    description: First step
    inputs:
      param1: required
      param2: optional
      param3: $reference        # Reference to previous output
    outputs:
      - name: result_ref
        type: reference
    next:
      - condition: success
        goto: process
      - condition: needs_enhancement  
        goto: enhance
        
  - id: enhance
    tool: synapse:enhance_prompt
    inputs:
      prompt_ref: $outputs.start.result_ref
    outputs:
      - name: enhanced_ref
        type: reference
    next: process
    
  - id: process
    tool: akab:create_campaign
    inputs:
      base_prompt: $outputs.enhance.enhanced_ref || $outputs.start.result_ref
    outputs:
      - name: campaign_id
        type: string
    next: complete
    
  - id: complete
    description: Workflow complete
    outputs:
      - name: final_result
        type: reference
```

## Phase 1 Implementation Notes

### What Worked Better Than Planned

1. **Single Docker Image Architecture**
   - Simpler than maintaining separate servers
   - Environment variables control behavior
   - Shared codebase reduces duplication

2. **Pre-loaded Professional YAMLs**
   - TLOEN: 13 platform templates ready to use
   - UQBAR: 32 personas and components
   - No need to create from scratch

3. **Self-Documenting Servers**
   - Each server explains itself when called by name
   - Natural discovery pattern for LLMs
   - No need to know about substrate_documentation

4. **Complete Workflow System**
   - 5 workflows covering common patterns
   - Dynamic loading from YAML
   - Integrated with navigation engine

### Lessons Learned

1. **Feature Isolation Works**
   - Each feature truly independent
   - Easy to test in isolation
   - Clear boundaries prevent coupling

2. **YAML Configuration Scales**
   - Templates, personas, workflows all in YAML
   - Easy to extend without code changes
   - Version control friendly

3. **Navigation Suggestions Are Essential**
   - Users discover capabilities naturally
   - Workflows emerge from suggestions
   - System teaches itself

## Migration Checklist

### Pre-Phase Preparation ✓

- [x] Backup current state (git branch)
- [x] Update .env with all models
- [x] Create substrate base structure
- [x] Implement model registry
- [x] Implement prompt loader

### Phase 1: Substrate + Instances ✓

- [x] Extract substrate documentation feature
- [x] Extract substrate reference feature
- [x] Extract substrate execution feature
- [x] Implement workflow navigation
- [x] Create base workflow patterns (5 created)
- [x] Configure TLOEN as substrate instance
- [x] Configure UQBAR as substrate instance
- [x] Load professional YAML templates
- [x] Implement self-documenting servers
- [x] Test all three servers

### Phase 2: AKAB

- [ ] Create AKAB feature structure
- [ ] Extract quick_compare (Level 1)
- [ ] Extract campaigns (Level 2)
- [ ] Extract experiments (Level 3)  
- [ ] Extract reporting features
- [ ] Convert all prompts to YAML
- [ ] Add tool metadata
- [ ] Integrate workflow hints
- [ ] Delete server.py monolith
- [ ] Delete models.json

### Phase 3: Synapse

- [ ] Create Synapse feature structure
- [ ] Extract enhance_prompt feature
- [ ] Extract stable_genius feature
- [ ] Extract pattern_analysis
- [ ] Extract experiment_prep
- [ ] Convert patterns to YAML
- [ ] Convert prompts to YAML
- [ ] Add comprehensive metadata
- [ ] Delete server.py monolith
- [ ] Final system cleanup

### Post-Migration

- [ ] Update all documentation
- [ ] Create feature development guide
- [ ] Test cross-server workflows
- [ ] Optimize suggestion algorithms
- [ ] Tag v2.0 release

## Future Considerations

### Microservice Potential

Each feature could become standalone:

- `atlas-enhance-prompt`
- `atlas-stable-genius`  
- `atlas-ab-testing`
- `atlas-workflow-engine`

### NPL and Q Implementation

When adding new servers:

1. Configure as substrate instance
2. Add instance-specific features
3. Define tool relationships
4. Add workflow patterns
5. Use standard responses

### Advanced Workflows

- Workflow recording and replay
- Custom workflow builder
- Performance analytics
- Automated optimization

## Conclusion

Phase 1 implementation exceeded expectations by:

1. **Simplifying architecture** through instance-based design
2. **Enhancing discoverability** through self-documentation
3. **Providing immediate value** through pre-loaded templates
4. **Creating solid foundation** for remaining phases

The system successfully evolved from a collection of tools to an intelligent assistant that guides users through cognitive manipulation workflows while maintaining the flexibility for power users to chart their own course.

**Remember**: The ASR is truth. Implementation serves the architecture.
