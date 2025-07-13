"""Main entry point for substrate MCP server."""

import logging
import sys

from substrate.server import SubstrateServer


def main():
    """Run the substrate MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Substrate MCP Server v1.0.0")
        server = SubstrateServer()
        server.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Substrate server stopped")


if __name__ == "__main__":
    main()
