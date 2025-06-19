"""Database-level operation tools for MongoDB."""

from typing import List, Dict, Any, Optional
from pymongo.errors import PyMongoError

from mongo_mcp.db import get_client, get_database
from mongo_mcp.config import logger


def list_databases() -> List[str]:
    """List all databases in the MongoDB instance.
    
    Returns:
        List[str]: List of database names
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        client = get_client()
        # Filter out system databases
        db_names = [
            db["name"] 
            for db in client.list_databases() 
            if db["name"] not in ["admin", "local", "config"]
        ]
        logger.info(f"Listed {len(db_names)} databases")
        return db_names
    except PyMongoError as e:
        logger.error(f"Failed to list databases: {e}")
        raise


def list_collections(database_name: str) -> List[str]:
    """List all collections in the specified database.
    
    Args:
        database_name: Name of the database
    
    Returns:
        List[str]: List of collection names
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    if not database_name:
        msg = "Database name must be provided"
        logger.error(msg)
        raise ValueError(msg)
        
    try:
        db = get_database(database_name)
        collection_names = db.list_collection_names()
        logger.info(f"Listed {len(collection_names)} collections in database '{database_name}'")
        return collection_names
    except PyMongoError as e:
        logger.error(f"Failed to list collections in database '{database_name}': {e}")
        raise


def create_database(
    database_name: str, 
    initial_collection: str = "init", 
    initial_document: Dict[str, Any] = None
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
    if not database_name:
        msg = "Database name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if initial_document is None:
        initial_document = {"_created": "Database initialization document"}
    
    try:
        db = get_database(database_name)
        collection = db[initial_collection]
        result = collection.insert_one(initial_document)
        
        logger.info(f"Created database '{database_name}' with initial collection '{initial_collection}'")
        return {
            "database_name": database_name,
            "initial_collection": initial_collection,
            "inserted_id": str(result.inserted_id),
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to create database '{database_name}': {e}")
        raise


def drop_database(database_name: str) -> Dict[str, Any]:
    """Delete an entire database and all its collections.
    
    Args:
        database_name: Name of the database to delete
    
    Returns:
        Dict[str, Any]: Result of the deletion operation
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    if not database_name:
        msg = "Database name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        client = get_client()
        client.drop_database(database_name)
        
        logger.info(f"Dropped database '{database_name}'")
        return {
            "database_name": database_name,
            "success": True,
            "message": f"Database '{database_name}' has been deleted"
        }
    except PyMongoError as e:
        logger.error(f"Failed to drop database '{database_name}': {e}")
        raise


def get_database_stats(database_name: str) -> Dict[str, Any]:
    """Get statistics information for a database.
    
    Args:
        database_name: Name of the database
    
    Returns:
        Dict[str, Any]: Database statistics
    
    Raises:
        PyMongoError: If the operation fails
        ValueError: If database name is not provided
    """
    if not database_name:
        msg = "Database name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        db = get_database(database_name)
        stats = db.command("dbStats")
        
        # Clean up the stats for JSON serialization
        clean_stats = {
            "database": stats.get("db"),
            "collections": stats.get("collections", 0),
            "views": stats.get("views", 0),
            "objects": stats.get("objects", 0),
            "avg_obj_size": stats.get("avgObjSize", 0),
            "data_size": stats.get("dataSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "indexes": stats.get("indexes", 0),
            "index_size": stats.get("indexSize", 0),
            "file_size": stats.get("fileSize", 0),
        }
        
        logger.info(f"Retrieved stats for database '{database_name}'")
        return clean_stats
    except PyMongoError as e:
        logger.error(f"Failed to get stats for database '{database_name}': {e}")
        raise


def create_collection(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        db = get_database(database_name)
        
        if options:
            collection = db.create_collection(collection_name, **options)
        else:
            collection = db.create_collection(collection_name)
        
        logger.info(f"Created collection '{collection_name}' in database '{database_name}'")
        return {
            "database_name": database_name,
            "collection_name": collection_name,
            "options": options or {},
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to create collection '{collection_name}' in database '{database_name}': {e}")
        raise


def drop_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        db = get_database(database_name)
        db.drop_collection(collection_name)
        
        logger.info(f"Dropped collection '{collection_name}' from database '{database_name}'")
        return {
            "database_name": database_name,
            "collection_name": collection_name,
            "success": True,
            "message": f"Collection '{collection_name}' has been deleted"
        }
    except PyMongoError as e:
        logger.error(f"Failed to drop collection '{collection_name}' from database '{database_name}': {e}")
        raise


def rename_collection(database_name: str, old_name: str, new_name: str) -> Dict[str, Any]:
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
    if not database_name or not old_name or not new_name:
        msg = "Database name, old name, and new name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        db = get_database(database_name)
        collection = db[old_name]
        collection.rename(new_name)
        
        logger.info(f"Renamed collection '{old_name}' to '{new_name}' in database '{database_name}'")
        return {
            "database_name": database_name,
            "old_name": old_name,
            "new_name": new_name,
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to rename collection '{old_name}' to '{new_name}' in database '{database_name}': {e}")
        raise


def get_collection_stats(database_name: str, collection_name: str) -> Dict[str, Any]:
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        db = get_database(database_name)
        stats = db.command("collStats", collection_name)
        
        # Clean up the stats for JSON serialization
        clean_stats = {
            "ns": stats.get("ns"),
            "count": stats.get("count", 0),
            "size": stats.get("size", 0),
            "avg_obj_size": stats.get("avgObjSize", 0),
            "storage_size": stats.get("storageSize", 0),
            "capped": stats.get("capped", False),
            "nindexes": stats.get("nindexes", 0),
            "total_index_size": stats.get("totalIndexSize", 0),
            "index_sizes": stats.get("indexSizes", {}),
        }
        
        logger.info(f"Retrieved stats for collection '{collection_name}' in database '{database_name}'")
        return clean_stats
    except PyMongoError as e:
        logger.error(f"Failed to get stats for collection '{collection_name}' in database '{database_name}': {e}")
        raise 