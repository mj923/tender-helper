# TOOLS.md - 虾虾投标工具使用规范

## 文档处理

| 操作 | 工具/技能 | 说明 |
|------|----------|------|
| **PDF 解析（唯一指定）** | `pdf-reader-cn` | 招标文件 PDF 全量解析、文本提取，不支持其他 PDF 工具 |
| **Word(.docx) 读取/分析** | `feishu-fetch-doc` | 读取飞书云空间中的 DOCX 文件 |
| **Word(.docx) 生成/排版** | `feishu-create-doc` | 从 Markdown 创建飞书云文档 |
| **飞书文档更新** | `feishu-update-doc` | overwrite / append / replace_range 等 7 种更新模式 |
| **飞书多维表格** | `feishu-bitable` | 创建/查询/编辑多维表格（投标计划表、检查表） |
| **飞书云空间文件管理** | `feishu_drive_file` | 上传/下载/复制/移动文件，获取 file_token |

## IMA 笔记

| 操作 | 工具 | 说明 |
|------|------|------|
| **读取企业资质清单** | `ima-skill`（ima_api） | 读取笔记 `7468934299129215`《集团企业资质清单》 |
| **搜索笔记** | `ima-skill`（search_note） | 按标题/正文搜索 ima 笔记 |

## Ontology

| 操作 | 工具 | 说明 |
|------|------|------|
| **查询/写入** | 本地 Python 脚本 | 读写 `memory/ontology/graph.jsonl` |
| **实体类型** | — | BiddingProject / TenderDocument / Organization / Requirement / ScoringCriteria / Milestone / Task / BidDocument / Event |

## 历史经验检索

| 操作 | 工具 | 说明 |
|------|------|------|
| **历史项目经验** | `memory_search` | 语义搜索 memory/*.md 和 MEMORY.md |
| **外部资料补充** | `web_search` / `tavily_search` | 搜索政策法规、评分标准参考（可选） |

## 流程图/架构图

| 操作 | 工具 | 说明 |
|------|------|------|
| **流程图绘制** | `lark-whiteboard`（Mermaid 路径） | 工作流/架构图/时序图，输出 PNG 或飞书画板 |

## 硬性规则

- **PDF 解析只使用 `pdf-reader-cn`，禁止使用 `pdf` 工具**
- 飞书文档创建/更新优先使用 Markdown 格式，不直接操作二进制
- Ontology 是项目信息的唯一真实来源，不依赖日记缓存
- 所有产出文件统一存入飞书云空间，记录 file_token
