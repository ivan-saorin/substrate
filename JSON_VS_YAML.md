# JSON vs YAML Reference Format Comparison

## Before (JSON)

```json
{
  "content": "**{{title}}**\n\n{{content}}\n\n**TL;DR**: {{summary}}\n\n**Edit**: Thanks for the gold, kind stranger!",
  "metadata": {
    "site": "reddit",
    "format_type": "post", 
    "placeholders": ["title", "content", "summary"],
    "created": "2025-01-18T12:00:00Z",
    "version": 1
  }
}
```

## After (YAML)

```yaml
# Reddit post format template
content: |
  **{{title}}**
  
  {{content}}
  
  **TL;DR**: {{summary}}
  
  **Edit**: Thanks for the gold, kind stranger!

metadata:
  site: reddit
  format_type: post
  placeholders:
    - title
    - content
    - summary
  created: '2025-01-18T12:00:00Z'
  version: 1
```

## Key Improvements

1. **Readability**: Content is displayed exactly as it will appear
2. **No escaping**: No need for `\n` characters
3. **Comments**: Can add `#` comments for documentation
4. **Natural formatting**: Indentation shows structure clearly
5. **Less syntax noise**: Fewer quotes, brackets, and commas

## Multiline Benefits

### JSON (hard to read)
```json
{
  "content": "Write with short sentences. Use simple words.\n\nSay what you mean. Cut the fat. Every word must earn its place.\n\nAvoid adverbs. They weaken prose. Strong verbs carry the weight."
}
```

### YAML (natural formatting)
```yaml
content: |
  Write with short sentences. Use simple words.
  
  Say what you mean. Cut the fat. Every word must earn its place.
  
  Avoid adverbs. They weaken prose. Strong verbs carry the weight.
```

## Complex Metadata

### JSON
```json
{
  "metadata": {
    "features": {
      "formatting": ["bold", "italic", "headers"],
      "sections": {
        "intro": true,
        "body": true,
        "conclusion": true
      }
    }
  }
}
```

### YAML
```yaml
metadata:
  features:
    formatting:
      - bold
      - italic  
      - headers
    sections:
      intro: true
      body: true
      conclusion: true
```

## With Comments

```yaml
# Hemingway writing style persona
content: |
  # Core principles
  Write with short sentences. Use simple words.
  
  # Technique
  Say what you mean. Cut the fat.
  
  # Style notes
  Avoid adverbs. Strong verbs carry weight.

metadata:
  persona: hemingway
  style: minimalist
  # These characteristics define the output
  characteristics:
    - concise      # Short, to the point
    - direct       # No fluff
    - powerful     # Every word matters
```

This is impossible with JSON!
