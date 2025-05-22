"""Tests for MongoDB tools."""

import os
import pytest
from unittest.mock import MagicMock, patch

from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from bson.objectid import ObjectId

from mongo_mcp.tools.database_tools import list_databases, list_collections
from mongo_mcp.tools.document_tools import (
    insert_document,
    find_documents,
    update_document,
    delete_document,
)


# Mock MongoDB client for testing
@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client for testing."""
    # Create mock objects
    mock_client = MagicMock(spec=MongoClient)
    mock_db = MagicMock(spec=Database)
    mock_collection = MagicMock(spec=Collection)
    
    # Set up mock return values
    mock_client.list_databases.return_value = [
        {"name": "test_db", "sizeOnDisk": 1000},
        {"name": "admin", "sizeOnDisk": 1000},
    ]
    mock_client.__getitem__.return_value = mock_db
    mock_db.list_collection_names.return_value = ["test_collection"]
    mock_db.__getitem__.return_value = mock_collection
    
    # Mock ObjectId
    mock_id = ObjectId("000000000000000000000000")
    
    # Mock insert_one
    insert_result = MagicMock()
    insert_result.inserted_id = mock_id
    mock_collection.insert_one.return_value = insert_result
    
    # Mock find
    mock_cursor = MagicMock()
    mock_cursor.__iter__.return_value = iter([{"_id": mock_id, "name": "Test"}])
    mock_collection.find.return_value = mock_cursor
    
    # Mock update_one and update_many
    update_result = MagicMock()
    update_result.matched_count = 1
    update_result.modified_count = 1
    update_result.upserted_id = None
    mock_collection.update_one.return_value = update_result
    mock_collection.update_many.return_value = update_result
    
    # Mock delete_one and delete_many
    delete_result = MagicMock()
    delete_result.deleted_count = 1
    mock_collection.delete_one.return_value = delete_result
    mock_collection.delete_many.return_value = delete_result
    
    return {
        "client": mock_client,
        "db": mock_db,
        "collection": mock_collection,
    }


@patch("mongo_mcp.tools.database_tools.get_client")
def test_list_databases(mock_get_client, mock_mongodb):
    """Test listing databases."""
    mock_get_client.return_value = mock_mongodb["client"]
    
    result = list_databases()
    
    assert isinstance(result, list)
    assert "test_db" in result
    assert "admin" not in result  # Should be filtered out
    assert mock_mongodb["client"].list_databases.called


@patch("mongo_mcp.tools.database_tools.get_database")
def test_list_collections(mock_get_database, mock_mongodb):
    """Test listing collections."""
    mock_get_database.return_value = mock_mongodb["db"]
    
    result = list_collections("test_db")
    
    assert isinstance(result, list)
    assert "test_collection" in result
    assert mock_mongodb["db"].list_collection_names.called


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_insert_document(mock_get_collection, mock_mongodb):
    """Test inserting a document."""
    mock_get_collection.return_value = mock_mongodb["collection"]
    
    document = {"name": "Test Document"}
    result = insert_document("test_db", "test_collection", document)
    
    assert isinstance(result, dict)
    assert "inserted_id" in result
    assert result["success"] is True
    mock_mongodb["collection"].insert_one.assert_called_with(document)


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_find_documents(mock_get_collection, mock_mongodb):
    """Test finding documents."""
    mock_get_collection.return_value = mock_mongodb["collection"]
    
    query = {"name": "Test"}
    result = find_documents("test_db", "test_collection", query)
    
    assert isinstance(result, list)
    assert len(result) > 0
    assert "name" in result[0]
    assert "_id" in result[0]
    assert isinstance(result[0]["_id"], str)  # Should be converted to string
    mock_mongodb["collection"].find.assert_called_with(query, projection=None)


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_update_document(mock_get_collection, mock_mongodb):
    """Test updating a document."""
    mock_get_collection.return_value = mock_mongodb["collection"]
    
    query = {"name": "Test"}
    update_data = {"$set": {"name": "Updated Test"}}
    result = update_document("test_db", "test_collection", query, update_data)
    
    assert isinstance(result, dict)
    assert result["matched_count"] == 1
    assert result["modified_count"] == 1
    mock_mongodb["collection"].update_one.assert_called_with(
        query, update_data, upsert=False
    )


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_delete_document(mock_get_collection, mock_mongodb):
    """Test deleting a document."""
    mock_get_collection.return_value = mock_mongodb["collection"]
    
    query = {"name": "Test"}
    result = delete_document("test_db", "test_collection", query)
    
    assert isinstance(result, dict)
    assert result["deleted_count"] == 1
    mock_mongodb["collection"].delete_one.assert_called_with(query) 