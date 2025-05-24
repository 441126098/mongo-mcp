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


def find_documents(
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
            deleted = result.deleted_count
            logger.info(f"Deleted {deleted} documents from {database_name}.{collection_name}")
            
            return {"deleted_count": deleted}
        else:
            result = collection.delete_one(query)
            logger.info(f"Deleted {result.deleted_count} document from {database_name}.{collection_name}")
            
            return {"deleted_count": result.deleted_count}
    except PyMongoError as e:
        logger.error(f"Failed to delete document(s) from {database_name}.{collection_name}: {e}")
        raise


def _convert_id_strings(query: Dict[str, Any]) -> Dict[str, Any]:
    """Convert string '_id' values to ObjectId instances.
    
    Args:
        query: Query dictionary
        
    Returns:
        Dict[str, Any]: Query with converted ObjectId values
    """
    if "_id" in query and isinstance(query["_id"], str):
        try:
            query["_id"] = ObjectId(query["_id"])
        except Exception:
            # If not a valid ObjectId, leave as is
            pass
    
    # Handle $in operator
    if "_id" in query and isinstance(query["_id"], dict) and "$in" in query["_id"]:
        if isinstance(query["_id"]["$in"], list):
            try:
                query["_id"]["$in"] = [
                    ObjectId(id_str) if isinstance(id_str, str) else id_str
                    for id_str in query["_id"]["$in"]
                ]
            except Exception:
                # If not a valid ObjectId, leave as is
                pass
                
    return query


def _process_query_results(cursor) -> List[Dict[str, Any]]:
    """Process query results to handle ObjectId and other BSON types.
    
    Args:
        cursor: MongoDB cursor from find operation
        
    Returns:
        List[Dict[str, Any]]: Processed documents
    """
    result = []
    for doc in cursor:
        try:
            # 使用自定义函数处理文档，确保所有字段都可JSON序列化
            cleaned_doc = clean_document_for_json(doc)
            logger.info(f"Doc: {doc}")
            result.append(cleaned_doc)
        except Exception as e:
            logger.warning(f"Skipping document due to encoding issues: {str(e)}")
    return result 