"""Main entry point for the mongo-mcp package."""

from mongo_mcp.server import start_server

def main():
    from mongo_mcp.server import start_server
    start_server()

if __name__ == "__main__":
    start_server() 