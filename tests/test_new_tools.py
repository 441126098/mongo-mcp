"""Tests for new MongoDB tools."""

import pytest
from unittest.mock import MagicMock, patch

# Test imports for all new tool modules
def test_database_tools_import():
    """Test that all database tools can be imported."""
    from mongo_mcp.tools.database_tools import (
        list_databases,
        list_collections,
        create_database,
        drop_database,
        get_database_stats,
        create_collection,
        drop_collection,
        rename_collection,
        get_collection_stats,
    )
    assert callable(list_databases)
    assert callable(list_collections)
    assert callable(create_database)
    assert callable(drop_database)
    assert callable(get_database_stats)
    assert callable(create_collection)
    assert callable(drop_collection)
    assert callable(rename_collection)
    assert callable(get_collection_stats)


def test_document_tools_import():
    """Test that all document tools can be imported."""
    from mongo_mcp.tools.document_tools import (
        insert_document,
        insert_many_documents,
        find_documents,
        find_one_document,
        count_documents,
        update_document,
        replace_document,
        delete_document,
    )
    assert callable(insert_document)
    assert callable(insert_many_documents)
    assert callable(find_documents)
    assert callable(find_one_document)
    assert callable(count_documents)
    assert callable(update_document)
    assert callable(replace_document)
    assert callable(delete_document)


def test_index_tools_import():
    """Test that all index tools can be imported."""
    from mongo_mcp.tools.index_tools import (
        list_indexes,
        create_index,
        create_text_index,
        create_compound_index,
        drop_index,
        reindex_collection,
    )
    assert callable(list_indexes)
    assert callable(create_index)
    assert callable(create_text_index)
    assert callable(create_compound_index)
    assert callable(drop_index)
    assert callable(reindex_collection)


def test_aggregation_tools_import():
    """Test that all aggregation tools can be imported."""
    from mongo_mcp.tools.aggregation_tools import (
        aggregate_documents,
        distinct_values,
    )
    assert callable(aggregate_documents)
    assert callable(distinct_values)


def test_admin_tools_import():
    """Test that all admin tools can be imported."""
    from mongo_mcp.tools.admin_tools import (
        get_server_status,
        get_replica_set_status,
        ping_database,
        test_mongodb_connection,
        get_connection_details,
    )
    assert callable(get_server_status)
    assert callable(get_replica_set_status)
    assert callable(ping_database)
    assert callable(test_mongodb_connection)
    assert callable(get_connection_details)


def test_all_tools_import():
    """Test that all tools can be imported from the main tools module."""
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
    
    # Verify all tools are callable
    tools = [
        list_databases, list_collections, create_database, drop_database,
        get_database_stats, create_collection, drop_collection, rename_collection,
        get_collection_stats, insert_document, insert_many_documents, find_documents,
        find_one_document, count_documents, update_document, replace_document,
        delete_document, list_indexes, create_index, create_text_index,
        create_compound_index, drop_index, reindex_collection, aggregate_documents,
        distinct_values, get_server_status, get_replica_set_status, ping_database,
        test_mongodb_connection, get_connection_details,
    ]
    
    for tool in tools:
        assert callable(tool)
    
    # Should match the number of tools registered in server
    assert len(tools) == 30


def test_server_tools_registration():
    """Test that the server has registered all tools."""
    from mongo_mcp.server import mongo_tools
    
    # Verify we have the expected number of tools
    assert len(mongo_tools) == 30
    
    # Verify all tools are callable
    for tool in mongo_tools:
        assert callable(tool)


def test_config_enhancements():
    """Test that configuration enhancements are available."""
    from mongo_mcp.config import (
        get_connection_options,
        log_configuration,
        MONGODB_MAX_DOCUMENTS_LIMIT,
        ENABLE_DANGEROUS_OPERATIONS,
        ENABLE_ADMIN_OPERATIONS,
        ENABLE_INDEX_OPERATIONS,
    )
    
    assert callable(get_connection_options)
    assert callable(log_configuration)
    assert isinstance(MONGODB_MAX_DOCUMENTS_LIMIT, int)
    assert isinstance(ENABLE_DANGEROUS_OPERATIONS, bool)
    assert isinstance(ENABLE_ADMIN_OPERATIONS, bool)
    assert isinstance(ENABLE_INDEX_OPERATIONS, bool)


def test_db_enhancements():
    """Test that database module enhancements are available."""
    from mongo_mcp.db import (
        test_connection,
        get_connection_info,
    )
    
    assert callable(test_connection)
    assert callable(get_connection_info)


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_insert_many_documents_validation(mock_get_collection):
    """Test validation for insert_many_documents function."""
    from mongo_mcp.tools.document_tools import insert_many_documents
    
    # Test with empty parameters
    with pytest.raises(ValueError, match="Database name and collection name must be provided"):
        insert_many_documents("", "test_collection", [{"test": "doc"}])
    
    # Test with invalid documents
    with pytest.raises(ValueError, match="Documents must be a non-empty list"):
        insert_many_documents("test_db", "test_collection", "not_a_list")


@patch("mongo_mcp.tools.document_tools.get_collection")
def test_count_documents_validation(mock_get_collection):
    """Test validation for count_documents function."""
    from mongo_mcp.tools.document_tools import count_documents
    
    # Test with empty parameters
    with pytest.raises(ValueError, match="Database name and collection name must be provided"):
        count_documents("", "test_collection", {})
    
    # Test with invalid query
    with pytest.raises(ValueError, match="Query must be a dictionary"):
        count_documents("test_db", "test_collection", "not_a_dict")


@patch("mongo_mcp.tools.index_tools.get_collection")
def test_create_index_validation(mock_get_collection):
    """Test validation for create_index function."""
    from mongo_mcp.tools.index_tools import create_index
    
    # Test with empty parameters
    with pytest.raises(ValueError, match="Database name and collection name must be provided"):
        create_index("", "test_collection", {"field": 1})
    
    # Test with invalid keys
    with pytest.raises(ValueError, match="Keys must be a non-empty dictionary"):
        create_index("test_db", "test_collection", None) 