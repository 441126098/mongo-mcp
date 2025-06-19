"""Administrative and monitoring tools for MongoDB."""

from typing import Dict, Any, Optional
from pymongo.errors import PyMongoError, OperationFailure

from mongo_mcp.db import get_client, get_database, test_connection, get_connection_info
from mongo_mcp.config import logger


def get_server_status() -> Dict[str, Any]:
    """Get MongoDB server status information.
    
    Returns:
        Dict[str, Any]: Server status information
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        client = get_client()
        status = client.admin.command("serverStatus")
        
        # Extract relevant information and clean for JSON serialization
        clean_status = {
            "host": status.get("host"),
            "version": status.get("version"),
            "process": status.get("process"),
            "pid": status.get("pid"),
            "uptime": status.get("uptime"),
            "uptime_millis": status.get("uptimeMillis"),
            "local_time": str(status.get("localTime")),
            "connections": {
                "current": status.get("connections", {}).get("current"),
                "available": status.get("connections", {}).get("available"),
                "total_created": status.get("connections", {}).get("totalCreated"),
            },
            "network": {
                "bytes_in": status.get("network", {}).get("bytesIn"),
                "bytes_out": status.get("network", {}).get("bytesOut"),
                "num_requests": status.get("network", {}).get("numRequests"),
            },
            "opcounters": status.get("opcounters", {}),
            "mem": {
                "bits": status.get("mem", {}).get("bits"),
                "resident": status.get("mem", {}).get("resident"),
                "virtual": status.get("mem", {}).get("virtual"),
                "mapped": status.get("mem", {}).get("mapped"),
            },
            "extra_info": {
                "note": status.get("extra_info", {}).get("note"),
                "heap_usage_bytes": status.get("extra_info", {}).get("heap_usage_bytes"),
                "page_faults": status.get("extra_info", {}).get("page_faults"),
            }
        }
        
        logger.info("Retrieved MongoDB server status")
        return clean_status
    except PyMongoError as e:
        logger.error(f"Failed to get server status: {e}")
        raise


def get_replica_set_status() -> Optional[Dict[str, Any]]:
    """Get replica set status information if applicable.
    
    Returns:
        Optional[Dict[str, Any]]: Replica set status or None if not in replica set
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        client = get_client()
        
        # Check if this is a replica set
        try:
            status = client.admin.command("replSetGetStatus")
        except OperationFailure as e:
            if "not running with --replSet" in str(e) or "not a member of a replica set" in str(e):
                logger.info("MongoDB instance is not part of a replica set")
                return None
            else:
                raise
        
        # Clean replica set status for JSON serialization
        clean_status = {
            "set": status.get("set"),
            "date": str(status.get("date")),
            "my_state": status.get("myState"),
            "term": status.get("term"),
            "sync_source_host": status.get("syncSourceHost"),
            "sync_source_id": status.get("syncSourceId"),
            "heartbeat_interval_millis": status.get("heartbeatIntervalMillis"),
            "majority_vote_count": status.get("majorityVoteCount"),
            "write_majority_count": status.get("writeMajorityCount"),
            "voting_members_count": status.get("votingMembersCount"),
            "write_concern_majority_journal_default": status.get("writeConcernMajorityJournalDefault"),
            "members": []
        }
        
        # Process members information
        for member in status.get("members", []):
            clean_member = {
                "_id": member.get("_id"),
                "name": member.get("name"),
                "health": member.get("health"),
                "state": member.get("state"),
                "state_str": member.get("stateStr"),
                "uptime": member.get("uptime"),
                "optime": {
                    "ts": str(member.get("optime", {}).get("ts")),
                    "t": member.get("optime", {}).get("t")
                },
                "optimeDurable": {
                    "ts": str(member.get("optimeDurable", {}).get("ts")),
                    "t": member.get("optimeDurable", {}).get("t")
                },
                "last_heartbeat": str(member.get("lastHeartbeat")),
                "last_heartbeat_recv": str(member.get("lastHeartbeatRecv")),
                "ping_ms": member.get("pingMs"),
                "sync_source_host": member.get("syncSourceHost"),
                "sync_source_id": member.get("syncSourceId"),
                "info_message": member.get("infoMessage"),
                "election_time": str(member.get("electionTime")),
                "election_date": str(member.get("electionDate")),
                "config_version": member.get("configVersion"),
                "config_term": member.get("configTerm")
            }
            # Remove None values
            clean_member = {k: v for k, v in clean_member.items() if v is not None and v != "None"}
            clean_status["members"].append(clean_member)
        
        logger.info(f"Retrieved replica set status for set '{clean_status['set']}'")
        return clean_status
    except PyMongoError as e:
        logger.error(f"Failed to get replica set status: {e}")
        raise


def ping_database(database_name: Optional[str] = None) -> Dict[str, Any]:
    """Test database connection and get basic information.
    
    Args:
        database_name: Optional database name to ping specific database
    
    Returns:
        Dict[str, Any]: Connection status and basic information
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        if database_name:
            # Ping specific database
            db = get_database(database_name)
            ping_result = db.command("ping")
            
            # Get database stats
            try:
                stats = db.command("dbStats")
                db_info = {
                    "database": stats.get("db"),
                    "collections": stats.get("collections"),
                    "objects": stats.get("objects"),
                    "data_size": stats.get("dataSize"),
                    "storage_size": stats.get("storageSize"),
                    "indexes": stats.get("indexes"),
                    "index_size": stats.get("indexSize"),
                }
            except PyMongoError:
                db_info = {"error": "Could not retrieve database stats"}
        else:
            # Ping admin database
            client = get_client()
            ping_result = client.admin.command("ping")
            db_info = {}
        
        # Get basic server information
        try:
            is_master = client.admin.command("hello")  # Updated from deprecated 'isMaster'
            server_info = {
                "is_writable_primary": is_master.get("isWritablePrimary", is_master.get("isMaster")),
                "max_bson_object_size": is_master.get("maxBsonObjectSize"),
                "max_message_size_bytes": is_master.get("maxMessageSizeBytes"),
                "max_write_batch_size": is_master.get("maxWriteBatchSize"),
                "local_time": str(is_master.get("localTime")),
                "log_component_verbosity": is_master.get("logComponentVerbosity"),
                "min_wire_version": is_master.get("minWireVersion"),
                "max_wire_version": is_master.get("maxWireVersion"),
                "readonly": is_master.get("readOnly"),
            }
        except PyMongoError:
            server_info = {"error": "Could not retrieve server info"}
        
        result = {
            "ping_ok": ping_result.get("ok") == 1,
            "timestamp": str(ping_result.get("operationTime")),
            "server_info": server_info,
            "connection_status": "healthy"
        }
        
        if database_name:
            result["database_info"] = db_info
            logger.info(f"Successfully pinged database '{database_name}'")
        else:
            logger.info("Successfully pinged MongoDB server")
        
        return result
    except PyMongoError as e:
        logger.error(f"Failed to ping database: {e}")
        return {
            "ping_ok": False,
            "connection_status": "failed",
            "error": str(e),
            "database_info": db_info if database_name else None
        }


def test_mongodb_connection() -> Dict[str, Any]:
    """Comprehensive MongoDB connection test.
    
    Returns:
        Dict[str, Any]: Detailed connection test results
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        # Use the enhanced connection test from db module
        result = test_connection()
        logger.info("Comprehensive connection test completed")
        return result
    except PyMongoError as e:
        logger.error(f"Connection test failed: {e}")
        raise


def get_connection_details() -> Dict[str, Any]:
    """Get detailed MongoDB connection information.
    
    Returns:
        Dict[str, Any]: Connection details and configuration
    
    Raises:
        PyMongoError: If the operation fails
    """
    try:
        # Use the connection info from db module
        result = get_connection_info()
        logger.info("Retrieved connection details")
        return result
    except Exception as e:
        logger.error(f"Failed to get connection details: {e}")
        raise 