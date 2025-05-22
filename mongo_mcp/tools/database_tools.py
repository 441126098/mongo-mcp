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