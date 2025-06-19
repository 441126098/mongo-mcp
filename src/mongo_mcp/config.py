"""Configuration module for mongo-mcp."""

import os
import logging
from typing import Optional
from pathlib import Path

# 获取项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# MongoDB configuration
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DEFAULT_DB = os.environ.get("MONGODB_DEFAULT_DB")

# Connection pool configuration
MONGODB_MIN_POOL_SIZE = int(os.environ.get("MONGODB_MIN_POOL_SIZE", "0"))
MONGODB_MAX_POOL_SIZE = int(os.environ.get("MONGODB_MAX_POOL_SIZE", "100"))
MONGODB_MAX_IDLE_TIME_MS = int(os.environ.get("MONGODB_MAX_IDLE_TIME_MS", "30000"))

# Operation timeout configuration
MONGODB_SERVER_SELECTION_TIMEOUT_MS = int(os.environ.get("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "30000"))
MONGODB_SOCKET_TIMEOUT_MS = int(os.environ.get("MONGODB_SOCKET_TIMEOUT_MS", "0"))  # 0 means no timeout
MONGODB_CONNECT_TIMEOUT_MS = int(os.environ.get("MONGODB_CONNECT_TIMEOUT_MS", "20000"))

# Operation limits
MONGODB_MAX_DOCUMENTS_LIMIT = int(os.environ.get("MONGODB_MAX_DOCUMENTS_LIMIT", "1000"))
MONGODB_DEFAULT_BATCH_SIZE = int(os.environ.get("MONGODB_DEFAULT_BATCH_SIZE", "100"))

# Security configuration
MONGODB_TLS_ENABLED = os.environ.get("MONGODB_TLS_ENABLED", "false").lower() == "true"
MONGODB_TLS_CA_FILE = os.environ.get("MONGODB_TLS_CA_FILE")
MONGODB_TLS_CERT_FILE = os.environ.get("MONGODB_TLS_CERT_FILE")
MONGODB_TLS_KEY_FILE = os.environ.get("MONGODB_TLS_KEY_FILE")

# Authentication configuration
MONGODB_AUTH_SOURCE = os.environ.get("MONGODB_AUTH_SOURCE", "admin")
MONGODB_AUTH_MECHANISM = os.environ.get("MONGODB_AUTH_MECHANISM")  # SCRAM-SHA-1, SCRAM-SHA-256, etc.

# Performance and optimization settings
MONGODB_READ_PREFERENCE = os.environ.get("MONGODB_READ_PREFERENCE", "primary")  # primary, secondary, etc.
MONGODB_WRITE_CONCERN_W = os.environ.get("MONGODB_WRITE_CONCERN_W", "1")
MONGODB_WRITE_CONCERN_J = os.environ.get("MONGODB_WRITE_CONCERN_J", "false").lower() == "true"
MONGODB_READ_CONCERN_LEVEL = os.environ.get("MONGODB_READ_CONCERN_LEVEL", "local")  # local, majority, etc.

# 确保日志目录存在
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "mongo_mcp.log"

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_MAX_FILE_SIZE = int(os.environ.get("LOG_MAX_FILE_SIZE", "10485760"))  # 10MB default
LOG_BACKUP_COUNT = int(os.environ.get("LOG_BACKUP_COUNT", "5"))

# Feature flags
ENABLE_DANGEROUS_OPERATIONS = os.environ.get("ENABLE_DANGEROUS_OPERATIONS", "false").lower() == "true"
ENABLE_ADMIN_OPERATIONS = os.environ.get("ENABLE_ADMIN_OPERATIONS", "true").lower() == "true"
ENABLE_INDEX_OPERATIONS = os.environ.get("ENABLE_INDEX_OPERATIONS", "true").lower() == "true"

# 创建日志格式
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)

# 创建日志文件处理程序，指定UTF-8编码和轮转
from logging.handlers import RotatingFileHandler
file_handler = RotatingFileHandler(
    LOG_FILE, 
    encoding='utf-8',
    maxBytes=LOG_MAX_FILE_SIZE,
    backupCount=LOG_BACKUP_COUNT
)
file_handler.setFormatter(log_formatter)

# 创建控制台处理程序（仅在开发模式下）
console_handler = None
if os.environ.get("MCP_ENV", "production").lower() == "development":
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

# 配置根日志记录器
logger = logging.getLogger("mongo-mcp")
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(file_handler)

if console_handler:
    logger.addHandler(console_handler)

# Log configuration on startup
def log_configuration():
    """Log current configuration settings."""
    logger.info("=== MongoDB MCP Configuration ===")
    logger.info(f"MongoDB URI: {MONGODB_URI}")
    logger.info(f"Default Database: {MONGODB_DEFAULT_DB or 'Not set'}")
    logger.info(f"Connection Pool: {MONGODB_MIN_POOL_SIZE}-{MONGODB_MAX_POOL_SIZE}")
    logger.info(f"Server Selection Timeout: {MONGODB_SERVER_SELECTION_TIMEOUT_MS}ms")
    logger.info(f"Socket Timeout: {MONGODB_SOCKET_TIMEOUT_MS}ms")
    logger.info(f"Connect Timeout: {MONGODB_CONNECT_TIMEOUT_MS}ms")
    logger.info(f"Max Documents Limit: {MONGODB_MAX_DOCUMENTS_LIMIT}")
    logger.info(f"Default Batch Size: {MONGODB_DEFAULT_BATCH_SIZE}")
    logger.info(f"TLS Enabled: {MONGODB_TLS_ENABLED}")
    logger.info(f"Read Preference: {MONGODB_READ_PREFERENCE}")
    logger.info(f"Write Concern W: {MONGODB_WRITE_CONCERN_W}")
    logger.info(f"Write Concern J: {MONGODB_WRITE_CONCERN_J}")
    logger.info(f"Read Concern Level: {MONGODB_READ_CONCERN_LEVEL}")
    logger.info(f"Dangerous Operations Enabled: {ENABLE_DANGEROUS_OPERATIONS}")
    logger.info(f"Admin Operations Enabled: {ENABLE_ADMIN_OPERATIONS}")
    logger.info(f"Index Operations Enabled: {ENABLE_INDEX_OPERATIONS}")
    logger.info(f"Log Level: {LOG_LEVEL}")
    logger.info("=== Configuration End ===")


# Connection options dictionary for MongoDB client
def get_connection_options():
    """Get MongoDB connection options based on configuration."""
    options = {
        "minPoolSize": MONGODB_MIN_POOL_SIZE,
        "maxPoolSize": MONGODB_MAX_POOL_SIZE,
        "maxIdleTimeMS": MONGODB_MAX_IDLE_TIME_MS,
        "serverSelectionTimeoutMS": MONGODB_SERVER_SELECTION_TIMEOUT_MS,
        "connectTimeoutMS": MONGODB_CONNECT_TIMEOUT_MS,
        "authSource": MONGODB_AUTH_SOURCE,
    }
    
    # Add socket timeout if specified
    if MONGODB_SOCKET_TIMEOUT_MS > 0:
        options["socketTimeoutMS"] = MONGODB_SOCKET_TIMEOUT_MS
    
    # Add TLS options if enabled
    if MONGODB_TLS_ENABLED:
        options["tls"] = True
        if MONGODB_TLS_CA_FILE:
            options["tlsCAFile"] = MONGODB_TLS_CA_FILE
        if MONGODB_TLS_CERT_FILE:
            options["tlsCertificateKeyFile"] = MONGODB_TLS_CERT_FILE
    
    # Add authentication mechanism if specified
    if MONGODB_AUTH_MECHANISM:
        options["authMechanism"] = MONGODB_AUTH_MECHANISM
    
    return options
