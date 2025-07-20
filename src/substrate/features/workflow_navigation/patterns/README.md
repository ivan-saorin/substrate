# Workflow Patterns

This directory contains YAML definitions for cognitive manipulation workflows that guide users through multi-step processes across the Atlas system.

## Structure

Each workflow YAML file contains:

```yaml
name: Workflow Name
description: What this workflow accomplishes
category: workflow_category
tags: [tag1, tag2, tag3]
version: 1.0

steps:
  - id: unique_step_id
    tool: server:tool_name       # Optional - some steps are just decision points
    description: What this step does
    inputs:
      param_name: required|optional|$reference
    outputs:
      - name: output_name
        type: output_type
    next:                        # Can be string, list, or conditional
      - condition: success
        goto: next_step_id
```

## Available Workflows

### 1. Prompt Optimization (`prompt_optimization.yaml`)
- **Purpose**: Optimize prompts for maximum effectiveness
- **Flow**: Analyze → Enhance → Test → Run → Analyze Results
- **Servers**: Synapse, AKAB, Substrate

### 2. Content Pipeline (`content_pipeline.yaml`)
- **Purpose**: Generate and format content for multiple platforms
- **Flow**: Generate → Save → Format → Apply Persona → Save Final
- **Servers**: Synapse, Substrate, TLOEN, UQBAR

### 3. Quick Testing (`quick_testing.yaml`)
- **Purpose**: Rapid prompt comparison across providers
- **Flow**: Compare → Analyze → Enhance → Recompare → Evaluate
- **Servers**: AKAB, Synapse, Substrate

### 4. Cross-Server Integration (`cross_server_integration.yaml`)
- **Purpose**: Demonstrate full Atlas system capabilities
- **Flow**: Complete end-to-end content creation with all servers
- **Servers**: All (Substrate, Synapse, UQBAR, TLOEN, AKAB)

## Input/Output References

Workflows support dynamic data flow between steps:

- `$inputs.param_name` - Reference to workflow input
- `$outputs.step_id.output_name` - Reference to previous step output
- `$outputs.step1.ref || $outputs.step2.ref` - Fallback references

## Conditional Flow

Steps can have conditional next steps:

```yaml
next:
  - condition: success
    goto: continue_flow
  - condition: error
    goto: handle_error
  - condition: needs_enhancement
    goto: enhance_step
```

## Using Workflows

### 1. Discover Available Workflows
```
Tool: substrate_show_workflows
Args: {
  "category": "prompt_optimization"  # Optional filter
}
```

### 2. Get Workflow Guide
```
Tool: substrate_workflow_guide
Args: {
  "workflow_name": "Prompt Optimization"
}
```

### 3. Get Next Step Suggestions
```
Tool: substrate_suggest_next
Args: {
  "current_tool": "synapse:enhance_prompt",
  "context": {
    "output_ref": "prompts/enhanced_v2"
  }
}
```

## Creating New Workflows

1. Create a new YAML file in this directory
2. Follow the structure template
3. Ensure all referenced tools exist
4. Test with `substrate_workflow_guide`
5. Update `index.yaml` with the new workflow

## Best Practices

1. **Unique IDs**: Every step must have a unique ID within the workflow
2. **Clear Descriptions**: Each step should clearly describe its purpose
3. **Error Handling**: Include alternative paths for failures
4. **Tool Validation**: Ensure all referenced tools exist and are accessible
5. **Output Types**: Define clear output types for better tooling support

## Integration with Navigation Engine

The workflow patterns integrate with the NavigationEngine to provide:
- Automatic next-step suggestions based on workflow context
- Workflow-aware parameter mapping
- Progress tracking through multi-step processes
- Alternative path suggestions when steps fail

## Future Enhancements

- [ ] Workflow execution tracking
- [ ] Progress persistence across sessions
- [ ] Custom workflow builder UI
- [ ] Workflow sharing and versioning
- [ ] Performance metrics per workflow
- [ ] Automated workflow optimization