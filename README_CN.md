# Mongo-MCP

[English](README.md) | 简体中文

一个用于 MongoDB 操作的机器聊天协议（Machine Chat Protocol, MCP）服务。该服务提供了一套工具，使大型语言模型（LLMs）能够通过基本的 CRUD 操作和管理任务与 MongoDB 数据库进行交互。

## 运行条件

- Python 3.10 及以上版本
- 已安装并运行中的 MongoDB 数据库服务
- 推荐使用 [uv](https://github.com/astral-sh/uv) 运行程序

## 功能特性

- MongoDB 实例连接管理
- 数据库和集合的列表查询
- 文档的增删改查（CRUD）操作
  - 插入文档
  - 查询文档（支持复杂查询和投影）
  - 更新文档
  - 删除文档
- 完整支持 MongoDB 查询语法和投影操作
- 完善的错误处理和日志记录
- 基于标准输入/输出（stdio）的 MCP 传输实现

## 使用说明

### 使用 uvx 安装并直接运行

```bash
uvx run mongo-mcp
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
                "MONGODB_DEFAULT_DB": "MONGODB_DEFAULT_DB",
                "LOG_LEVEL": "INFO"
            }
        }
    }
}
```
### 环境变量配置说明

- `MONGODB_URI`: MongoDB 连接字符串（默认值: "mongodb://localhost:27017"）
- `MONGODB_DEFAULT_DB`: 默认数据库名称（可选）
- `LOG_LEVEL`: 日志级别（默认值: "INFO"）
  - 可选值: DEBUG, INFO, WARNING, ERROR, CRITICAL

### 支持的操作

- 列出所有数据库
- 列出指定数据库中的所有集合
- 插入文档
- 查询文档（支持查询条件和字段投影）
- 更新文档（支持单个和批量更新）
- 删除文档（支持单个和批量删除）

## 开发指南

1. 克隆仓库
```bash
git clone https://github.com/yourusername/mongo-mcp.git
cd mongo-mcp
```

2. 安装开发依赖
```bash
# 使用 pip
pip install -e ".[dev]"

# 或使用 uv（推荐，安装更快）
uv pip install -e ".[dev]"
```

3. 运行测试
```bash
pytest
```

4. 代码结构
- `server.py`: MCP 服务器实现
- `db.py`: MongoDB 操作核心实现
- `config.py`: 配置管理
- `tools/`: MCP 工具集实现
- `tests/`: 测试用例

## 日志

日志文件默认保存在 `logs` 目录下，可通过环境变量 `LOG_LEVEL` 控制日志级别。

## 许可证

MIT

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交 PR 之前，请确保：

1. 代码通过所有测试
2. 添加了适当的测试用例
3. 更新了相关文档 