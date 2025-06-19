# MongoDB MCP 服务

[English](README.md) | 简体中文

这是一个基于 MCP (Model Context Protocol) 的 MongoDB 数据库操作服务，为大语言模型提供完整的 MongoDB 数据库交互功能。

## 🚀 功能特性

### 📊 数据库管理工具
- `list_databases` - 列出所有数据库
- `create_database` - 创建新数据库
- `drop_database` - 删除数据库
- `get_database_stats` - 获取数据库统计信息

### 📦 集合管理工具
- `list_collections` - 列出数据库中的所有集合
- `create_collection` - 创建新集合（支持选项设置）
- `drop_collection` - 删除集合
- `rename_collection` - 重命名集合
- `get_collection_stats` - 获取集合统计信息

### 📄 文档CRUD操作
- `insert_document` - 插入单个文档
- `insert_many_documents` - 批量插入多个文档
- `find_documents` - 查询文档（支持排序、投影、限制）
- `find_one_document` - 查询单个文档
- `count_documents` - 统计文档数量
- `update_document` - 更新文档（单个或批量）
- `replace_document` - 替换文档
- `delete_document` - 删除文档（单个或批量）

### 🔍 索引管理工具
- `list_indexes` - 列出集合的所有索引
- `create_index` - 创建普通索引
- `create_text_index` - 创建文本搜索索引
- `create_compound_index` - 创建复合索引
- `drop_index` - 删除索引
- `reindex_collection` - 重建集合的所有索引

### 📈 聚合操作
- `aggregate_documents` - 执行聚合管道操作
- `distinct_values` - 获取字段的不重复值

### 🔧 监控和管理工具
- `get_server_status` - 获取MongoDB服务器状态
- `get_replica_set_status` - 获取副本集状态
- `ping_database` - 测试数据库连接
- `test_mongodb_connection` - 综合连接测试
- `get_connection_details` - 获取连接详细信息

## 🛠️ 技术栈

- **Python**: 主要编程语言
- **FastMCP**: MCP Python SDK，用于自动生成工具定义
- **PyMongo**: MongoDB 官方 Python 驱动程序
- **uv**: 现代 Python 包管理工具

## 运行条件

- Python 3.10 及以上版本
- 已安装并运行中的 MongoDB 数据库服务
- 推荐使用 [uv](https://github.com/astral-sh/uv) 运行程序

## 📦 安装

1. 克隆仓库：
```bash
git clone https://github.com/441126098/mongo-mcp.git
cd mongo-mcp
```

2. 安装依赖：
```bash
uv sync
```

## 使用说明

### 使用 uvx 安装并直接运行

```bash
uvx mongo-mcp
```
服务器使用标准输入/输出（stdio）传输方式，适合与支持此传输方式的 MCP 客户端集成。

### Cursor 配置样例

如果你使用 [Cursor](https://www.cursor.so/) 作为开发环境，可以在 `.cursor/mcp.json` 文件中添加如下配置以便本地调试：

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

### 环境变量配置说明

#### 基础配置
- `MONGODB_URI`: MongoDB 连接字符串（默认值: "mongodb://localhost:27017"）
- `MONGODB_DEFAULT_DB`: 默认数据库名称（可选）

#### 连接池配置
- `MONGODB_MIN_POOL_SIZE`: 最小连接池大小（默认值: 0）
- `MONGODB_MAX_POOL_SIZE`: 最大连接池大小（默认值: 100）
- `MONGODB_MAX_IDLE_TIME_MS`: 最大空闲时间（毫秒）（默认值: 30000）

#### 超时配置
- `MONGODB_SERVER_SELECTION_TIMEOUT_MS`: 服务器选择超时时间（默认值: 30000）
- `MONGODB_SOCKET_TIMEOUT_MS`: 套接字超时时间（默认值: 0 - 无超时）
- `MONGODB_CONNECT_TIMEOUT_MS`: 连接超时时间（默认值: 20000）

#### 安全配置
- `MONGODB_TLS_ENABLED`: 启用TLS连接（默认值: false）
- `MONGODB_AUTH_SOURCE`: 认证源数据库（默认值: admin）
- `MONGODB_AUTH_MECHANISM`: 认证机制（SCRAM-SHA-1、SCRAM-SHA-256等）

#### 性能设置
- `MONGODB_READ_PREFERENCE`: 读取偏好（默认值: primary）
- `MONGODB_WRITE_CONCERN_W`: 写入关注级别（默认值: 1）
- `MONGODB_READ_CONCERN_LEVEL`: 读取关注级别（默认值: local）

#### 日志配置
- `LOG_LEVEL`: 日志级别（默认值: "INFO"）
  - 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL
- `LOG_MAX_FILE_SIZE`: 日志文件最大大小（字节）（默认值: 10MB）
- `LOG_BACKUP_COUNT`: 备份日志文件数量（默认值: 5）

#### 功能开关
- `ENABLE_DANGEROUS_OPERATIONS`: 启用潜在危险操作（默认值: false）
- `ENABLE_ADMIN_OPERATIONS`: 启用管理操作（默认值: true）
- `ENABLE_INDEX_OPERATIONS`: 启用索引操作（默认值: true）

## 开发指南

1. 克隆仓库
```bash
git clone https://github.com/441126098/mongo-mcp.git
cd mongo-mcp
```

2. 安装开发依赖
```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e ".[dev]"
```

3. 运行测试
```bash
uv run pytest tests/ -v
```

4. 代码结构
- `src/mongo_mcp/server.py`: MCP 服务器实现
- `src/mongo_mcp/db.py`: MongoDB 操作核心实现
- `src/mongo_mcp/config.py`: 配置管理
- `src/mongo_mcp/tools/`: MCP 工具集实现
  - `database_tools.py`: 数据库和集合管理
  - `document_tools.py`: 文档CRUD操作
  - `index_tools.py`: 索引管理
  - `aggregation_tools.py`: 聚合操作
  - `admin_tools.py`: 管理和监控工具
- `src/mongo_mcp/utils/`: 工具模块
- `tests/`: 测试用例

## 测试

项目包含完整的测试覆盖：
- 所有工具模块的单元测试
- MongoDB集成测试
- 隔离组件的模拟测试

运行测试套件：
```bash
# 运行所有测试
uv run pytest

# 详细输出运行
uv run pytest -v

# 运行特定测试文件
uv run pytest tests/test_tools.py
```

## 日志

日志文件默认保存在 `logs` 目录下。日志系统支持：
- 可配置的日志级别
- 基于大小的文件轮转
- UTF-8编码支持
- 包含函数名和行号的结构化日志

## 许可证

MIT

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交 PR 之前，请确保：

1. 代码通过所有测试（`uv run pytest`）
2. 添加了适当的测试用例
3. 更新了相关文档
4. 代码遵循现有的样式规范 