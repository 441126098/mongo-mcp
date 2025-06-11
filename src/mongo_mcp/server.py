"""MCP server module for MongoDB operations."""

import signal
import sys
import logging
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP

from mongo_mcp.config import logger
from mongo_mcp.db import close_connection, get_client
from mongo_mcp.tools import (
    list_databases,
    list_collections,
    insert_document,
    find_documents,
    update_document,
    delete_document,
)
from mongo_mcp.utils.json_encoder import mongodb_json_serializer


# Set up MCP server
app = FastMCP(name="MongoDB MCP")

# Register MongoDB tools using the @app.tool() decorator approach
@app.tool()
def mcp_list_databases() -> List[str]:
    """List all databases in the MongoDB instance.
    
    Returns:
        List[str]: List of database names
    
    Raises:
        PyMongoError: If the operation fails
    """
    return list_databases()

@app.tool()  
def mcp_list_collections(database_name: str) -> List[str]:
    """List all collections in the specified database.
    
    Args:
        database_name: Name of the database
    
    Returns:
        List[str]: List of collection names
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    return list_collections(database_name)

@app.tool()
def mcp_insert_document(
    database_name: str, 
    collection_name: str, 
    document: Dict[str, Any]
) -> Dict[str, Any]:
    """Insert a document into the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        document: Document to insert (JSON-compatible dictionary)
    
    Returns:
        Dict[str, Any]: Result containing the inserted document's ID
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return insert_document(database_name, collection_name, document)

@app.tool()
def mcp_find_documents(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None,
    limit: int = 0
) -> List[Dict[str, Any]]:
    """Find documents in the specified collection matching the query.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        projection: MongoDB projection (fields to include/exclude)
        limit: Maximum number of documents to return (0 for no limit)
    
    Returns:
        List[Dict[str, Any]]: List of matching documents
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return find_documents(database_name, collection_name, query, projection, limit)

@app.tool()
def mcp_update_document(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    update_data: Dict[str, Any],
    upsert: bool = False,
    update_many: bool = False
) -> Dict[str, Any]:
    """Update document(s) in the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        update_data: MongoDB update document (must include operators like $set)
        upsert: Whether to insert if no document matches the query
        update_many: Whether to update all matching documents or just the first one
    
    Returns:
        Dict[str, Any]: Result of the update operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing or invalid
    """
    return update_document(database_name, collection_name, query, update_data, upsert, update_many)

@app.tool()
def mcp_delete_document(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    delete_many: bool = False
) -> Dict[str, Any]:
    """Delete document(s) from the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        delete_many: Whether to delete all matching documents or just the first one
    
    Returns:
        Dict[str, Any]: Result of the delete operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return delete_document(database_name, collection_name, query, delete_many)


# Set up signal handlers for graceful shutdown
def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info("Shutting down MCP server")
    close_connection()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def start_server() -> None:
    """Start the MCP server with stdio transport."""
    try:
        # 使用FastMCP的run方法，指定stdio传输方式
        app.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        close_connection()
        sys.exit(1)


if __name__ == "__main__":
    start_server() 