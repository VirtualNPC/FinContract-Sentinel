# 合规知识库建设说明

本说明用于指导法规/制度文本的入库、版本管理与审计留存，不包含任何法条全文。

## 1. 数据来源
- 政府或权威机构公开渠道。
- 已获得授权的商业法规数据库。
- 企业内部制度文件（合同管理制度、审批流程、报销标准等）。

## 2. 结构化要求
每条记录必须是条款级文本，字段如下：
- doc_id：法规/制度唯一标识（建议英文大写）。
- title：法规/制度标题。
- version：版本号或发布日期。
- effective_date：生效日期。
- source：来源URL或内部制度编号。
- chunk_id：条款编号或分段编号。
- text：条款文本。

## 3. 入库文件格式
- 文件路径：data/knowledge/knowledge.jsonl
- 每行一条 JSON 记录，字段与2.2一致。

## 4. 版本与回滚
- 任何更新必须保留旧版本记录，并在doc_id或version中体现。
- 规则与提示词需映射到具体doc_id与chunk_id，确保可追溯。

## 5. 审核输出约束
- 若审核项缺少匹配的法条/制度条款，则输出必须标记为“需人工复核”。
- 每条审核结论必须输出 basis（法规条款）与 evidence（原文位置）。

## 6. 来源清单与入库清单
- 允许来源清单：data/knowledge/sources.yaml
- 入库文档清单：data/knowledge/documents.yaml（需要填写具体doc_id与URL）
- 原始下载目录：data/knowledge/raw/

## 7. 批量入库流程
1) 运行发现脚本，生成documents.yaml：
```
python scripts/knowledge_discover.py --sources data/knowledge/sources.yaml
```
2) 维护documents.yaml，补齐缺失的version/effective_date字段。
3) 运行入库脚本：
```
python scripts/knowledge_ingest.py --documents data/knowledge/documents.yaml --rate-limit 1.0
```
4) 校验knowledge.jsonl并进行抽样复核，确保条款与来源一致。

## 8. 合规与节流
- 仅抓取公开或已授权文档；企业内部制度需在授权范围内使用。
- 保持请求频率与来源站点要求一致，避免高频抓取造成风险。
