#!/usr/bin/env python3
"""
Test script to verify workflow YAML loading
Run this in the substrate container to test workflow patterns
"""
import sys
import os
from pathlib import Path

# Add substrate to path
sys.path.insert(0, '/app/src')

from substrate.shared.prompts import PromptLoader

def test_workflow_loading():
    """Test loading workflow YAML files"""
    loader = PromptLoader()
    patterns_dir = Path('/app/src/substrate/features/workflow_navigation/patterns')
    
    print("Testing Workflow Pattern Loading")
    print("=" * 50)
    
    if not patterns_dir.exists():
        print(f"ERROR: Patterns directory not found: {patterns_dir}")
        return
    
    yaml_files = list(patterns_dir.glob("*.yaml"))
    print(f"Found {len(yaml_files)} YAML files")
    print()
    
    for yaml_file in yaml_files:
        if yaml_file.name == 'index.yaml':
            continue  # Skip index
            
        print(f"Loading: {yaml_file.name}")
        try:
            workflow = loader.load_yaml(str(yaml_file))
            
            # Validate structure
            assert 'name' in workflow, "Missing 'name' field"
            assert 'steps' in workflow, "Missing 'steps' field"
            assert isinstance(workflow['steps'], list), "'steps' must be a list"
            
            print(f"  ✓ Name: {workflow['name']}")
            print(f"  ✓ Category: {workflow.get('category', 'none')}")
            print(f"  ✓ Steps: {len(workflow['steps'])}")
            
            # Check tools
            tools = []
            for step in workflow['steps']:
                if 'tool' in step:
                    tools.append(step['tool'])
            print(f"  ✓ Tools: {', '.join(tools[:3])}{'...' if len(tools) > 3 else ''}")
            
            print()
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
    
    print("=" * 50)
    print("Workflow loading test complete!")

if __name__ == "__main__":
    test_workflow_loading()
