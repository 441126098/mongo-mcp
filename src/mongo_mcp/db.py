"""Database connection module for mongo-mcp."""

from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from mongo_mcp.config import (
    MONGODB_URI, 
    MONGODB_DEFAULT_DB, 
    logger,
    get_connection_options,
    log_configuration
)

# Global client instance
_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Get or initialize MongoDB client with enhanced configuration.
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _client
    if _client is None:
        try:
            # Log configuration on first connection
            log_configuration()
            
            logger.info(f"Connecting to MongoDB at {MONGODB_URI}")
            
            # Get connection options from configuration
            connection_options = get_connection_options()
            
            # Create client with all configuration options
            _client = MongoClient(MONGODB_URI, **connection_options)
            
            # Ping the server to validate connection
            _client.admin.command('ping')
            
            # 获取并打印更详细的连接信息
            server_info = _client.server_info()
            server_status = _client.admin.command('serverStatus')
            
            # 打印详细的连接信息
            logger.info("=== MongoDB 连接信息 ===")
            logger.info(f"MongoDB 版本: {server_info.get('version', 'Unknown')}")
            logger.info(f"MongoDB 服务器: {MONGODB_URI}")
            logger.info(f"默认数据库: {MONGODB_DEFAULT_DB or '未设置'}")
            logger.info(f"当前连接数: {server_status.get('connections', {}).get('current', 'Unknown')}")
            logger.info(f"可用连接数: {server_status.get('connections', {}).get('available', 'Unknown')}")
            logger.info(f"已创建连接数: {server_status.get('connections', {}).get('totalCreated', 'Unknown')}")
            
            # 列出所有可用的数据库
            try:
                database_names = _client.list_database_names()
                user_databases = [db for db in database_names if db not in ['admin', 'local', 'config']]
                logger.info(f"用户数据库列表: {', '.join(user_databases) if user_databases else '无'}")
                logger.info(f"系统数据库列表: admin, local, config")
            except Exception as e:
                logger.warning(f"无法列出数据库: {e}")
            
            # Check if this is a replica set
            try:
                is_master_result = _client.admin.command("hello")
                if is_master_result.get("setName"):
                    logger.info(f"副本集名称: {is_master_result.get('setName')}")
                    logger.info(f"主节点: {is_master_result.get('isWritablePrimary', is_master_result.get('isMaster'))}")
                else:
                    logger.info("连接类型: 单实例 MongoDB")
            except Exception as e:
                logger.warning(f"无法检查副本集状态: {e}")
            
            logger.info("=== 连接信息结束 ===")
            
            logger.info("Successfully connected to MongoDB with enhanced configuration")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    return _client


def get_database(database_name: Optional[str] = None) -> Database:
    """Get MongoDB database with read/write preferences.
    
    Args:
        database_name: Name of the database, or None to use default
        
    Returns:
        Database: MongoDB database instance
    
    Raises:
        ValueError: If no database name is provided and no default is set
    """
    client = get_client()
    db_name = database_name or MONGODB_DEFAULT_DB
    
    if not db_name:
        raise ValueError("No database name provided and no default database set")
    
    # Get database with configured read/write preferences
    database = client[db_name]
    
    # Apply read/write preferences if configured
    from mongo_mcp.config import (
        MONGODB_READ_PREFERENCE,
        MONGODB_WRITE_CONCERN_W,
        MONGODB_WRITE_CONCERN_J,
        MONGODB_READ_CONCERN_LEVEL
    )
    
    # Set read preference
    if MONGODB_READ_PREFERENCE != "primary":
        from pymongo.read_preferences import ReadPreference
        read_pref_map = {
            "secondary": ReadPreference.SECONDARY,
            "secondaryPreferred": ReadPreference.SECONDARY_PREFERRED,
            "primaryPreferred": ReadPreference.PRIMARY_PREFERRED,
            "nearest": ReadPreference.NEAREST
        }
        if MONGODB_READ_PREFERENCE in read_pref_map:
            database = database.with_options(read_preference=read_pref_map[MONGODB_READ_PREFERENCE])
    
    # Set write concern
    if MONGODB_WRITE_CONCERN_W != "1" or MONGODB_WRITE_CONCERN_J:
        from pymongo.write_concern import WriteConcern
        w_value = int(MONGODB_WRITE_CONCERN_W) if MONGODB_WRITE_CONCERN_W.isdigit() else MONGODB_WRITE_CONCERN_W
        write_concern = WriteConcern(w=w_value, j=MONGODB_WRITE_CONCERN_J)
        database = database.with_options(write_concern=write_concern)
    
    # Set read concern
    if MONGODB_READ_CONCERN_LEVEL != "local":
        from pymongo.read_concern import ReadConcern
        read_concern = ReadConcern(level=MONGODB_READ_CONCERN_LEVEL)
        database = database.with_options(read_concern=read_concern)
    
    return database


def get_collection(database_name: str, collection_name: str) -> Collection:
    """Get MongoDB collection with configured preferences.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = get_database(database_name)
    return db[collection_name]


def test_connection() -> Dict[str, Any]:
    """Test MongoDB connection and return connection details.
    
    Returns:
        Dict[str, Any]: Connection test results
    """
    try:
        client = get_client()
        
        # Test basic connectivity
        ping_result = client.admin.command("ping")
        
        # Get server information
        server_info = client.server_info()
        
        # Get server status
        server_status = client.admin.command("serverStatus")
        
        # Get database list
        database_names = client.list_database_names()
        
        result = {
            "connection_status": "healthy",
            "ping_ok": ping_result.get("ok") == 1,
            "server_version": server_info.get("version"),
            "server_process": server_status.get("process"),
            "uptime_seconds": server_status.get("uptime"),
            "connections": {
                "current": server_status.get("connections", {}).get("current"),
                "available": server_status.get("connections", {}).get("available"),
                "total_created": server_status.get("connections", {}).get("totalCreated"),
            },
            "databases": {
                "total_count": len(database_names),
                "user_databases": [db for db in database_names if db not in ['admin', 'local', 'config']],
                "system_databases": [db for db in database_names if db in ['admin', 'local', 'config']]
            }
        }
        
        logger.info("Connection test completed successfully")
        return result
        
    except PyMongoError as e:
        logger.error(f"Connection test failed: {e}")
        return {
            "connection_status": "failed",
            "error": str(e),
            "ping_ok": False
        }


def close_connection() -> None:
    """Close the MongoDB connection and cleanup resources."""
    global _client
    if _client is not None:
        logger.info("Closing MongoDB connection")
        try:
            _client.close()
            logger.info("MongoDB connection closed successfully")
        except Exception as e:
            logger.warning(f"Error closing MongoDB connection: {e}")
        finally:
            _client = None


def get_connection_info() -> Dict[str, Any]:
    """Get current connection information.
    
    Returns:
        Dict[str, Any]: Connection information
    """
    global _client
    if _client is None:
        return {"status": "not_connected"}
    
    try:
        # Get connection options that were used
        from mongo_mcp.config import get_connection_options
        options = get_connection_options()
        
        return {
            "status": "connected",
            "uri": MONGODB_URI,
            "default_database": MONGODB_DEFAULT_DB,
            "connection_options": options,
            "client_info": {
                "nodes": _client.nodes,
                "primary": _client.primary,
                "secondaries": list(_client.secondaries),
                "arbiters": list(_client.arbiters),
                "is_mongos": _client.is_mongos,
                "is_primary": _client.is_primary,
            }
        }
    except Exception as e:
        logger.error(f"Error getting connection info: {e}")
        return {
            "status": "error",
            "error": str(e)
        } 