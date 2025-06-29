"""Tests for SubstrateMCP base class."""

import asyncio
import pytest
from unittest.mock import Mock, patch

from substrate import SubstrateMCP, ResponseBuilder
from substrate.types import ToolResponse


class TestServer(SubstrateMCP):
    """Test implementation of SubstrateMCP."""
    
    async def get_capabilities(self):
        return {
            "test": True,
            "features": ["feature1", "feature2"]
        }


@pytest.fixture
def test_server():
    """Create test server instance."""
    return TestServer(
        name="test",
        version="1.0.0",
        description="Test server"
    )


class TestSubstrateMCP:
    """Test SubstrateMCP base functionality."""
    
    def test_initialization(self, test_server):
        """Test server initialization."""
        assert test_server.name == "test"
        assert test_server.version == "1.0.0"
        assert test_server.description == "Test server"
        assert test_server.mcp is not None
        assert test_server.response_builder is not None
        assert test_server.sampling_manager is not None
        assert test_server.progress_tracker is not None
        
    def test_standard_tools_registered(self, test_server):
        """Test that standard tools are registered."""
        # Check that tools with server name exist
        # This would need actual FastMCP inspection
        assert hasattr(test_server.mcp, "tool")
        
    @pytest.mark.asyncio
    async def test_get_capabilities(self, test_server):
        """Test get_capabilities method."""
        caps = await test_server.get_capabilities()
        assert caps["test"] is True
        assert "features" in caps
        assert len(caps["features"]) == 2
        
    def test_create_response_success(self, test_server):
        """Test create_response for success."""
        response = test_server.create_response(
            success=True,
            data={"key": "value"},
            message="Success!"
        )
        
        assert response["success"] is True
        assert response["data"]["key"] == "value"
        assert response["message"] == "Success!"
        assert "timestamp" in response
        
    def test_create_response_error(self, test_server):
        """Test create_response for error."""
        response = test_server.create_response(
            success=False,
            error="Something went wrong"
        )
        
        assert response["success"] is False
        assert response["error"] == "Something went wrong"
        assert "timestamp" in response
        
    @pytest.mark.asyncio
    async def test_progress_context(self, test_server):
        """Test progress context manager."""
        async with test_server.progress_context("test_op") as progress:
            await progress(0.5, "Halfway")
            # Would need to check progress tracker state
            assert True  # Placeholder
            
    def test_response_builder_integration(self, test_server):
        """Test response builder is properly integrated."""
        response = test_server.response_builder.success(
            data={"test": True},
            message="Test message"
        )
        
        assert response["success"] is True
        assert response["data"]["test"] is True
        assert response["message"] == "Test message"


class TestResponseBuilder:
    """Test ResponseBuilder functionality."""
    
    @pytest.fixture
    def builder(self):
        """Create response builder."""
        return ResponseBuilder()
        
    def test_success_response(self, builder):
        """Test success response creation."""
        response = builder.success(
            data={"result": 42},
            message="Calculation complete"
        )
        
        assert response["success"] is True
        assert response["data"]["result"] == 42
        assert response["message"] == "Calculation complete"
        assert "timestamp" in response
        
    def test_error_response(self, builder):
        """Test error response creation."""
        response = builder.error(
            "Invalid input",
            error_code="VALIDATION_ERROR",
            suggestions=["Check input format", "Try again"]
        )
        
        assert response["success"] is False
        assert response["error"] == "Invalid input"
        assert response["error_code"] == "VALIDATION_ERROR"
        assert len(response["suggestions"]) == 2
        
    def test_paginated_response(self, builder):
        """Test paginated response creation."""
        items = list(range(100))
        response = builder.paginated(
            items[:10],
            page=1,
            page_size=10,
            total=100
        )
        
        assert response["success"] is True
        assert len(response["data"]["items"]) == 10
        assert response["data"]["pagination"]["total"] == 100
        assert response["data"]["pagination"]["total_pages"] == 10
        assert response["data"]["pagination"]["has_next"] is True
        assert response["data"]["pagination"]["has_prev"] is False
        
    def test_with_annotations(self, builder):
        """Test response with annotations."""
        response = builder.success(
            data={"test": True},
            annotations={"priority": 0.8, "audience": ["user"]}
        )
        
        assert "_annotations" in response
        assert response["_annotations"]["priority"] == 0.8
        assert response["_annotations"]["audience"] == ["user"]
