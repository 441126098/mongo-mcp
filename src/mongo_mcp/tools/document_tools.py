"""Document-level operation tools for MongoDB."""

from typing import List, Dict, Any, Optional, Union
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

from mongo_mcp.db import get_collection
from mongo_mcp.config import logger
from mongo_mcp.utils.json_encoder import clean_document_for_json


def insert_document(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not document or not isinstance(document, dict):
        msg = "Document must be a non-empty dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        result = collection.insert_one(document)
        
        inserted_id = str(result.inserted_id)
        logger.info(f"Inserted document with ID '{inserted_id}' into {database_name}.{collection_name}")
        
        return {"inserted_id": inserted_id, "success": True}
    except PyMongoError as e:
        logger.error(f"Failed to insert document into {database_name}.{collection_name}: {e}")
        raise


def insert_many_documents(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not documents or not isinstance(documents, list):
        msg = "Documents must be a non-empty list"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        result = collection.insert_many(documents, ordered=ordered)
        
        inserted_ids = [str(oid) for oid in result.inserted_ids]
        logger.info(f"Inserted {len(inserted_ids)} documents into {database_name}.{collection_name}")
        
        return {
            "inserted_ids": inserted_ids,
            "inserted_count": len(inserted_ids),
            "success": True
        }
    except PyMongoError as e:
        logger.error(f"Failed to insert documents into {database_name}.{collection_name}: {e}")
        raise


def find_documents(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict):
        msg = "Query must be a dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        # Execute query
        cursor = collection.find(query, projection=projection)
        
        # Apply sort if provided
        if sort:
            cursor = cursor.sort(list(sort.items()))
        
        # Apply limit if provided
        if limit > 0:
            cursor = cursor.limit(limit)
        
        # Convert to list and ensure ObjectId is converted to string
        documents = _process_query_results(cursor)
        
        result_count = len(documents)
        logger.info(f"Found {result_count} documents in {database_name}.{collection_name}")
        
        return documents
    except PyMongoError as e:
        logger.error(f"Failed to find documents in {database_name}.{collection_name}: {e}")
        raise


def find_one_document(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict):
        msg = "Query must be a dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        # Execute query
        document = collection.find_one(query, projection=projection)
        
        if document:
            document = clean_document_for_json(document)
            logger.info(f"Found document in {database_name}.{collection_name}")
        else:
            logger.info(f"No document found in {database_name}.{collection_name}")
        
        return document
    except PyMongoError as e:
        logger.error(f"Failed to find document in {database_name}.{collection_name}: {e}")
        raise


def count_documents(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict):
        msg = "Query must be a dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        count = collection.count_documents(query)
        logger.info(f"Counted {count} documents in {database_name}.{collection_name}")
        
        return count
    except PyMongoError as e:
        logger.error(f"Failed to count documents in {database_name}.{collection_name}: {e}")
        raise


def update_document(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict) or not isinstance(update_data, dict):
        msg = "Query and update_data must be dictionaries"
        logger.error(msg)
        raise ValueError(msg)
    
    # Check if update_data contains MongoDB operators
    if not any(key.startswith("$") for key in update_data):
        # If not, wrap it in $set
        update_data = {"$set": update_data}
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        # Execute update
        if update_many:
            result = collection.update_many(query, update_data, upsert=upsert)
            matched = result.matched_count
            modified = result.modified_count
            logger.info(f"Updated {modified} of {matched} documents in {database_name}.{collection_name}")
            
            return {
                "matched_count": matched,
                "modified_count": modified,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
        else:
            result = collection.update_one(query, update_data, upsert=upsert)
            logger.info(f"Updated document in {database_name}.{collection_name}")
            
            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "upserted_id": str(result.upserted_id) if result.upserted_id else None
            }
    except PyMongoError as e:
        logger.error(f"Failed to update document(s) in {database_name}.{collection_name}: {e}")
        raise


def replace_document(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict) or not isinstance(replacement, dict):
        msg = "Query and replacement must be dictionaries"
        logger.error(msg)
        raise ValueError(msg)
    
    # Check if replacement contains update operators (which it shouldn't)
    if any(key.startswith("$") for key in replacement):
        msg = "Replacement document should not contain update operators"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        # Execute replace
        result = collection.replace_one(query, replacement, upsert=upsert)
        
        logger.info(f"Replaced document in {database_name}.{collection_name}")
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "upserted_id": str(result.upserted_id) if result.upserted_id else None
        }
    except PyMongoError as e:
        logger.error(f"Failed to replace document in {database_name}.{collection_name}: {e}")
        raise


def delete_document(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(query, dict):
        msg = "Query must be a dictionary"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in the query if present
        query = _convert_id_strings(query)
        
        # Execute delete
        if delete_many:
            result = collection.delete_many(query)
            logger.info(f"Deleted {result.deleted_count} documents from {database_name}.{collection_name}")
        else:
            result = collection.delete_one(query)
            logger.info(f"Deleted {result.deleted_count} document from {database_name}.{collection_name}")
        
        return {"deleted_count": result.deleted_count}
    except PyMongoError as e:
        logger.error(f"Failed to delete document(s) from {database_name}.{collection_name}: {e}")
        raise


def _convert_id_strings(query: Dict[str, Any]) -> Dict[str, Any]:
    """Convert string representations of ObjectId to actual ObjectId objects.
    
    This function recursively processes a query dictionary and converts
    any string values that look like MongoDB ObjectIds into actual ObjectId objects.
    
    Args:
        query: The query dictionary to process
        
    Returns:
        Dict[str, Any]: The processed query with ObjectIds converted
    """
    if not isinstance(query, dict):
        return query
        
    converted = {}
    for key, value in query.items():
        if isinstance(value, str) and ObjectId.is_valid(value):
            # Convert string ObjectId to ObjectId object
            converted[key] = ObjectId(value)
        elif isinstance(value, dict):
            # Recursively process nested dictionaries
            converted[key] = _convert_id_strings(value)
        elif isinstance(value, list):
            # Process lists that might contain ObjectId strings
            converted[key] = [
                ObjectId(item) if isinstance(item, str) and ObjectId.is_valid(item) else item
                for item in value
            ]
        else:
            converted[key] = value
    
    return converted


def _process_query_results(cursor) -> List[Dict[str, Any]]:
    """Process query results and convert ObjectIds to strings for JSON serialization.
    
    Args:
        cursor: MongoDB cursor object
        
    Returns:
        List[Dict[str, Any]]: List of processed documents
    """
    documents = []
    for doc in cursor:
        # Use the clean_document_for_json utility
        cleaned_doc = clean_document_for_json(doc)
        documents.append(cleaned_doc)
    
    return documents 