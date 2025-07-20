# Claude Desktop Configuration for TLOEN and UQBAR

Add these configurations to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "tloen": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "INSTANCE_TYPE=tloen",
        "-v", "C:/projects/atlas/substrate/data/tloen:/app/data/tloen",
        "atlas/substrate:latest"
      ]
    },
    "uqbar": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "INSTANCE_TYPE=uqbar",
        "-v", "C:/projects/atlas/substrate/data/uqbar:/app/data/uqbar",
        "atlas/substrate:latest"
      ]
    }
  }
}
```

## Key Points:

1. **Environment Variable**: The `-e INSTANCE_TYPE=<name>` flag sets the instance type
2. **Volume Mount**: Each instance mounts its own data directory
3. **Same Image**: Both use `atlas/substrate:latest` image
4. **Names Must Match**: The server name in config must match INSTANCE_TYPE value

## Testing:

After adding the configuration and restarting Claude Desktop:

1. Test TLOEN:
   ```
   tloen()  # Should show site formatter capabilities
   tloen_list_refs()  # Should list available site formats
   ```

2. Test UQBAR:
   ```
   uqbar()  # Should show persona composer capabilities
   uqbar_list_refs()  # Should list available personas
   ```

## Troubleshooting:

If you see "substrate_*" methods instead of "tloen_*" or "uqbar_*":
- Check that INSTANCE_TYPE environment variable is set correctly
- Ensure the Docker image was rebuilt with the latest changes
- Restart Claude Desktop after configuration changes
