"""Main entry point for substrate MCP server."""

import asyncio
import logging
import sys

from substrate.server import server


async def main():
    """Run the substrate MCP server."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stderr
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Substrate MCP Server v2.0.0")
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Substrate server stopped")


if __name__ == "__main__":
    asyncio.run(main())
