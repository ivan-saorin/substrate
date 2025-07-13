"""Test substrate server functionality."""

import asyncio
import json
from pathlib import Path

import pytest

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from substrate.server import SubstrateServer
from substrate.base import SubstrateMCP


@pytest.mark.asyncio
async def test_substrate_server_initialization():
    """Test that substrate server initializes correctly."""
    server = SubstrateServer()
    
    assert server.name == "substrate"
    assert server.version == "1.0.0"
    assert server.docs_path.exists()
    

@pytest.mark.asyncio
async def test_get_capabilities():
    """Test get_capabilities returns expected structure."""
    server = SubstrateServer()
    capabilities = await server.get_capabilities()
    
    assert capabilities["role"] == "system_architect"
    assert "methodology" in capabilities["provides"]
    assert "atlas.md" in capabilities["documents"]


@pytest.mark.asyncio
async def test_substrate_base_class():
    """Test SubstrateMCP base class functionality."""
    
    class TestServer(SubstrateMCP):
        async def get_capabilities(self):
            return {"test": True}
    
    server = TestServer(
        name="test",
        version="1.0.0",
        description="Test server"
    )
    
    # Test response building
    response = server.create_response(
        success=True,
        data={"foo": "bar"},
        message="Test message"
    )
    
    assert response["success"] is True
    assert response["data"]["foo"] == "bar"
    assert response["message"] == "Test message"
    assert "timestamp" in response


def test_documentation_files_exist():
    """Test that all required documentation files exist."""
    docs_path = Path(__file__).parent.parent / "docs"
    
    assert (docs_path / "atlas.md").exists()
    assert (docs_path / "system-design.md").exists()
    assert (docs_path / "component-map.json").exists()
    
    # Verify component map is valid JSON
    with open(docs_path / "component-map.json", 'r') as f:
        data = json.load(f)
        assert "components" in data
        assert "substrate" in data["components"]


if __name__ == "__main__":
    # Run basic tests
    asyncio.run(test_substrate_server_initialization())
    asyncio.run(test_get_capabilities())
    asyncio.run(test_substrate_base_class())
    test_documentation_files_exist()
    print("All tests passed!")
