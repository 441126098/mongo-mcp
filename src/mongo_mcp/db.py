"""Database connection module for mongo-mcp."""

from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import PyMongoError

from mongo_mcp.config import MONGODB_URI, MONGODB_DEFAULT_DB, logger

# Global client instance
_client: Optional[MongoClient] = None


def get_client() -> MongoClient:
    """Get or initialize MongoDB client.
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _client
    if _client is None:
        try:
            logger.info(f"Connecting to MongoDB at {MONGODB_URI}")
            _client = MongoClient(MONGODB_URI)
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
            logger.info(f"连接数: {server_status.get('connections', {}).get('current', 'Unknown')}")
            
            # 列出所有可用的数据库
            database_names = _client.list_database_names()
            logger.info(f"可用数据库列表: {', '.join(database_names)}")
            logger.info("=== 连接信息结束 ===")
            
            logger.info("Successfully connected to MongoDB")
        except PyMongoError as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    return _client


def get_database(database_name: Optional[str] = None) -> Database:
    """Get MongoDB database.
    
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
    
    return client[db_name]


def get_collection(database_name: str, collection_name: str) -> Collection:
    """Get MongoDB collection.
    
    Args:
        database_name: Name of the database
        collection_name: Name of the collection
        
    Returns:
        Collection: MongoDB collection instance
    """
    db = get_database(database_name)
    return db[collection_name]


def close_connection() -> None:
    """Close the MongoDB connection."""
    global _client
    if _client is not None:
        logger.info("Closing MongoDB connection")
        _client.close()
        _client = None 