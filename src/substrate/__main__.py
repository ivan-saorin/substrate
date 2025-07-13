"""Main entry point for substrate MCP server."""

import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def main():
    """Run the substrate server."""
    # Import here to avoid circular imports
    from substrate.server import SubstrateServer
    
    # Create and run the server
    server = SubstrateServer()
    server.run()

if __name__ == "__main__":
    main()
