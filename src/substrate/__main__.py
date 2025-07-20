"""
Main entry point for substrate MCP server
"""
import sys
import logging

# Setup logging to stderr (CRITICAL: never stdout for MCP!)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)

logger = logging.getLogger(__name__)


def main():
    """Run the substrate server - NO asyncio.run() with FastMCP!"""
    try:
        # Import here to avoid circular imports
        from .server import create_substrate_instance
        
        logger.info("Starting substrate server from __main__")
        server = create_substrate_instance()
        server.run()
        
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
