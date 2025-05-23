"""MCP server module for MongoDB operations."""

import signal
import sys
import logging
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP

from mongo_mcp.config import logger
from mongo_mcp.db import close_connection, get_client
from mongo_mcp.tools import (
    list_databases,
    list_collections,
    insert_document,
    find_documents,
    update_document,
    delete_document,
)
from mongo_mcp.utils.json_encoder import mongodb_json_serializer


# Set up MCP server
# 尝试设置配置以禁用内部日志记录
# 注意：根据FastMCP的版本和功能，此处的参数可能不支持，可能需要查看FastMCP文档
app = FastMCP(name="MongoDB MCP")

# Register MongoDB tools
for tool in [
    list_databases,
    list_collections,
    insert_document,
    find_documents,
    update_document,
    delete_document,
]:
    # 添加工具，不使用serializer参数
    app.add_tool(tool)


# Set up signal handlers for graceful shutdown
def signal_handler(sig, frame):
    """Handle termination signals."""
    logger.info("Shutting down MCP server")
    close_connection()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def start_server() -> None:
    """Start the MCP server with stdio transport."""
    # 移除下面这行日志，因为FastMCP会自动记录类似的信息
    # logger.info("Starting MCP server with stdio transport")
    try:
        # 使用FastMCP的run方法，指定stdio传输方式
        app.run(transport="stdio")
    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}")
        close_connection()
        sys.exit(1)


if __name__ == "__main__":
    start_server() 