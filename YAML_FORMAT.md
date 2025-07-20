# YAML Reference Format

## Overview

Starting from version 1.1.0, substrate uses YAML format for all references instead of JSON. This provides better human readability, especially for multiline content.

## Benefits

1. **Multiline strings**: Use `|` for readable content blocks
2. **Comments**: Add `#` comments for documentation
3. **Cleaner syntax**: Less quotes and brackets
4. **Backwards compatible**: Still reads old .json files

## Format

All references follow this structure:

```yaml
content: |
  Your actual content here
  Can span multiple lines
  Much more readable than JSON

metadata:
  key: value
  nested:
    structure: supported
  lists:
    - item1
    - item2
```

## File Naming

- New files: `reference_name.yaml`
- Legacy files: `reference_name.json` (still readable)

## Examples

See `example_refs/` directory for sample YAML references:
- `reddit_format.yaml` - TLOEN site formatting
- `hemingway_persona.yaml` - UQBAR writing persona

## Migration

No migration needed! The system automatically:
1. Creates new references as YAML
2. Reads existing JSON references
3. Prefers YAML if both exist
