"""Main entry point for substrate MCP server."""

import asyncio
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

async def main():
    """Run the substrate server."""
    # Import here to avoid circular imports
    from substrate.server import server
    
    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
