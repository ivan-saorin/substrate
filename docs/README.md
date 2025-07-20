# Atlas Cognitive Manipulation System

## Overview

Atlas is a distributed cognitive manipulation toolkit designed to optimize AI interactions through systematic prompt engineering, multi-model testing, and intelligent content transformation.

## System Components

### Core Servers

1. **Substrate** - The foundation layer providing:
   - Reference management (CRUD operations)
   - Documentation access
   - Workflow navigation
   - Shared services for all servers

2. **Synapse** - Prompt engineering and enhancement:
   - Pattern-based prompt optimization
   - Model-specific enhancements
   - Stable genius content generation
   - Pattern effectiveness analysis

3. **AKAB** - A/B testing and experimentation:
   - Level 1: Quick comparison across providers
   - Level 2: Campaign-based testing
   - Level 3: Blinded scientific experiments
   - Statistical analysis and cost reporting

4. **TLOEN** - Site format transformation:
   - Platform-specific formatting (Reddit, Twitter, GitHub, etc.)
   - Template-based content transformation
   - Multi-platform formatting

5. **UQBAR** - Persona and component management:
   - Writing personas (technical, casual, creative)
   - Content components (citations, code, structure)
   - Style composition and application

## Architecture v2.0

The system follows a feature-based hybrid architecture:
- **Feature Isolation**: Each capability is a self-contained module
- **YAML Configuration**: All prompts, patterns, and workflows in YAML
- **Single Source of Truth**: Model configuration from .env
- **Standardized Responses**: Consistent format with navigation hints

## Quick Start

### Using Substrate (Full System)
Access documentation, manage references, and navigate workflows:
```
substrate:documentation - Read system docs
substrate:show_workflows - Discover workflows
substrate:create_ref - Save content
```

### Using TLOEN (Formatting)
Transform content for specific platforms:
```
tloen:execute - Apply platform templates
tloen:list_refs - View available formats
```

### Using UQBAR (Personas)
Apply writing styles and components:
```
uqbar:execute - Apply personas/components
uqbar:list_refs - View available personas
```

## Workflows

Pre-built workflows guide you through complex tasks:
- **Prompt Optimization**: Analyze → Enhance → Test → Deploy
- **Content Pipeline**: Generate → Format → Style → Publish
- **Quick Testing**: Compare → Enhance → Validate

## Navigation

Every tool response includes intelligent suggestions for next steps, making it easy to discover and use the system's capabilities.

## Documentation

- `atlas.md` - Development methodology
- `system-design.md` - Architectural principles
- `component-map.json` - Server relationships