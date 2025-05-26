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

# 确保日志目录存在
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "mongo_mcp.log"

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

# 创建日志格式
log_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# 创建日志文件处理程序，指定UTF-8编码
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(log_formatter)

# 配置根日志记录器
logger = logging.getLogger("mongo-mcp")
logger.setLevel(getattr(logging, LOG_LEVEL))
logger.addHandler(file_handler)
