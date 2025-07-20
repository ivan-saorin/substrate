#!/usr/bin/env python3
"""
Test script to show new documentation format
Demonstrates what each server will return when rebuilt
"""
import json

# Simulate what each server will return with new documentation

docs = {
    "atlas": {
        "name": "atlas",
        "version": "2.0.0",
        "description": "Master orchestrator of the cognitive manipulation system",
        "documentation": {
            "summary": "I am Atlas, the master orchestrator of the cognitive manipulation system.",
            "usage": """I am ATLAS, the complete cognitive manipulation system. I know about all servers:

**Available Servers**:
- **Substrate** - Documentation, workflows, and reference management
- **Synapse** - Prompt engineering and enhancement  
- **AKAB** - A/B testing and experimentation
- **TLOEN** - Site format transformation
- **UQBAR** - Persona and component management

**How to Use Atlas**:
1. Start with me to understand the system
2. Use workflows to guide complex tasks
3. Navigate between servers using suggestions

**Example Workflow**:
1. `atlas` - Get system overview
2. `substrate_show_workflows` - Discover workflows
3. `substrate_workflow_guide` - Get step-by-step guidance
4. Follow the workflow using multiple servers

**Quick Actions**:
- Generate content: Use Synapse's stable_genius
- Format for platform: Use TLOEN's site templates
- Apply persona: Use UQBAR's personas
- Test variations: Use AKAB's experiments""",
            "examples": [
                {
                    "description": "Get system overview",
                    "tool": "atlas",
                    "args": {}
                },
                {
                    "description": "Start prompt optimization workflow",
                    "tool": "substrate_workflow_guide",
                    "args": {"workflow_name": "Prompt Optimization"}
                }
            ]
        },
        "tools": [
            {"name": "atlas_documentation", "description": "Access system architecture and methodology documentation"},
            {"name": "atlas_show_workflows", "description": "Discover available cognitive manipulation workflows"},
            {"name": "atlas_workflow_guide", "description": "Get step-by-step guidance for a specific workflow"},
            {"name": "atlas_suggest_next", "description": "Get smart suggestions for next tool based on current context"},
            {"name": "atlas_create_ref", "description": "Create or update a reference."},
            {"name": "atlas_read_ref", "description": "Read reference content."},
            {"name": "atlas_update_ref", "description": "Update existing reference."},
            {"name": "atlas_delete_ref", "description": "Delete a reference."},
            {"name": "atlas_list_refs", "description": "List all references with optional prefix filter."}
        ],
        "tool_count": 11,
        "model_registry": {
            "providers": ["anthropic", "openai", "google", "groq"],
            "models": 24
        }
    },
    
    "tloen": {
        "name": "tloen",
        "version": "2.0.0",
        "description": "Site format transformation service",
        "documentation": {
            "summary": "I transform content for specific platforms using format templates.",
            "usage": """I am TLOEN, the site format specialist. I format content for platforms like Reddit, Twitter, GitHub, etc.

**My Capabilities**:
- Transform content using platform-specific templates
- Apply formatting rules for each site
- Combine multiple platform formats

**Available Tools**:
- `tloen_execute` - Apply format templates
- `tloen_list_refs` - View available formats
- `tloen_create_ref` - Add new format templates

**Usage Pattern**:
```
tloen_execute(
    ref="sites/reddit",        # Platform template
    prompt="Your content",     # Content to format
    save_as="output/formatted" # Optional save
)
```""",
            "examples": [
                {
                    "description": "Format for Reddit",
                    "tool": "tloen_execute",
                    "args": {
                        "ref": "sites/reddit",
                        "prompt": "My awesome project announcement"
                    }
                },
                {
                    "description": "Multi-platform format",
                    "tool": "tloen_execute",
                    "args": {
                        "refs": ["sites/reddit", "sites/twitter"],
                        "prompt": "Content to format"
                    }
                }
            ],
            "available_formats": [
                "reddit", "twitter", "github", "stackoverflow",
                "hackernews", "linkedin", "arxiv", "wikipedia"
            ]
        },
        "tools": [
            {"name": "tloen_execute", "description": "Execute transformation using tloen templates/personas"},
            {"name": "tloen_create_ref", "description": "Create or update a reference."},
            {"name": "tloen_read_ref", "description": "Read reference content."},
            {"name": "tloen_update_ref", "description": "Update existing reference."},
            {"name": "tloen_delete_ref", "description": "Delete a reference."},
            {"name": "tloen_list_refs", "description": "List all references with optional prefix filter."}
        ],
        "tool_count": 8
    },
    
    "uqbar": {
        "name": "uqbar",
        "version": "2.0.0",
        "description": "Persona and component composition service",
        "documentation": {
            "summary": "I manage writing personas and content components for consistent style.",
            "usage": """I am UQBAR, the persona and component specialist. I help you write in different voices and styles.

**My Capabilities**:
- Apply writing personas (technical, casual, creative)
- Use content components (citations, code blocks, structure)
- Combine multiple personas/components

**Available Tools**:
- `uqbar_execute` - Apply personas/components
- `uqbar_list_refs` - View available resources
- `uqbar_create_ref` - Add new personas/components

**Usage Pattern**:
```
uqbar_execute(
    ref="personas/technical_writer",  # Persona to apply
    prompt="Explain quantum computing", # Content
    save_as="output/technical"        # Optional save
)
```""",
            "examples": [
                {
                    "description": "Apply technical persona",
                    "tool": "uqbar_execute",
                    "args": {
                        "ref": "personas/technical_writer",
                        "prompt": "Explain Docker containers"
                    }
                },
                {
                    "description": "Combine persona + component",
                    "tool": "uqbar_execute",
                    "args": {
                        "refs": ["personas/hemingway", "components/code_presentation"],
                        "prompt": "Tutorial on Python decorators"
                    }
                }
            ],
            "available_personas": [
                "technical_writer", "casual_explainer", "academic",
                "hemingway", "shakespeare", "gordon_ramsay"
            ],
            "available_components": [
                "code_presentation", "citation_system", "tutorial_structure"
            ]
        },
        "tools": [
            {"name": "uqbar_execute", "description": "Execute transformation using uqbar templates/personas"},
            {"name": "uqbar_create_ref", "description": "Create or update a reference."},
            {"name": "uqbar_read_ref", "description": "Read reference content."},
            {"name": "uqbar_update_ref", "description": "Update existing reference."},
            {"name": "uqbar_delete_ref", "description": "Delete a reference."},
            {"name": "uqbar_list_refs", "description": "List all references with optional prefix filter."}
        ],
        "tool_count": 8
    }
}

# Display each server's documentation
for server_name, response in docs.items():
    print(f"\n{'='*60}")
    print(f"Server: {server_name.upper()}")
    print(f"{'='*60}")
    
    # Show what calling the server tool returns
    print(f"\nCalling `{server_name}` returns:")
    print(f"Message: {response['documentation']['summary']}")
    print(f"\nDocumentation:")
    print(response['documentation']['usage'])
    
    if response['documentation'].get('examples'):
        print(f"\nExamples:")
        for ex in response['documentation']['examples']:
            print(f"- {ex['description']}")
            print(f"  Tool: {ex['tool']}")
            print(f"  Args: {json.dumps(ex['args'])}")
    
    print(f"\nTools ({response['tool_count']}):")
    for tool in response['tools'][:5]:  # Show first 5
        print(f"- {tool['name']}: {tool['description']}")
    if len(response['tools']) > 5:
        print(f"  ... and {len(response['tools']) - 5} more")

print("\n" + "="*60)
print("Summary: Each server is now self-documenting!")
print("Users can call the server name (e.g., 'tloen') to get full documentation.")
print("This solves the discovery problem - 'How do I use tloen?' -> Just call 'tloen'!")
