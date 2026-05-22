# 环境准备说明

本项目面向企业级审核场景，环境准备以可复现、可审计为原则。

## 1. 必备软件
- Python 3.11（建议使用官方发行版）
- Git
- Docker Desktop（可选，用于本地启动PostgreSQL/Redis）

## 2. Python环境
1) 创建虚拟环境
```
python -m venv .venv
```
2) 激活虚拟环境
```
.\.venv\Scripts\activate
```
3) 安装依赖
```
pip install -e .
```
开发环境依赖（可选）：
```
pip install -e ".[dev]"
```

## 3. 运行依赖服务（推荐Docker）
```
docker-compose up -d
```
启动后本地服务：
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## 4. 环境变量
复制并修改配置：
```
copy .env.example .env
```
关键配置项：
- POSTGRES_DSN
- REDIS_URL
- OCR_PROVIDER
- KNOWLEDGE_DIR
- PYTHON_BASE_IMAGE（Docker Hub受限时使用镜像源）

## 5. 启动API服务
```
uvicorn fincontract.api.main:app --reload
```

## 6. 测试与质量
- 运行测试：
```
pytest
```
- 代码规范（可选）：
```
ruff check .
black .
```

## 7. 合规知识库准备
- 知识库条款文件位置：data/knowledge/knowledge.jsonl
- 格式要求详见：docs/engineering/knowledge-base.md

## 8. 常见问题排查
- 无法连接数据库：检查docker-compose服务是否启动。
- LLM或OCR不可用：确认外部服务配置与密钥。
- 审核结果缺少依据：检查knowledge.jsonl是否包含对应条款。
- Docker构建基础镜像拉取失败：设置PYTHON_BASE_IMAGE为可用镜像源。
