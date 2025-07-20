"""
Substrate Base MCP Server - FastMCP Implementation
Main implementation using FastMCP with dynamic feature loading
"""
import os
import sys
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from fastmcp import FastMCP

# Setup logging to stderr (CRITICAL: never stdout for MCP!)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Import shared instances - created once, used everywhere
from .shared.instances import (
    INSTANCE_TYPE,
    response_builder,
    navigation_engine,
    model_registry
)

# Import instance configuration
from .shared.instance import get_instance_config, should_load_feature

# Create FastMCP instance
mcp = FastMCP(INSTANCE_TYPE)
logger.info(f"Created FastMCP instance for {INSTANCE_TYPE}")


def get_instance_documentation() -> Dict[str, str]:
    """Get instance-specific documentation"""
    config = get_instance_config(INSTANCE_TYPE)
    return config.get("documentation", {
        "summary": f"I am {INSTANCE_TYPE}, part of the Atlas system.",
        "usage": "Part of the cognitive manipulation system."
    })


def get_initial_suggestions() -> List[Any]:
    """Get initial suggestions based on instance type"""
    if INSTANCE_TYPE in ["substrate", "atlas"]:
        return [
            response_builder.suggest_next(
                f"{INSTANCE_TYPE}_documentation",
                "Read ASR v2.0 - Complete architecture",
                doc_type="asr-v2"
            ),
            response_builder.suggest_next(
                f"{INSTANCE_TYPE}_show_workflows",
                "Discover available workflows"
            )
        ]
    elif INSTANCE_TYPE == "tloen":
        return [
            response_builder.suggest_next(
                "tloen_list_refs",
                "View available site formats",
                prefix="sites"
            )
        ]
    elif INSTANCE_TYPE == "uqbar":
        return [
            response_builder.suggest_next(
                "uqbar_list_refs",
                "View available personas",
                prefix="personas"
            )
        ]
    return []


# Base tools - all instances have these

@mcp.tool(name=INSTANCE_TYPE)
async def get_server_info() -> Dict[str, Any]:
    """Get server capabilities and documentation"""
    documentation = get_instance_documentation()
    
    return response_builder.build(
        data={
            "name": INSTANCE_TYPE,
            "version": "2.0.0",
            "description": get_instance_config(INSTANCE_TYPE).get("description", ""),
            "documentation": documentation,
            "model_registry": {
                "providers": list(set(m.provider.value for m in model_registry.models.values())),
                "models": len(model_registry.models)
            }
        },
        tool=INSTANCE_TYPE,
        message=f"{INSTANCE_TYPE.upper()} server ready. {documentation['summary']}",
        suggestions=get_initial_suggestions()
    )


@mcp.tool(name=f"{INSTANCE_TYPE}_sampling_callback")
async def sampling_callback(request_id: str, response: str) -> Dict[str, Any]:
    """Handle sampling callback responses"""
    return response_builder.build(
        data={
            "request_id": request_id,
            "response": response,
            "status": "received"
        },
        tool=f"{INSTANCE_TYPE}_sampling_callback",
        message="Sampling response recorded."
    )


# Dynamic feature loading
def load_features():
    """Dynamically load and register features based on instance configuration"""
    logger.info(f"Loading features for {INSTANCE_TYPE}")
    
    features_loaded = []
    
    # Documentation feature
    if should_load_feature(INSTANCE_TYPE, "documentation"):
        try:
            from .features.documentation.tool import register_documentation_tools
            tools = register_documentation_tools(mcp)
            features_loaded.append(("documentation", len(tools)))
            logger.info(f"Loaded documentation feature with {len(tools)} tools")
        except Exception as e:
            logger.error(f"Failed to load documentation feature: {e}", exc_info=True)
    
    # References feature
    if should_load_feature(INSTANCE_TYPE, "references"):
        try:
            from .features.references.tool import register_reference_tools
            tools = register_reference_tools(mcp)
            features_loaded.append(("references", len(tools)))
            logger.info(f"Loaded references feature with {len(tools)} tools")
        except Exception as e:
            logger.error(f"Failed to load references feature: {e}", exc_info=True)
    
    # Execution feature
    if should_load_feature(INSTANCE_TYPE, "execution"):
        try:
            from .features.execution.tool import register_execution_tools
            tools = register_execution_tools(mcp)
            features_loaded.append(("execution", len(tools)))
            logger.info(f"Loaded execution feature with {len(tools)} tools")
        except Exception as e:
            logger.error(f"Failed to load execution feature: {e}", exc_info=True)
    
    # Workflow navigation feature
    if should_load_feature(INSTANCE_TYPE, "workflows"):
        try:
            from .features.workflow_navigation.tool import register_workflow_tools
            tools = register_workflow_tools(mcp)
            features_loaded.append(("workflows", len(tools)))
            logger.info(f"Loaded workflow navigation feature with {len(tools)} tools")
        except Exception as e:
            logger.error(f"Failed to load workflow navigation feature: {e}", exc_info=True)
    
    # Summary
    total_tools = sum(count for _, count in features_loaded)
    logger.info(f"Loaded {len(features_loaded)} features with {total_tools} tools total")
    
    return features_loaded


# Load all features at startup
features = load_features()
logger.info(f"{INSTANCE_TYPE} server initialized with features: {features}")


# Main entry point
def main():
    """Main entry point - NEVER use asyncio.run() with FastMCP!"""
    try:
        logger.info(f"Starting {INSTANCE_TYPE} FastMCP server")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server runtime error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
