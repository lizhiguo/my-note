# LLM-Wiki 四操作详解

OKF frontmatter 规则见 `okf-spec-summary.md`。本文讲操作流程与判断标准。

---

## 摄入（ingest）

### 何时触发

- 用户给 URL、文件路径，或粘贴大段内容
- 用户在 `sources/` 建立了手写笔记（如 `sources/02 技术/...`，无排版负担自由记录）
- 用户说「把这篇整理进去」「读一下这个」

### 流程

**第 1 步：完整读来源**

不要skim。多文件先列清单，问用户：
- 全部读
- 先读前 N 个
- 只读指定某几个

来源很长时主动报告并提议分批，不要闷头全读。

**第 2 步：先汇报再写**

写之前告诉用户：
- 提取到哪些关键实体/概念
- 主要结论是什么
- 会触及哪些既有页面（列出具体文件名）
- **有发现的矛盾**（如果有）

这一步不能跳。跳过就是闭门写，用户失去了纠错机会。

**第 3 步：写或更新页面**

| 情况 | 动作 |
|------|------|
| 命中既有页面 | 整合新信息进正文，更新 `generated.at`，`sources` 追加条目 |
| 新主题 | 按页面格式新建，文件名用中文（与本库一致） |
| 部分重合 | 拆分：既有页面保留，新增独立页面，互相链接 |
| **发现矛盾** | **显式标注，停下问用户** |

矛盾标注格式：

```markdown
> ⚠️ 与 [[DDD与整洁架构]] 的「薄聚合根」结论矛盾：
> 该页主张完整聚合根，本文的场景（子实体 50 万行）下完整加载会 OOM。
> 可能原因：适用规模不同。已向用户确认。
```

**严禁静默覆盖。** 两个来源打架比一个干净但错误的页面更有价值。

**第 4 步：更新索引**

`wiki/索引.md` 是总入口。不更新索引的页面等于不存在。

更新三处：
- 对应分类行的「已收录主题」加新页面
- 「导航与说明」表更新摘要与日期
- 顶部「最后更新」日期与页面数

**第 5 步：追加操作日志**

`wiki/操作日志.md` 追加，**永不修改历史条目**：

```markdown
## [2026-10-07] ingest | Redis 缓存设计实践
Source: https://redis.io/docs/latest/develop/use-cases/caching/
Pages affected: 07-网络与协议/缓存设计.md (new), 06-数据库与存储/数据库与存储.md (updated), 索引.md (updated)
Key points: 缓存三大问题（穿透/击穿/雪崩）的成因与对策；TTL 抖动策略
Note: 与 [[JPA与持久化]] 的二级缓存建议存在张力，已标注待确认
```

格式固定，可 grep：`grep "^\## \[" 操作日志.md | tail -5`

**第 6 步：报告**

明确说：更新 N 页，新建 M 页，列出文件名。有矛盾要单独提。

### 摄入开发类资料的额外动作

| 识别到什么 | 额外做 |
|------------|--------|
| 一个技术选择 | 考虑在 `wiki/` 对应分类落 ADR 决策记录 |
| 某个项目的设计 | 在 `wiki/` 对应分类建项目页并互链 |
| 可复用的领域知识 | **同时**写进 `wiki/` 对应分类 |
| 推翻既有结论 | 标 deprecated 或显式矛盾标注，不要偷偷改 |

---

## 查询（query）

### 流程

1. **先读 `wiki/索引.md`** — 唯一入口，不跳步
2. 从索引挑 **2–5 个**最相关页面，读它们
3. 综合回答，**行内引用** `(→ [[页面名]])`
4. 追加操作日志：`## [YYYY-MM-DD] query | 问题摘要`
5. **问：要不要存成新页面？**

### 引用格式

```markdown
## 结论

订单状态用状态模式而非枚举字段，因为状态转移有 12 条边且仍在增加，
枚举方案的分支逻辑已分散在 5 个 service 里。(→ [[DDD与整洁架构]])

## 展开

...(→ [[0001 订单状态机选用状态模式]])
```

### 回答格式

用户没指定时的默认选择：

| 问题类型 | 格式 |
|----------|------|
| 对比、选型 | 表格 |
| 枚举、清单 | 无序列表 |
| 流程、步骤 | 有序列表 |
| 关系、架构 | mermaid 图 + 文字 |
| 单个事实 | 一句话 + 引用 |

### 一定要问的收尾

**「这个分析要不要存成页面？」** 好答案不该烂在聊天记录里。存下来才能被下次查询复用，这是知识库复利的来源。

---

## 体检（lint）

### 跑脚本

```bash
# <skill_dir> 即本 skill 所在根目录
python <skill_dir>/scripts/okf_lint.py <bundle_root>
```

| 参数 | 作用 |
|------|------|
| 无参 | 人类可读报告（默认） |
| `--json` | 机器可读，供其他工具消费 |
| `--strict` | 有 P0 时退出码 1，可进 pre-commit |

### 检查项

| 规则 | 级别 | 含义 |
|------|------|------|
| `frontmatter-parse` | P0 | 缺 frontmatter 或 YAML 不可解析 |
| `type-missing` | P0 | 缺 `type`（OKF 唯一必填项） |
| `encoding` | P0 | 文件编码无法识别 |
| `link-broken` | P1 | 断链，目标不存在 |
| `sources-shape` / `sources-resource` | P1 | sources 结构或必填项错 |
| `actor-format` | P1 | actor 不符合 `human:` / `producer/version` / `process:` 约定 |
| `status-invalid` | P1 | status 不在 draft/stable/deprecated |
| `timestamp-format` | P1 | 时间戳非 ISO 8601 |
| `legacy-field` | P1 | v0.1 遗留 `timestamp` / `# Citations` |
| `index-missing` | P1 | 页面未在索引中提及 |
| `stale` | P1 | 已过 `stale_after` |
| `generated-by` / `verified-by` | P1 | 条目内必填项缺失 |
| `type-unknown` | P2 | type 不在词表（可能拼写漂移） |
| `link-roadmap` | P2 | Hub 页的规划主题，尚未撰写（正常） |
| `link-placeholder` | P2 | 含「待补/待写」标记的占位链接 |
| `section-missing` | P2 | 缺 `## 概述` / `## 相关` |
| `desc-missing` | P2 | 缺 description，索引摘要会为空 |
| `source-unused` | P2 | sources id 未被脚注引用 |
| `footnote-unlinked` | P2 | 脚注无对应 sources id |

### 豁免规则（脚本已实现）

| 情况 | 处理 |
|------|------|
| `sources/` 下的文件 | 不校验 frontmatter（不可变原始层） |
| `index.md` / `log.md` | 豁免 frontmatter |
| `wiki/索引.md`、`操作日志.md`、`知识库使用指南.md` | schema 文件，豁免 |
| `templates/` | 模板，豁免 |
| `.okf-backup/` | 备份，豁免 |
| 附件链接（png/pdf/xlsx 等） | 不算断链 |
| Hub 页的未撰写主题 | P2 而非 P1 |

### 报告纪律

**先给清单，等用户决定，批量改动前必须确认。**

好的呈现：

```markdown
体检完成。3 个问题需要你决定怎么处理：

**P0 破损（1 项）**
- tech/订单系统-架构设计.md — frontmatter YAML 解析失败（第 12 行缩进错误）

**P1 失真（2 项）**
- projects/订单系统.md — 未在索引中提及，新文档忘了登记
- decisions/0001-xxx.md — 已过 stale_after（2026-08-01），内容可能过期

**P2 优化（45 项）**
- 41 项 Hub 页规划主题（正常，不建议动）
- 4 项 sources id 未被脚注引用

要我修 P0 和 P1 吗？P2 建议先放着。
```

坏的呈现：直接改一堆文件然后报告「已优化知识库」。

### 脚本不会做的事

脚本是确定性的，**不做语义判断**：

| 判断 | 谁做 |
|------|------|
| 页面内容是否过期 | 你（读内容判断） |
| 两个页面结论是否矛盾 | 你（对比内容） |
| 该建新页还是补既有页 | 你（理解主题） |
| 链接语义对不对 | 你（读上下文） |
| 文档是否够完整 | 你 |

脚本只管格式层面的机械正确性。

---

## 初始化（init）

仅当目录为空或缺 schema 时执行。

1. 建基础目录：`sources/`、`sources/09 资源/attachments/`、`sources/09 资源/templates/`、`wiki/`（**严禁预建 wiki/ 分类子目录**）
2. 写 `wiki/索引.md` 骨架：空表头，不预设分类
3. 写 `wiki/操作日志.md`，记 Initialization 初始化条目
4. 写根保留文件 `index.md` 与 `log.md`
5. 告知用户：可直接在 `sources/` 下自由手写笔记，`wiki/` 分类目录由 Agent 在后续摄入（ingest）时按需动态创建

**不要重复 init 已存在的 bundle。** 现有知识库先跑一遍 lint 看缺什么。

---

## 迁移既有文档

已有文档缺 frontmatter 时：

```bash
# 先预览（<skill_dir> 即本 skill 所在根目录）
python <skill_dir>/scripts/okf_migrate.py <bundle_root>

# 确认无误后执行（自动备份到 .okf-backup/）
python <skill_dir>/scripts/okf_migrate.py <bundle_root> --apply

# 只处理某个目录
python <skill_dir>/scripts/okf_migrate.py <bundle_root> --apply --only wiki/02
```

推断规则：
- 目录 → type：`concepts/`→Concept、`projects/`→Project、`tech/`→Tech Design、`decisions/`→ADR、`people/`→Person
- `wiki/0X-*/`：文件名等于分类名（去数字前缀）→ Hub，否则 Concept
- description：取引用块首行，否则 H1 后第一段首句
- sources：从正文「## 来源」小节的 markdown 链接反推
- `generated.at`：用文件 mtime，反映真实最后修改时间
- `generated.by`：`workbuddy/gpt-5`（迁移是 agent 做的）

**迁移后必须人工校准**：
- 抽查 3–5 个页面的 description 是否贴切
- 核对 `status` 是否有该标 `draft` 的
- 确认 `sources` 的 `resource` 路径能解析
