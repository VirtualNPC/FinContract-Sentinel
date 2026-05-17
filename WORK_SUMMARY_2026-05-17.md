# 工作说明（2026-05-17）

以下内容为本次在 FinContract Sentinel 项目中的实际修改与新增内容说明，按模块和目的整理。

## 1. 目标与范围
- 依据项目 SKILLS 文档整理可复用的技能清单。
- 给出可落地的技术选型方案。
- 初始化项目骨架（API、Agent 流程、规则引擎、任务队列、基础测试与配置）。

## 2. 新增的技能与选型文件
- skills/skills-index.md
  - 将 SKILLS 文档拆分为可执行的 skill 卡片，覆盖项目治理、代码质量、Agent 架构、LLM 调用、规则引擎、测试与部署等领域。
- skills/tech-selection.md
  - 固化技术选型：Python 3.11、FastAPI、LangChain 0.2、PostgreSQL+pgvector、Chroma/Pinecone、Redis、Celery、Docker、GitHub Actions 等。

## 3. 项目骨架与核心模块
- README.md
  - 说明项目特性、快速启动与目录结构。
- pyproject.toml
  - 定义依赖与开发工具（FastAPI、LangChain、Chroma、Celery、结构化日志等）。
- .env.example
  - 提供数据库、缓存、OCR 供应商等配置样例。
- Dockerfile / docker-compose.yml
  - 提供容器化运行与本地依赖服务（Postgres、Redis）。

### 3.1 API 层（FastAPI）
- src/fincontract/api/main.py
  - FastAPI 入口，挂载健康检查与审核路由。
- src/fincontract/api/routes/health.py
  - /health 端点用于服务健康检查。
- src/fincontract/api/routes/audit.py
  - /audit 端点，接收审核请求并返回审核结果。

### 3.2 Agent 与业务编排
- src/fincontract/agent/state.py
  - 定义审核状态对象（请求ID、文本、风险评分等）。
- src/fincontract/agent/pipeline.py
  - 审核主流程：解析文本 -> 规则评估 -> 风险评分与分级。

### 3.3 规则引擎与规则文件
- src/fincontract/tools/rule_engine.py
  - 支持 regex / keyword / keyword_absent 三类规则，具备加载与执行逻辑。
- src/fincontract/rules/default_rules.yaml
  - 提供基础样例规则（负金额、币种缺失、审批条款）。

### 3.4 OCR 与向量检索接口占位
- src/fincontract/tools/ocr.py
  - OCR 客户端占位，当前未绑定真实供应商。
- src/fincontract/tools/vector_store.py
  - 向量检索接口占位，便于后续替换为 Chroma 或 Pinecone 实现。

### 3.5 业务服务与任务队列
- src/fincontract/services/audit_service.py
  - 业务服务层，封装审核流程调用。
- src/fincontract/workers/celery_app.py
  - Celery 实例配置（Redis 作为 broker/backend）。
- src/fincontract/workers/tasks.py
  - 异步任务封装，便于批量或后台审核。

### 3.6 结构化日志与错误体系
- src/fincontract/core/logging.py
  - 结构化日志（JSON）配置。
- src/fincontract/core/errors.py
  - 定义审核、解析、规则、工具等异常基类。

## 4. 测试与验证
- tests/test_health.py
  - FastAPI /health 端点的最小可用测试。

## 5. 当前可运行能力
- 可启动 API 服务，进行基础审核请求处理。
- 可读取规则文件并输出基础风险评级与发现项。

## 6. 下一步建议（可选）
- 接入真实 OCR 服务（阿里云/腾讯云）。
- 增加向量检索实现与数据库持久化。
- 规则管理与版本控制功能。
- 更完善的审计日志与合规权限控制。
