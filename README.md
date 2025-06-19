# Mongo-MCP

[![smithery badge](https://smithery.ai/badge/@441126098/mongo-mcp)](https://smithery.ai/server/@441126098/mongo-mcp)
English | [简体中文](README_CN.md)

A Machine Chat Protocol (MCP) service for MongoDB operations. This service provides a comprehensive set of tools that allow Large Language Models (LLMs) to interact with MongoDB databases through complete CRUD operations, administrative tasks, and advanced features.

## Requirements

- Python 3.10 or above
- A running MongoDB database service
- It is recommended to use [uv](https://github.com/astral-sh/uv) to run the program

## 🚀 Features

### 📊 Database Management Tools
- `list_databases` - List all databases
- `create_database` - Create new database
- `drop_database` - Delete database
- `get_database_stats` - Get database statistics

### 📦 Collection Management Tools
- `list_collections` - List all collections in a database
- `create_collection` - Create new collection (with optional settings)
- `drop_collection` - Delete collection
- `rename_collection` - Rename collection
- `get_collection_stats` - Get collection statistics

### 📄 Document CRUD Operations
- `insert_document` - Insert single document
- `insert_many_documents` - Batch insert multiple documents
- `find_documents` - Query documents (supports sorting, projection, limit)
- `find_one_document` - Query single document
- `count_documents` - Count documents matching query
- `update_document` - Update documents (single or batch)
- `replace_document` - Replace document
- `delete_document` - Delete documents (single or batch)

### 🔍 Index Management Tools
- `list_indexes` - List all indexes for a collection
- `create_index` - Create regular index
- `create_text_index` - Create text search index
- `create_compound_index` - Create compound index
- `drop_index` - Delete index
- `reindex_collection` - Rebuild all indexes for a collection

### 📈 Aggregation Operations
- `aggregate_documents` - Execute aggregation pipeline operations
- `distinct_values` - Get distinct values for a field

### 🔧 Monitoring and Administrative Tools
- `get_server_status` - Get MongoDB server status
- `get_replica_set_status` - Get replica set status
- `ping_database` - Test database connection
- `test_mongodb_connection` - Comprehensive connection test
- `get_connection_details` - Get detailed connection information

## 🛠️ Technology Stack

- **Python**: Primary programming language
- **FastMCP**: MCP Python SDK for automatic tool definition generation
- **PyMongo**: Official MongoDB Python driver
- **uv**: Modern Python package management tool

## Usage

### Run directly with uvx

```bash
uvx run mongo-mcp
```
The server uses the stdio transport method, making it suitable for integration with MCP clients that support this transport method.

### Cursor Example Configuration

If you use [Cursor](https://www.cursor.so/) as your development environment, you can add the following configuration to your `.cursor/mcp.json` file for local debugging:

```json
{
    "mcpServers": {
        "mongo-mcp": {
            "command": "uvx",
            "args": [
                "mongo-mcp"
            ],
            "env": {
                "MONGODB_URI": "mongodb://localhost:27017",
                "MONGODB_DEFAULT_DB": "your_database_name",
                "LOG_LEVEL": "INFO"
            }
        }
    }
}
```

### Environment Variables

#### Basic Configuration
- `MONGODB_URI`: MongoDB connection string (default: "mongodb://localhost:27017")
- `MONGODB_DEFAULT_DB`: Default database name (optional)

#### Connection Pool Configuration
- `MONGODB_MIN_POOL_SIZE`: Minimum connection pool size (default: 0)
- `MONGODB_MAX_POOL_SIZE`: Maximum connection pool size (default: 100)
- `MONGODB_MAX_IDLE_TIME_MS`: Maximum idle time in milliseconds (default: 30000)

#### Timeout Configuration
- `MONGODB_SERVER_SELECTION_TIMEOUT_MS`: Server selection timeout (default: 30000)
- `MONGODB_SOCKET_TIMEOUT_MS`: Socket timeout (default: 0 - no timeout)
- `MONGODB_CONNECT_TIMEOUT_MS`: Connection timeout (default: 20000)

#### Security Configuration
- `MONGODB_TLS_ENABLED`: Enable TLS connection (default: false)
- `MONGODB_AUTH_SOURCE`: Authentication source (default: admin)
- `MONGODB_AUTH_MECHANISM`: Authentication mechanism (SCRAM-SHA-1, SCRAM-SHA-256, etc.)

#### Performance Settings
- `MONGODB_READ_PREFERENCE`: Read preference (default: primary)
- `MONGODB_WRITE_CONCERN_W`: Write concern (default: 1)
- `MONGODB_READ_CONCERN_LEVEL`: Read concern level (default: local)

#### Logging Configuration
- `LOG_LEVEL`: Logging level (default: "INFO")
  - Available values: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_MAX_FILE_SIZE`: Maximum log file size in bytes (default: 10MB)
- `LOG_BACKUP_COUNT`: Number of backup log files (default: 5)

#### Feature Flags
- `ENABLE_DANGEROUS_OPERATIONS`: Enable potentially dangerous operations (default: false)
- `ENABLE_ADMIN_OPERATIONS`: Enable administrative operations (default: true)
- `ENABLE_INDEX_OPERATIONS`: Enable index operations (default: true)

## Development Guide

1. Clone the repository
```bash
git clone https://github.com/441126098/mongo-mcp.git
cd mongo-mcp
```

2. Install development dependencies
```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e ".[dev]"
```

3. Run tests
```bash
uv run pytest tests/ -v
```

4. Code Structure
- `src/mongo_mcp/server.py`: MCP server implementation
- `src/mongo_mcp/db.py`: Core MongoDB operations implementation
- `src/mongo_mcp/config.py`: Configuration management
- `src/mongo_mcp/tools/`: MCP tools implementation
  - `database_tools.py`: Database and collection management
  - `document_tools.py`: Document CRUD operations
  - `index_tools.py`: Index management
  - `aggregation_tools.py`: Aggregation operations
  - `admin_tools.py`: Administrative and monitoring tools
- `src/mongo_mcp/utils/`: Utility modules
- `tests/`: Test cases

## Testing

The project includes comprehensive test coverage:
- Unit tests for all tool modules
- Integration tests with MongoDB
- Mock tests for isolated component testing

Run the test suite:
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_tools.py
```

## Logging

Log files are stored in the `logs` directory by default. The logging system supports:
- Configurable log levels
- File rotation based on size
- UTF-8 encoding support
- Structured logging with function names and line numbers

## License

MIT

## Contributing

Contributions via Issues and Pull Requests are welcome. Before submitting a PR, please ensure:

1. All tests pass (`uv run pytest`)
2. Appropriate test cases are added
3. Documentation is updated
4. Code follows the existing style patterns 