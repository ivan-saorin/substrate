"""
Substrate MCP Server - Wrapper for FastMCP implementation
This file provides compatibility for complex initialization scenarios
"""
import sys
import logging
from .server_fastmcp import mcp

# Setup logging to stderr (never stdout for MCP!)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


class SubstrateServer:
    """Wrapper class for FastMCP server - provides initialization hooks"""
    
    def __init__(self):
        logger.info("SubstrateServer wrapper initialized")
    
    def run(self):
        """Run the FastMCP server"""
        try:
            logger.info("Starting substrate server via wrapper")
            mcp.run()
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            sys.exit(1)


def create_substrate_instance():
    """Factory function to create substrate instance"""
    return SubstrateServer()


if __name__ == "__main__":
    server = create_substrate_instance()
    server.run()
