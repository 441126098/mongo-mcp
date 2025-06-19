"""MCP server module for MongoDB operations."""

import signal
import sys
import logging
from typing import Dict, Any, List, Optional, Tuple

from fastmcp import FastMCP

from mongo_mcp.config import logger
from mongo_mcp.db import close_connection, get_client
from mongo_mcp.tools import (
    # Database management tools
    list_databases,
    list_collections,
    create_database,
    drop_database,
    get_database_stats,
    create_collection,
    drop_collection,
    rename_collection,
    get_collection_stats,
    
    # Document CRUD operations
    insert_document,
    insert_many_documents,
    find_documents,
    find_one_document,
    count_documents,
    update_document,
    replace_document,
    delete_document,
    
    # Index management tools
    list_indexes,
    create_index,
    create_text_index,
    create_compound_index,
    drop_index,
    reindex_collection,
    
    # Aggregation operations
    aggregate_documents,
    distinct_values,
    
    # Administrative and monitoring tools
    get_server_status,
    get_replica_set_status,
    ping_database,
    test_mongodb_connection,
    get_connection_details,
)
from mongo_mcp.utils.json_encoder import mongodb_json_serializer


# Set up MCP server
app = FastMCP(name="MongoDB MCP")

# Register MongoDB tools using the @app.tool() decorator approach

# Database management tools
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
def mcp_create_database(
    database_name: str,
    initial_collection: str = "init",
    initial_document: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new database by inserting an initial document.
    
    MongoDB creates databases implicitly when the first document is inserted.
    
    Args:
        database_name: Name of the database to create
        initial_collection: Name of the initial collection
        initial_document: Initial document to insert
    
    Returns:
        Dict[str, Any]: Result of the creation operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    return create_database(database_name, initial_collection, initial_document)

@app.tool()
def mcp_drop_database(database_name: str) -> Dict[str, Any]:
    """Delete an entire database and all its collections.
    
    Args:
        database_name: Name of the database to delete
    
    Returns:
        Dict[str, Any]: Result of the deletion operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    return drop_database(database_name)

@app.tool()
def mcp_get_database_stats(database_name: str) -> Dict[str, Any]:
    """Get statistics information for a database.
    
    Args:
        database_name: Name of the database
    
    Returns:
        Dict[str, Any]: Database statistics
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    return get_database_stats(database_name)

@app.tool()
def mcp_create_collection(
    database_name: str,
    collection_name: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new collection with optional settings.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection to create
        options: Collection options (e.g., capped, size, max)
    
    Returns:
        Dict[str, Any]: Result of the creation operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return create_collection(database_name, collection_name, options)

@app.tool()
def mcp_drop_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
    """Delete a collection from the database.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection to delete
    
    Returns:
        Dict[str, Any]: Result of the deletion operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return drop_collection(database_name, collection_name)

@app.tool()
def mcp_rename_collection(
    database_name: str,
    old_name: str,
    new_name: str
) -> Dict[str, Any]:
    """Rename a collection.
    
    Args:
        database_name: Name of the database
        old_name: Current name of the collection
        new_name: New name for the collection
    
    Returns:
        Dict[str, Any]: Result of the rename operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return rename_collection(database_name, old_name, new_name)

@app.tool()
def mcp_get_collection_stats(database_name: str, collection_name: str) -> Dict[str, Any]:
    """Get statistics information for a collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
    
    Returns:
        Dict[str, Any]: Collection statistics
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return get_collection_stats(database_name, collection_name)

# Document CRUD operations
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
def mcp_insert_many_documents(
    database_name: str,
    collection_name: str,
    documents: List[Dict[str, Any]],
    ordered: bool = True
) -> Dict[str, Any]:
    """Insert multiple documents into the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        documents: List of documents to insert
        ordered: Whether to perform ordered or unordered inserts
    
    Returns:
        Dict[str, Any]: Result containing the inserted document IDs
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return insert_many_documents(database_name, collection_name, documents, ordered)

@app.tool()
def mcp_find_documents(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None,
    limit: int = 0,
    sort: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Find documents in the specified collection matching the query.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        projection: MongoDB projection (fields to include/exclude)
        limit: Maximum number of documents to return (0 for no limit)
        sort: MongoDB sort specification
    
    Returns:
        List[Dict[str, Any]]: List of matching documents
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return find_documents(database_name, collection_name, query, projection, limit, sort)

@app.tool()
def mcp_find_one_document(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    projection: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Find a single document in the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        projection: MongoDB projection (fields to include/exclude)
    
    Returns:
        Optional[Dict[str, Any]]: The found document or None
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return find_one_document(database_name, collection_name, query, projection)

@app.tool()
def mcp_count_documents(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any]
) -> int:
    """Count documents matching the query in the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
    
    Returns:
        int: Number of matching documents
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return count_documents(database_name, collection_name, query)

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
def mcp_replace_document(
    database_name: str,
    collection_name: str,
    query: Dict[str, Any],
    replacement: Dict[str, Any],
    upsert: bool = False
) -> Dict[str, Any]:
    """Replace a single document in the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        query: MongoDB query filter
        replacement: Replacement document (should not contain update operators)
        upsert: Whether to insert if no document matches the query
    
    Returns:
        Dict[str, Any]: Result of the replace operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing or invalid
    """
    return replace_document(database_name, collection_name, query, replacement, upsert)

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

# Index management tools
@app.tool()
def mcp_list_indexes(database_name: str, collection_name: str) -> List[Dict[str, Any]]:
    """List all indexes for the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
    
    Returns:
        List[Dict[str, Any]]: List of index information
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return list_indexes(database_name, collection_name)

@app.tool()
def mcp_create_index(
    database_name: str,
    collection_name: str,
    keys: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create an index on the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        keys: Index key specification (e.g., {"field": 1} for ascending)
        options: Index options (unique, sparse, background, etc.)
    
    Returns:
        Dict[str, Any]: Result of the index creation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return create_index(database_name, collection_name, keys, options)

@app.tool()
def mcp_create_text_index(
    database_name: str,
    collection_name: str,
    fields: List[str],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a text search index on the specified fields.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        fields: List of field names to include in text index
        options: Text index options (weights, default_language, etc.)
    
    Returns:
        Dict[str, Any]: Result of the index creation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return create_text_index(database_name, collection_name, fields, options)

@app.tool()
def mcp_create_compound_index(
    database_name: str,
    collection_name: str,
    field_specs: List[Tuple[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a compound index on multiple fields.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        field_specs: List of (field_name, direction) tuples
        options: Index options (unique, sparse, background, etc.)
    
    Returns:
        Dict[str, Any]: Result of the index creation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return create_compound_index(database_name, collection_name, field_specs, options)

@app.tool()
def mcp_drop_index(
    database_name: str,
    collection_name: str,
    index_name: str
) -> Dict[str, Any]:
    """Drop an index from the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        index_name: Name of the index to drop
    
    Returns:
        Dict[str, Any]: Result of the index drop operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return drop_index(database_name, collection_name, index_name)

@app.tool()
def mcp_reindex_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
    """Rebuild all indexes for the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
    
    Returns:
        Dict[str, Any]: Result of the reindex operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return reindex_collection(database_name, collection_name)

# Aggregation operations
@app.tool()
def mcp_aggregate_documents(
    database_name: str,
    collection_name: str,
    pipeline: List[Dict[str, Any]],
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """Execute an aggregation pipeline on the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        pipeline: MongoDB aggregation pipeline (list of stage dictionaries)
        options: Aggregation options (allowDiskUse, maxTimeMS, etc.)
    
    Returns:
        List[Dict[str, Any]]: Aggregation results
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return aggregate_documents(database_name, collection_name, pipeline, options)

@app.tool()
def mcp_distinct_values(
    database_name: str,
    collection_name: str,
    field: str,
    query: Optional[Dict[str, Any]] = None
) -> List[Any]:
    """Get distinct values for a field in the specified collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        field: Field name to get distinct values for
        query: Optional query filter to limit documents
    
    Returns:
        List[Any]: List of distinct values
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If required parameters are missing
    """
    return distinct_values(database_name, collection_name, field, query)

# Administrative and monitoring tools
@app.tool()
def mcp_get_server_status() -> Dict[str, Any]:
    """Get MongoDB server status information.
    
    Returns:
        Dict[str, Any]: Server status information
    
    Raises:
        PyMongoError: If the operation fails
    """
    return get_server_status()

@app.tool()
def mcp_get_replica_set_status() -> Optional[Dict[str, Any]]:
    """Get replica set status information if applicable.
    
    Returns:
        Optional[Dict[str, Any]]: Replica set status or None if not in replica set
    
    Raises:
        PyMongoError: If the operation fails
    """
    return get_replica_set_status()

@app.tool()
def mcp_ping_database(database_name: Optional[str] = None) -> Dict[str, Any]:
    """Test database connection and get basic information.
    
    Args:
        database_name: Optional database name to ping specific database
    
    Returns:
        Dict[str, Any]: Connection status and basic information
    
    Raises:
        PyMongoError: If the operation fails
    """
    return ping_database(database_name)

@app.tool()
def mcp_test_mongodb_connection() -> Dict[str, Any]:
    """Comprehensive MongoDB connection test.
    
    Returns:
        Dict[str, Any]: Detailed connection test results
    
    Raises:
        PyMongoError: If the operation fails
    """
    return test_mongodb_connection()

@app.tool()
def mcp_get_connection_details() -> Dict[str, Any]:
    """Get detailed MongoDB connection information.
    
    Returns:
        Dict[str, Any]: Connection details and configuration
    
    Raises:
        PyMongoError: If the operation fails
    """
    return get_connection_details()

# Collect all registered tools for logging
mongo_tools = [
    # Database management tools
    mcp_list_databases,
    mcp_list_collections,
    mcp_create_database,
    mcp_drop_database,
    mcp_get_database_stats,
    mcp_create_collection,
    mcp_drop_collection,
    mcp_rename_collection,
    mcp_get_collection_stats,
    
    # Document CRUD operations
    mcp_insert_document,
    mcp_insert_many_documents,
    mcp_find_documents,
    mcp_find_one_document,
    mcp_count_documents,
    mcp_update_document,
    mcp_replace_document,
    mcp_delete_document,
    
    # Index management tools
    mcp_list_indexes,
    mcp_create_index,
    mcp_create_text_index,
    mcp_create_compound_index,
    mcp_drop_index,
    mcp_reindex_collection,
    
    # Aggregation operations
    mcp_aggregate_documents,
    mcp_distinct_values,
    
    # Administrative and monitoring tools
    mcp_get_server_status,
    mcp_get_replica_set_status,
    mcp_ping_database,
    mcp_test_mongodb_connection,
    mcp_get_connection_details,
]

logger.info(f"Registered {len(mongo_tools)} MongoDB tools with MCP server")


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