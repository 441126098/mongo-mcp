# Mongo-MCP

[![smithery badge](https://smithery.ai/badge/@441126098/mongo-mcp)](https://smithery.ai/server/@441126098/mongo-mcp)
English | [简体中文](README_CN.md)

A Machine Chat Protocol (MCP) service for MongoDB operations. This service provides a set of tools that allow Large Language Models (LLMs) to interact with MongoDB databases through basic CRUD operations and administrative tasks.

## Features

- MongoDB instance connection management
- List databases and collections
- Document CRUD operations
  - Insert documents
  - Query documents (supports complex queries and projections)
  - Update documents
  - Delete documents
- Full support for MongoDB query syntax and projections
- Comprehensive error handling and logging
- Stdin/stdout (stdio) based MCP transport implementation

## Usage

### Run directly with uvx

```bash
uvx run mongo-mcp
```
The server uses the stdio transport method, making it suitable for integration with MCP clients that support this transport method.

### Cursor Example Configuration

If you use [Cursor](https://www.cursor.so/) as your development environment, you can add the following configuration to your `.cursor/mcp.json` file for local debugging:

```json
"mongodb": {
  "command": "python -m mongo_mcp.server",
  "env": {
    "MONGODB_URI": "mongodb://localhost:27017",
    "MONGODB_DEFAULT_DB": "DEFAULT_DB_NAME",
    "LOG_LEVEL": "INFO"
  }
}
```

### Environment Variables

- `MONGODB_URI`: MongoDB connection string (default: "mongodb://localhost:27017")
- `MONGODB_DEFAULT_DB`: Default database name (optional)
- `LOG_LEVEL`: Logging level (default: "INFO")
  - Available values: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Supported Operations

- List all databases
- List all collections in a specified database
- Insert documents
- Query documents (supports query conditions and field projections)
- Update documents (supports single and bulk updates)
- Delete documents (supports single and bulk deletions)

## Development Guide

1. Clone the repository
```bash
git clone https://github.com/yourusername/mongo-mcp.git
cd mongo-mcp
```

2. Install development dependencies
```bash
# Using pip
pip install -e "[dev]"

# Or using uv (recommended for faster installation)
uv pip install -e "[dev]"
```

3. Run tests
```bash
pytest
```

4. Code Structure
- `server.py`: MCP server implementation
- `db.py`: Core MongoDB operations implementation
- `config.py`: Configuration management
- `tools/`: MCP tools implementation
- `tests/`: Test cases

## Logging

Log files are stored in the `logs` directory by default. The log level can be controlled through the `LOG_LEVEL` environment variable.

## License

MIT

## Contributing

Contributions via Issues and Pull Requests are welcome. Before submitting a PR, please ensure:

1. All tests pass
2. Appropriate test cases are added
3. Documentation is updated 