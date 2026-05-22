# 技术栈说明

## 1. 核心技术栈
- 编程语言：Python 3.11
- Web框架：FastAPI
- LLM编排：LangChain 0.2
- 数据库：PostgreSQL 15 + pgvector
- 缓存与任务队列：Redis 7 + Celery
- 向量检索：Chroma（本地）/ Pinecone（生产）

## 2. 文档与数据处理
- PDF：PyPDF2, pdfplumber, pdf2image
- Excel：pandas, openpyxl
- OCR：阿里云OCR / 腾讯云OCR

## 3. 可观测性与安全
- 结构化日志：structlog
- 安全要求：TLS 1.3 + AES-256
- 审计：关键操作日志至少保留3年

## 4. 交付与部署
- 容器化：Docker + Docker Compose
- CI/CD：GitHub Actions（规划）

## 5. 版本策略
- Python依赖在pyproject.toml中锁定范围版本
- 规则与法条库版本化，支持回滚与审计追踪

## 6. 可替换组件
- 向量库可替换：Qdrant（自建）
- 任务队列可替换：RabbitMQ
- OCR可替换：PaddleOCR（本地）
