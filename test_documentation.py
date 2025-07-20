#!/usr/bin/env python3
"""
Test script to verify documentation feature
Run this in the substrate container to test documentation loading
"""
import sys
import os
from pathlib import Path

# Add substrate to path
sys.path.insert(0, '/app/src')

from substrate import create_substrate_instance
import asyncio
import json

async def test_documentation():
    """Test documentation loading"""
    print("Testing Documentation Feature")
    print("=" * 50)
    
    # Create substrate instance
    server = create_substrate_instance()
    
    # Get the documentation handler
    doc_handler = server._tool_handlers.get('substrate_documentation')
    
    if not doc_handler:
        print("ERROR: Documentation handler not found!")
        print(f"Available handlers: {list(server._tool_handlers.keys())}")
        return
    
    # Test each documentation type
    doc_types = ['overview', 'atlas', 'system-design', 'component-map']
    
    for doc_type in doc_types:
        print(f"\nTesting: {doc_type}")
        print("-" * 30)
        
        try:
            result = await doc_handler(doc_type=doc_type)
            
            if 'error' in result.get('data', {}):
                print(f"  ✗ ERROR: {result['data']['error']}")
                if 'details' in result['data']:
                    print(f"    Details: {json.dumps(result['data']['details'], indent=4)}")
            else:
                print(f"  ✓ Success!")
                print(f"    File: {result['data']['file']}")
                print(f"    Source: {result['data'].get('source_path', 'unknown')}")
                print(f"    Content length: {len(result['data']['content'])} chars")
                print(f"    Suggestions: {len(result.get('suggestions', []))}")
                
        except Exception as e:
            print(f"  ✗ EXCEPTION: {e}")
    
    print("\n" + "=" * 50)
    print("Documentation test complete!")

if __name__ == "__main__":
    asyncio.run(test_documentation())
