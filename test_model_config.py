#!/usr/bin/env python3
"""
Test script for the model configuration system
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.providers.providers import ProviderManager, ModelConfig


async def test_model_config():
    """Test model configuration functionality"""
    print("=== Testing Model Configuration System ===\n")
    
    # Test 1: ModelConfig
    print("1. Testing ModelConfig class...")
    config = ModelConfig()
    
    try:
        # Test getting configured models
        anthropic_m = config.get_model_name("ANTHROPIC", "M")
        print(f"✓ ANTHROPIC M model: {anthropic_m}")
        
        openai_s = config.get_model_name("OPENAI", "S")
        print(f"✓ OPENAI S model: {openai_s}")
        
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("  Make sure model configurations are in .env file")
    
    print()
    
    # Test 2: List all configured models
    print("2. Listing all configured models...")
    all_models = config.list_configured_models()
    
    for provider, models in all_models.items():
        if models:
            print(f"\n{provider}:")
            for size, model in models.items():
                print(f"  {size}: {model}")
    
    print()
    
    # Test 3: ProviderManager
    print("3. Testing ProviderManager...")
    manager = ProviderManager()
    
    print(f"Available providers: {manager.list_providers()}")
    print()
    
    # Test 4: Execute with different sizes
    print("4. Testing execution with different model sizes...")
    
    test_prompts = [
        ("XS", "What is 2+2?"),
        ("S", "Explain photosynthesis in one sentence."),
        ("M", "Write a haiku about programming."),
    ]
    
    for size, prompt in test_prompts:
        try:
            print(f"\nTesting {size} model with: '{prompt}'")
            print("(In production, this would execute the prompt)")
            
            # Get model info
            model_info = manager.get_model_info("ANTHROPIC", size)
            if model_info['available']:
                print(f"✓ Would use: {model_info['model']}")
                print(f"  Estimated cost for 100 tokens: ${model_info['costs']['input'] * 0.1:.6f}")
            else:
                print(f"✗ Model not available: {model_info.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print()
    
    # Test 5: Cost estimation
    print("5. Testing cost estimation...")
    
    sizes = ["XS", "S", "M", "L"]
    prompt_tokens = 1000
    
    print(f"\nCost estimates for {prompt_tokens} prompt tokens:")
    print("-" * 50)
    
    for provider in ["ANTHROPIC", "OPENAI", "GOOGLE"]:
        print(f"\n{provider}:")
        for size in sizes:
            try:
                cost = manager.estimate_cost(provider, size, prompt_tokens, 500)
                print(f"  {size}: ${cost:.4f}")
            except:
                print(f"  {size}: Not configured")
    
    print("\n=== Test Complete ===")


async def test_actual_execution():
    """Test actual API execution (requires valid API keys)"""
    print("\n=== Testing Actual API Execution ===\n")
    
    manager = ProviderManager()
    
    # Simple test prompt
    test_prompt = "Say 'Hello from the model configuration test!' and nothing else."
    
    # Test with LOCAL provider (always available)
    print("Testing LOCAL provider...")
    try:
        result, metadata = await manager.execute(
            prompt=test_prompt,
            provider="LOCAL",
            size="M"
        )
        print(f"✓ LOCAL execution successful")
        print(f"  Metadata: {metadata}")
    except Exception as e:
        print(f"✗ LOCAL execution failed: {e}")
    
    print()
    
    # Test with a remote provider if available
    if "ANTHROPIC" in manager.list_providers():
        print("Testing ANTHROPIC provider with S model...")
        try:
            result, metadata = await manager.execute(
                prompt=test_prompt,
                provider="ANTHROPIC",
                size="S"
            )
            print(f"✓ ANTHROPIC execution successful")
            print(f"  Response: {result}")
            print(f"  Model used: {metadata['model']}")
            print(f"  Cost: ${metadata['cost']:.4f}")
        except Exception as e:
            print(f"✗ ANTHROPIC execution failed: {e}")
    
    print("\n=== Execution Test Complete ===")


if __name__ == "__main__":
    # Run configuration tests
    asyncio.run(test_model_config())
    
    # Uncomment to test actual API execution
    # asyncio.run(test_actual_execution())
