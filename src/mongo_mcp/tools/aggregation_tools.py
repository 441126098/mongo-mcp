"""Aggregation operation tools for MongoDB."""

from typing import List, Dict, Any, Optional
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId

from mongo_mcp.db import get_collection
from mongo_mcp.config import logger
from mongo_mcp.utils.json_encoder import clean_document_for_json


def aggregate_documents(
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
    if not database_name or not collection_name:
        msg = "Database name and collection name must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    if not isinstance(pipeline, list):
        msg = "Pipeline must be a list of stage dictionaries"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in pipeline stages if present
        processed_pipeline = _convert_pipeline_objectids(pipeline)
        
        # Execute aggregation
        if options:
            cursor = collection.aggregate(processed_pipeline, **options)
        else:
            cursor = collection.aggregate(processed_pipeline)
        
        # Process results
        results = []
        for doc in cursor:
            cleaned_doc = clean_document_for_json(doc)
            results.append(cleaned_doc)
        
        logger.info(f"Executed aggregation pipeline with {len(results)} results in {database_name}.{collection_name}")
        return results
    except PyMongoError as e:
        logger.error(f"Failed to execute aggregation pipeline in {database_name}.{collection_name}: {e}")
        raise


def distinct_values(
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
    if not database_name or not collection_name or not field:
        msg = "Database name, collection name, and field must be provided"
        logger.error(msg)
        raise ValueError(msg)
    
    try:
        collection = get_collection(database_name, collection_name)
        
        # Convert ObjectId strings in query if present
        if query:
            query = _convert_id_strings(query)
        
        # Get distinct values
        if query:
            distinct_vals = collection.distinct(field, query)
        else:
            distinct_vals = collection.distinct(field)
        
        # Clean results for JSON serialization
        cleaned_vals = []
        for val in distinct_vals:
            if isinstance(val, ObjectId):
                cleaned_vals.append(str(val))
            elif isinstance(val, dict):
                cleaned_vals.append(clean_document_for_json(val))
            else:
                cleaned_vals.append(val)
        
        logger.info(f"Found {len(cleaned_vals)} distinct values for field '{field}' in {database_name}.{collection_name}")
        return cleaned_vals
    except PyMongoError as e:
        logger.error(f"Failed to get distinct values for field '{field}' in {database_name}.{collection_name}: {e}")
        raise


def _convert_pipeline_objectids(pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert ObjectId strings in aggregation pipeline stages.
    
    Args:
        pipeline: Aggregation pipeline to process
        
    Returns:
        List[Dict[str, Any]]: Processed pipeline with ObjectIds converted
    """
    processed_pipeline = []
    
    for stage in pipeline:
        if isinstance(stage, dict):
            processed_stage = _convert_id_strings(stage)
            processed_pipeline.append(processed_stage)
        else:
            processed_pipeline.append(stage)
    
    return processed_pipeline


def _convert_id_strings(obj: Any) -> Any:
    """Recursively convert ObjectId strings to ObjectId objects.
    
    Args:
        obj: Object to process
        
    Returns:
        Any: Processed object with ObjectIds converted
    """
    if isinstance(obj, dict):
        converted = {}
        for key, value in obj.items():
            converted[key] = _convert_id_strings(value)
        return converted
    elif isinstance(obj, list):
        return [_convert_id_strings(item) for item in obj]
    elif isinstance(obj, str) and ObjectId.is_valid(obj):
        return ObjectId(obj)
    else:
        return obj 