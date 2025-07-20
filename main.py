"""Main entry point for substrate server"""
import logging
import os
import sys

# Add src to path before imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from substrate.server_fastmcp import SubstrateServer


def main():
    """Run the substrate server"""
    # Configure logging
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run server
    server = SubstrateServer()
    
    try:
        server.run()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
