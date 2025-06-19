"""Index management tools for MongoDB."""

from typing import List, Dict, Any, Optional, Tuple
from pymongo.errors import PyMongoError
from pymongo import TEXT, ASCENDING, DESCENDING

from mongo_mcp.db import get_collection
from mongo_mcp.config import logger


def list_indexes(database_name: str, collection_name: str) -> List[Dict[str, Any]]:
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        indexes = list(collection.list_indexes())
        
        # Clean up index information for JSON serialization
        clean_indexes = []
        for index in indexes:
            clean_index = {
                "name": index.get("name"),
                "key": dict(index.get("key", {})),
                "unique": index.get("unique", False),
                "sparse": index.get("sparse", False),
                "background": index.get("background", False),
                "text_index_version": index.get("textIndexVersion"),
                "2dsphere_index_version": index.get("2dsphereIndexVersion"),
                "expire_after_seconds": index.get("expireAfterSeconds"),
                "weights": index.get("weights"),
                "default_language": index.get("default_language"),
                "language_override": index.get("language_override"),
            }
            # Remove None values
            clean_index = {k: v for k, v in clean_index.items() if v is not None}
            clean_indexes.append(clean_index)
        
        logger.info(f"Listed {len(clean_indexes)} indexes for {database_name}.{collection_name}")
        return clean_indexes
    except PyMongoError as e:
        logger.error(f"Failed to list indexes for {database_name}.{collection_name}: {e}")
        raise


def create_index(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not keys or not isinstance(keys, dict):
        msg = "Keys must be a non-empty dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert keys to proper format
        index_keys = []
        for field, direction in keys.items():
            if direction == 1 or direction == "asc" or direction == "ascending":
                index_keys.append((field, ASCENDING))
            elif direction == -1 or direction == "desc" or direction == "descending":
                index_keys.append((field, DESCENDING))
            elif direction == "text":
                index_keys.append((field, TEXT))
            else:
                index_keys.append((field, direction))
        
        # Create index with options
        if options:
            index_name = collection.create_index(index_keys, **options)
        else:
            index_name = collection.create_index(index_keys)
        
        logger.info(f"Created index '{index_name}' on {database_name}.{collection_name}")
        return {
            "index_name": index_name,
            "keys": keys,
            "options": options or {},
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to create index on {database_name}.{collection_name}: {e}")
        raise


def create_text_index(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not fields or not isinstance(fields, list):
        msg = "Fields must be a non-empty list"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Create text index specification
        index_keys = [(field, TEXT) for field in fields]
        
        # Create text index with options
        if options:
            index_name = collection.create_index(index_keys, **options)
        else:
            index_name = collection.create_index(index_keys)
        
        logger.info(f"Created text index '{index_name}' on fields {fields} in {database_name}.{collection_name}")
        return {
            "index_name": index_name,
            "fields": fields,
            "type": "text",
            "options": options or {},
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to create text index on {database_name}.{collection_name}: {e}")
        raise


def create_compound_index(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not field_specs or not isinstance(field_specs, list):
        msg = "Field specifications must be a non-empty list"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert field specifications to proper format
        index_keys = []
        for field_spec in field_specs:
            if not isinstance(field_spec, (list, tuple)) or len(field_spec) != 2:
                raise ValueError("Each field specification must be a (field_name, direction) tuple")
            
            field, direction = field_spec
            if direction == 1 or direction == "asc" or direction == "ascending":
                index_keys.append((field, ASCENDING))
            elif direction == -1 or direction == "desc" or direction == "descending":
                index_keys.append((field, DESCENDING))
            elif direction == "text":
                index_keys.append((field, TEXT))
            else:
                index_keys.append((field, direction))
        
        # Create compound index with options
        if options:
            index_name = collection.create_index(index_keys, **options)
        else:
            index_name = collection.create_index(index_keys)
        
        logger.info(f"Created compound index '{index_name}' on {database_name}.{collection_name}")
        return {
            "index_name": index_name,
            "field_specs": field_specs,
            "type": "compound",
            "options": options or {},
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to create compound index on {database_name}.{collection_name}: {e}")
        raise


def drop_index(
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
    if not database_name or not collection_name or not index_name:
        msg = "Database name, collection name, and index name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    # Prevent dropping the default _id index
    if index_name == "_id_":
        msg = "Cannot drop the default _id index"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        collection.drop_index(index_name)
        
        logger.info(f"Dropped index '{index_name}' from {database_name}.{collection_name}")
        return {
            "index_name": index_name,
            "success": True,
            "message": f"Index '{index_name}' has been dropped"
        }
    except PyMongoError as e:
        logger.error(f"Failed to drop index '{index_name}' from {database_name}.{collection_name}: {e}")
        raise


def reindex_collection(database_name: str, collection_name: str) -> Dict[str, Any]:
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Use the reIndex command
        result = collection.database.command("reIndex", collection_name)
        
        logger.info(f"Reindexed collection {database_name}.{collection_name}")
        return {
            "collection": collection_name,
            "success": True,
            "result": result,
            "message": f"All indexes for collection '{collection_name}' have been rebuilt"
        }
    except PyMongoError as e:
        logger.error(f"Failed to reindex collection {database_name}.{collection_name}: {e}")
        raise 