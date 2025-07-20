#!/usr/bin/env python
"""Check fastmcp imports"""
import sys

try:
    import fastmcp
    print("fastmcp imported successfully")
    print("fastmcp attributes:", dir(fastmcp))
    
    # Try different import paths
    imports_to_try = [
        ("from fastmcp import FastMCP", "FastMCP"),
        ("from fastmcp.server import Server", "Server"),
        ("from fastmcp import Server", "Server"),
        ("from fastmcp import MCP", "MCP"),
    ]
    
    for import_str, attr in imports_to_try:
        try:
            exec(import_str)
            print(f"✓ {import_str} - SUCCESS")
        except Exception as e:
            print(f"✗ {import_str} - ERROR: {e}")
            
except Exception as e:
    print(f"Failed to import fastmcp: {e}")
    sys.exit(1)
