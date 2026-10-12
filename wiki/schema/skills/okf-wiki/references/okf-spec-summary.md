# OKF v0.2 规范速查

来源：GoogleCloudPlatform/knowledge-catalog `okf/SPEC.md`，Version 0.2。
本文件是查阅用摘要，权威原文在 SPEC.md。冲突时以原文为准。

---

## Bundle 结构

```
bundle/
  index.md          # 保留名，目录清单（bundle 根可带 okf_version）
  log.md            # 保留名，更新历史
  <concept>.md      # 概念文档
  <subdir>/         # 任意层级
```

- `index.md` / `log.md` 在**任意层级**都有既定含义，**不能当概念页用**
- 目录结构与领域无关，生产者自行组织
- 分发方式：git 仓库（推荐，有历史和 diff）/ tarball / 大仓库的子目录
- 标签通过 frontmatter `tags` 表达，OKF 不规定 tag 聚合文件

---

## Frontmatter 字段全表

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ **唯一必填** | 种类标识。未注册，消费者须容忍未知值 |
| `title` | 推荐 | 展示名。省略则从文件名推导 |
| `description` | 推荐 | 一句话摘要。用于 index 生成、搜索片段、预览 |
| `resource` | 推荐 | 底层资产规范 URI。抽象概念可省 |
| `tags` | 推荐 | YAML 字符串数组，跨切面分类 |
| `sources` | 可选 | 溯源列表，见下 |
| `usage_window` | 可选 | `{ from, to }`，框定所有 `usage_count` |
| `generated` | 可选 | `{ by, at }`，`by` 在条目内必填 |
| `verified` | 可选 | 验证事件列表或单个 `{ by, at }` |
| `status` | 可选 | `draft` / `stable` / `deprecated`，缺省 `stable` |
| `stale_after` | 可选 | 绝对时刻，`now >= stale_after` 即过期 |
| `runtime` | Attested Computation 必填 | 执行环境 |
| `parameters` | 可选 | `[{ name, type, required }]` |
| `computation` | 可选 | 计算文件路径；缺省用正文 `# Computation` 围栏 |
| `executor` | 可选 | `{ resource, receipt }` |
| `attester` | 可选 | `{ resource }`，确定性校验代码（无 LLM） |

**扩展**：生产者可加任意键。消费者 round-trip 时 SHOULD 保留未知键，MUST NOT 因未知字段拒绝文档。

**时间戳**：所有时间值一律 ISO 8601 带显式 UTC 偏移，如 `2026-06-30T14:00:00Z`。

---

## sources 条目

```yaml
sources:
  - id: ga4-schema
    resource: https://...        # 条目内必填
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30T00:00:00Z
usage_window: { from: 2026-06-01T00:00:00Z, to: 2026-06-30T00:00:00Z }
```

| 字段 | 必填 | 含义 |
|------|------|------|
| `resource` | ✅ | 具体可跟随的产物（URL / bundle 相对路径 / `references/` 下路径），或范围描述 |
| `id` | 正文引用时强烈建议 | 稳定 key，用于逐条声明归属 |
| `title` | 可选 | 人读标签 |
| `author` | 可选 | 权威性信号 |
| `usage_count` | 可选 | 采用度与活跃度信号 |
| `last_modified` | 可选 | 新鲜度信号，区别于 `generated.at` |
| `usage_window` | 可选 | 单条可覆盖共享值 |

**可信度是推断的，不是存的**。OKF 只记录客观信号，存分数会主观、不可移植、会过期。

`usage_count` 是粗粒度信号，只在「活/死」和数量级层面可比，**读作活跃度与趋势，不是排名**。

**血缘走链接，不走字段**。当 `resource` 指向另一个 OKF 概念时，派生边已在图里，消费者可递归其 `sources` 让可信度传播。

### 逐条声明归属

用 markdown 脚注，label 是 `sources[].id`：

```markdown
`events_` 表按天分片为 `events_YYYYMMDD`。[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

用 key 而非位置索引，因为 agent 频繁重写这些文档，位置索引在列表重排时会静默错配，稳定 id 不会。

---

## 信任与生命周期

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
status: stable
stale_after: 2026-09-23T00:00:00Z
```

- `generated.by` 在条目内必填
- `verified` 多个条目表示独立检查（人签字 + 夜间任务）。"有多新" 取最新 `at`
- `verified` 与 `generated.at` **相互独立**：内容可改而未重新确认，事实可重新确认而未重新生成
- 单个验证者可写成不带列表短横的裸映射，消费者 MUST 当作单元素列表处理

### 信任档位（从 `verified` 推导）

| 条件 | 档位 |
|------|------|
| 无 `verified` | unverified |
| 仅非 `human:` actor | machine-confirmed |
| 有 `human:<id>` | human-reviewed |

**信任档位是建议信号，不是访问控制。** 无信任字段的概念仍可消费，消费者 MUST NOT 拒绝。

### 生命周期

| status | 含义 |
|--------|------|
| `draft` | 尚未评审，可能不完整 |
| `stable` | 缺省值，可消费 |
| `deprecated` | 为链接和历史保留，已非当前 |

`stale_after` 是**绝对时刻**不是相对 TTL，过期判断是纯比较，不依赖阅读时刻。

---

## Actor 约定

| 形式 | 用于 |
|------|------|
| `<producer>/<version>` | agent 与工具，如 `reference_agent/gemini-2.5-pro` |
| `human:<id>` | 人，如 `human:ahormati` |
| `process:<id>` | 自动化流程，如 `process:finance-nightly` |

分类信任档位靠 `human:` 前缀识别，**生产者必须对人工编写/人工确认的内容使用该前缀**。

本机约定：`human:laoli`（老李）、`workbuddy/gpt-5`（本 agent）。

---

## 链接与路径

两种形式：

```markdown
绝对（bundle 相对，推荐）: [customers table](/tables/customers.md)
相对:                        [neighbor](./other.md)
```

- 绝对形式在文档于子目录内移动时**保持稳定**，优先用
- 链接 A→B 断言一个**关系**，关系种类（父子/引用/join/依赖）由周围文字表达，不由链接本身表达
- 图视图消费者通常把所有链接当作**无类型**有向边
- 消费者 MUST 容忍断链：目标不存在不是格式错误，可能只是尚未写出的知识

路径值字段（`resource`、`sources[].resource`、`computation`、`executor.resource`、`attester.resource`）接受：绝对 URL、`/` 开头的 bundle 相对路径、相对路径。

### references/ 约定

`references/` 子目录惯例上把外部材料、运行说明、代码镜像成 bundle 内的一等概念。**是命名惯例，非要求。**

---

## index.md

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description
* [Title 2](relative-url-2) - short description

# Another Section

* [Subdirectory](subdir/) - short description
```

- 可出现在任意目录含 bundle 根
- **无 frontmatter**，唯一例外：bundle 根 `index.md` 可带 `okf_version`
- 目的是渐进式披露：不打开单个文档就能知道有什么
- 条目 SHOULD 带上被链概念 frontmatter 里的 `description`
- 生产者 MAY 自动生成；消费者在缺失时可即时合成

## log.md

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a BigQuery table reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

- 可出现在任意层级，记录该范围的变化史
- 日期标题 MUST 用 ISO 8601 `YYYY-MM-DD`
- **最新在前**
- 条目是散文；开头加粗词（`**Update**` / `**Creation**` / `**Deprecation**`）是惯例非要求

---

## Attested Computation（可信计算）

带**认可的计算方式**的概念，让消费者能确认值是按规定算法算出来的，而非 agent 即兴发挥。

**为什么独立成概念**：
- `runtime` 定义 `parameters` 的含义（SQL 绑定变量？dbt var？Python 参数？）
- 一个计算多消费者复用
- 信任状态按计算独立：revenue / profit / margin 各验证各证明

```yaml
type: Attested Computation
title: Revenue for fiscal year
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-09-23T00:00:00Z
sources:
  - { id: rev-policy, resource: https://wiki.acme/finance/revenue-recognition }
```

正文：

```markdown
# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year
```

两种给法：
- **内联**：正文 `# Computation` 下的单个围栏。适合短计算，与契约并排评审
- **文件**：`computation` 指向路径，正文不放围栏。适合长/生成/与非 OKF 工具共享的计算

**硬约束**：agent 只能为已声明的 `parameters` 供值，MUST NOT 编写或修改 computation。attester 独立重算绑定做比对，因为比对的是 receipt 携带的**展开后产物**（`executed_sql`），所以被改写的查询、被替换的计算文件、被篡改的依赖都会失败。

### 消费流程

1. **发现**：`type: Attested Computation` 是 frontmatter 信号，可提升进 `index.md`
2. **加载**：契约从 frontmatter，计算从正文或 `computation` 文件
3. **参数化**：agent 提供已声明参数的值
4. **执行**：executor 运行并返回 receipt
5. **证明**：attester 跑 receipt，确认溯源（实际跑的 == `computation` 绑声明参数，非 agent 自撰 SQL）与保真（展示值 == receipt 权威源，按 job id 重读而非取 agent 文本）
6. **门禁**：证明失败拒绝展示；`now >= stale_after` 警告或拒绝；成功则展示裁决（如 job log 链接）让信任可见

runtime 产物（receipt）**不存进 bundle**。

### verified vs attestation

| | verified | attestation |
|---|---|---|
| 确认什么 | 定义是否仍符合政策 | 单次运行是否按规定方式产出值 |
| 粒度 | 文档级，慢 | 每次调用，运行时 |
| 存哪 | 存进 bundle | 不存 |

定义过期的概念仍可能证明通过；刚验证的定义每次跑仍需证明。**两者都需要。**

---

## 合规性

一个 bundle 合规当且仅当：

1. 树中每个非保留 `.md` 文件有**可解析的 YAML frontmatter**
2. 每个 frontmatter 有**非空 `type`**
3. 每个保留文件名（`index.md` / `log.md`）在出现时遵循 §8 / §9 结构

消费者 **MUST NOT** 因以下原因拒绝 bundle：
- 缺可选 frontmatter 字段
- 未知 `type` 值
- 未知附加 frontmatter 键
- 断链
- 缺 `index.md`

---

## 版本

- 当前 **0.2**，版本号 `<major>.<minor>`
- minor 升级：向后兼容的新增（可选字段、新惯例标题）
- major 升级：破坏性变更（重命名必填字段、改保留文件名）
- bundle 根 `index.md` 可声明 `okf_version: "0.2"`（**唯一允许 frontmatter 的 index.md**）
- 不理解声明版本 SHOULD 尽力消费而非拒绝

### v0.1 → v0.2 破坏性变更

| 变更 | 替代 |
|------|------|
| `timestamp` | `generated.at`（消费者可回退读 legacy `timestamp`） |
| 正文 `# Citations` 列表 | frontmatter `sources`（SHOULD 读 `sources`，MAY 仍解析 legacy） |

### v0.2 新增

`sources` 及可信度信号（`author`/`usage_count`/`last_modified`）、`usage_window`；`generated`、`verified`；`status`、`stale_after`；新 type `Attested Computation` 及 `runtime`/`parameters`/`computation`/`executor`/`attester`；新惯例标题 `# Computation`；actor 约定。

其余（bundle 结构、保留文件名、必填 `type`、推荐字段、交叉链接、index、log、宽容合规）从 v0.1 原样承继。
