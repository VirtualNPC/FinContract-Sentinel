# 合规知识库目录

将已获得授权或公开可用的法律法规与企业制度文件整理为条款级文本后写入
`knowledge.jsonl`。每行一条 JSON 记录，字段如下：

- doc_id: 唯一法规/制度标识
- title: 标题
- version: 版本号或发布日期
- effective_date: 生效日期
- source: 来源URL或内部制度编号
- chunk_id: 条款或分段编号
- text: 条款文本

示例（仅结构演示，不含真实法条内容）：
{"doc_id":"PRC_CIVIL_CODE_CONTRACT","title":"中华人民共和国民法典（合同编）","version":"2021-01","effective_date":"2021-01-01","source":"https://example.gov.cn","chunk_id":"502","text":"..."}

相关文件：
- sources.yaml：允许来源清单
- documents.yaml：入库文档清单（需填写具体doc_id与URL）
- raw/：原始下载文件目录
 - scripts/knowledge_discover.py：发现文档列表
 - scripts/knowledge_ingest.py：批量入库
