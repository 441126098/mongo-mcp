"""MCP tools for MongoDB operations."""

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
from mongo_mcp.tools.index_tools import (
    list_indexes,
    create_index,
    create_text_index,
    create_compound_index,
    drop_index,
    reindex_collection,
)
from mongo_mcp.tools.aggregation_tools import (
    aggregate_documents,
    distinct_values,
)
from mongo_mcp.tools.admin_tools import (
    get_server_status,
    get_replica_set_status,
    ping_database,
    test_mongodb_connection,
    get_connection_details,
)

__all__ = [
    # Database management tools
    "list_databases",
    "list_collections",
    "create_database",
    "drop_database",
    "get_database_stats",
    "create_collection",
    "drop_collection",
    "rename_collection",
    "get_collection_stats",
    
    # Document CRUD operations
    "insert_document",
    "insert_many_documents",
    "find_documents",
    "find_one_document",
    "count_documents",
    "update_document",
    "replace_document",
    "delete_document",
    
    # Index management tools
    "list_indexes",
    "create_index",
    "create_text_index",
    "create_compound_index",
    "drop_index",
    "reindex_collection",
    
    # Aggregation operations
    "aggregate_documents",
    "distinct_values",
    
    # Administrative and monitoring tools
    "get_server_status",
    "get_replica_set_status",
    "ping_database",
    "test_mongodb_connection",
    "get_connection_details",
] 