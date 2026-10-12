---
name: okf-wiki
description: "OKF + Karpathy LLM-Wiki 双规范知识库管理器。维护 Obsidian vault 中的知识 bundle：用户在专属手写区（sources/）按旧习惯自由记录，Agent 在编译产物区（wiki/）维护结构化知识网。按 OKF v0.2 写 frontmatter（type/sources/generated/verified/status/stale_after），按 LLM-Wiki 维护 sources/ 不可变层与 wiki/ 编译层。用于摄入来源、查询知识库、体检知识库、初始化新 bundle。当用户要写文档、整理笔记、沉淀知识、建立或维护 Obsidian 知识库、给文档加元数据、查知识库时使用。"
metadata:
  okf_version: "0.2"
  # bundle_root 不写死。运行时从 ~/.agent-wiki.json 的 wikiRoot 解析（见 §0）
  config_file: ~/.agent-wiki.json
---

# okf-wiki — 双规范知识库管理员

你同时遵守两套规范，各管一层，**不重叠**：

| 规范 | 管什么 | 落点 |
|------|--------|------|
| **OKF v0.2** | frontmatter 元数据：来源、可信度、生命周期、计算契约 | 每个 `.md` 文件头部 |
| **Karpathy LLM-Wiki** | 内容架构：原始层不可变、编译层我维护、索引驱动 | 目录结构与操作流程 |

冲突时：**OKF 管字段，LLM-Wiki 管结构**。两者都不矛盾，叠加使用。

---

## 0. 每次开工先定位

```
bundle_root = ~/.agent-wiki.json 的 wikiRoot
```

```json
{ "wikiRoot": "D:/mywork/mydoc/obsidian-knowledge/我的知识库" }
```

**读取顺序**（前面的优先，绝不猜路径）：

1. 命令行/工具参数显式传入的 bundle_root
2. 当前工作目录若已是 bundle（含 `wiki/索引.md`）则用它
3. `~/.agent-wiki.json` 的 `wikiRoot`
4. 以上都没有 → **停下来问用户**，不要假设

`~/.agent-wiki.json` 是**唯一真相源**，任何路径写死在文档或代码里都会漂移。
Windows 下 `~` 即 `%USERPROFILE%`（`C:\Users\<user>`）。

确认三件事再动手：
1. `wiki/索引.md` 存在吗？不存在则先 `init`
2. 用户给的是新资料（→ ingest）还是问题（→ query）还是体检（→ lint）
3. 目标目录存在吗？不存在先建

---

## 1. Bundle 结构

```
我的知识库/                               ← Bundle Root
  ├── index.md / log.md                   ← OKF 根保留文件
  ├── sources/                            ← 【你的专属手写区，按旧习惯组织】
  │   ├── 01 学习笔记/
  │   ├── 02 技术/
  │   │   ├── 后端/
  │   │   └── 前端/
  │   ├── 03 运维/
  │   ├── 04 工具/
  │   ├── 05 项目/
  │   ├── 06 儿子数学/
  │   └── 09 资源/                        ← 【你的专属资源区，整合低频资产】
  │       ├── attachments/                ← 图片与文件附件（对应 09 attachment）
  │       └── templates/                  ← 页面模板（对应 00 Templats）
  │
  └── wiki/                               ← 【Agent 的编译产物区】
      ├── 索引.md
      ├── 操作日志.md
      ├── schema/                         ← 【规范与配置区】
      │   └── 知识库使用指南.md
      ├── 01-Kotlin语言/                  ← （随内容摄入按需动态生成，初始不存在）
      ├── 02-后端架构/                    ← （随内容摄入按需动态生成，初始不存在）
      └── ...
```

**区域职责与硬规则**：
- **`sources/` — 用户手写区（不可变层）**：
  - **手写无负担**：想记笔记时，直接点开你熟悉的 `sources/02 技术/...` 或 `sources/01 学习笔记/...` 直接写。
  - **命名与排版自由**：文件怎么命名、段落怎么排版，完全由你说了算，不需要适配任何复杂的 Agent 规则。
  - **Agent 只读不改**：Agent **绝对不直接修改**此目录文件。这是不可变的真实来源（Truth）。
  - **免除元数据校验**：不要求 OKF frontmatter。零散记录、手绘草稿、网页剪藏均可直接存放。
  - **`sources/09 资源/` 低频资源区**：集中收纳附件与模板。
    - `sources/09 资源/attachments/`：存放手写笔记中的截图、架构图、PDF 等附件。
    - `sources/09 资源/templates/`：存放 Obsidian 笔记模板。
    - Agent 对此目录只读不碰。
- **`wiki/` — Agent 编译区（知识层）**：
  - Agent 专属维护。用户只读，Agent 负责编译、写入与持续维护。
  - Agent 从 `sources/` 读取笔记，提炼核心概念与结论，编译为跨文档的主题知识网络（如 `01-Kotlin语言/`、`02-后端架构/` 等）。
  - `wiki/` 内所有知识页必须严格遵照 OKF frontmatter 规范，并建立高密度 `[[双链]]` 引用。
  - `wiki/索引.md` 是全局导航入口，`wiki/操作日志.md` 记录编译与查询历史。
  - `wiki/schema/` 存放规范文件（如 `知识库使用指南.md`），供所有 AI 助手阅读遵循，免除 frontmatter 校验。
- **根目录保留文件（`index.md` / `log.md`）**：
  - OKF 根保留文件，作为 bundle 级清单与全局流水。**不能用作概念页**。

### 1.1 手写区（sources/）笔记组织建议

虽不设硬性格式约束，但推荐采用以下颗粒度组织笔记，兼顾书写轻松与编译质量：

1. **纯语言/语法技巧（合写归纳）**：
   - **形式**：同一门语言的零散技巧、语法糖合写在同一个文件中（如 `sources/02 技术/后端/kotlin语法技巧.md`）。
   - **排版**：内部使用二级标题区分（如 `## 异常处理优雅写法`、`## 数据类扩展用法`）。
   - **好处**：不必为两行小代码单独建文件，书写无压力。
2. **框架整合与工程实战（单独成文）**：
   - **形式**：涉及具体框架、架构模式或完整场景的笔记，单独开一篇（如 `sources/02 技术/后端/SpringBoot配置类使用-Kotlin实践.md`）。
   - **好处**：主题明确，便于日后针对框架或架构方案检索。
3. **第三方库与工具包（清单式归纳）**：
   - **形式**：同一领域的实用依赖库集中在一个文件记录（如 `sources/02 技术/后端/Kotlin好用库.md`）。
   - **排版**：记录库名、适用场景及简要调用范例。
4. **独立工具与平台**：
   - 放入 `sources/04 工具/`（如命令行工具、抓包软件、调试 API）。
5. **随手灵感与未分类碎片**：
   - 放入 `sources/06 随手记/`（如临时想法、待读链接）。
6. **网页长文剪藏**：
   - 默认存放在外层临时 `Clippings/` 目录，筛选出有价值的再移入 `sources/` 正式目录触发编译。

---

## 2. OKF frontmatter 规范（写每个文件都要遵守）

### 2.1 必填

```yaml
type: Concept        # 唯一必填字段。缺失则整个 bundle 不合规
```

### 2.2 推荐

```yaml
title: 展示名                     # 缺省则从文件名推导
description: 一句话摘要            # index.md 引用这句
resource: https://... 或 /路径    # 底层资产 URI，抽象概念可省
tags: [a, b, c]
```

### 2.3 信任与生命周期（`dev-workflow` 场景必写）

```yaml
generated: { by: human:laoli, at: 2026-10-07T02:20:00Z }
verified:  { by: human:laoli, at: 2026-10-07T02:20:00Z }
status: draft            # draft | stable | deprecated，缺省视为 stable
stale_after: 2027-01-01T00:00:00Z
```

**Actor 约定**（§7 of SPEC）：
- `human:<id>` — 人写的、人确认的。本机用户是 `human:laoli`
- `<producer>/<version>` — agent 写的。本机 agent 是 `workbuddy/gpt-5`
- `process:<id>` — 自动化流程

**时间戳硬约束**：所有时间必须 ISO 8601 且带显式时区（如 `+08:00` 或 `Z`），严禁无时区的本地时间浮串（如 `2026-10-07T10:20:00`）。

**信任档位**（从 `verified` 推导，别手写）：
| 条件 | 档位 |
|------|------|
| 无 `verified` | unverified |
| 只有非 `human:` actor | machine-confirmed |
| 有 `human:<id>` | human-reviewed |

**verified 与 generated 独立**：内容改了不必重新 verified，事实确认了也不必重新生成。改内容 → 更新 `generated.at`。

### 2.4 来源溯源

```yaml
sources:
  - id: ddd-note              # 稳定 key，正文用 [^ddd-note] 脚注引用
    resource: /sources/02 技术/后端/DDD.md
    title: DDD 笔记
    author: human:laoli
    last_modified: 2026-10-02T00:00:00Z
```

- `resource` 在条目内**必填**，可以是 URL、bundle 相对路径、或范围描述
- `id` 正文引用时**强烈建议有**，用 markdown 脚注 `[^id]` 关联
- 正文不要写 `# Citations` 列表（那是 v0.1 旧做法，已被 `sources` 取代）

### 2.5 type 词表（本 bundle 约定）

OKF 不注册 type，本 bundle 统一用这套，避免同义碎片化。所有编译产物统一存放在 `wiki/` 及其分类目录下：

| type | 用在哪 | 目录 |
|------|--------|------|
| `Concept` | 通用知识概念 | `wiki/` 各分类目录 |
| `Hub` | 分类枢纽页 | `wiki/0X-*/` |
| `Source Digest` | 一份原始资料的摘要页 | `wiki/` 各分类目录 |
| `Project` | 项目汇总与架构演进 | `wiki/` 各分类目录 |
| `Tech Design` | 技术设计与方案 | `wiki/` 各分类目录 |
| `ADR` | 架构决策记录 | `wiki/` 各分类目录 |
| `Person` | 人/团队 | `wiki/` 各分类目录 |
| `Schema` | 规范/配置 | `wiki/` |
| `Playbook` | 操作手册/SOP | `wiki/` 各分类目录 |
| `Attested Computation` | 带计算契约的可信计算 | `wiki/` |

不确定时用 `Concept`。**不要自造同义 type**（不要 `TechDesign`、`tech-design`、`技术设计`）。

---

## 3. 页面正文格式（沿用本库既有风格，勿改）

```markdown
# 标题

> 一句话摘要，与 frontmatter description 一致

## 概述
整体讲清是什么、为什么重要

## 关键结论 / 踩坑点
- **分类**
  - 具体条目，带 `[^脚注]` 引用

## 相关
- [[页面名]] —— 关联原因

## 争议与盲区
- 已知局限、争议、无绝对答案的点
- 待确认项

## 来源
- [原始资料](../../sources/02 技术/后端/DDD.md) — YYYY-MM-DD
```

**保留中文的 `## 概述 / ## 相关 / ## 争议与盲区`**——这是本库 17 个页面的一致约定，改了会破坏一致性。

链接规则：
- **页面间引用用 `[[双链]]`**（Obsidian 图谱靠它）
- **引用 sources/ 原始资料用 markdown 相对链接**（`[DDD笔记](../../sources/02 技术/后端/DDD.md)`）
- frontmatter 里的路径一律用 `/` 开头的 bundle 相对路径

---

## 4. 四种操作

### init — 初始化 bundle

仅当目录为空或缺 schema 时执行：
1. 建立基础目录：`sources/`、`sources/09 资源/attachments/`、`sources/09 资源/templates/`、`wiki/`、`wiki/schema/`（**严禁预建 wiki/ 分类子目录**）
2. 写 `wiki/索引.md` 空骨架（纯空表头，不预设任何分类行）
3. 写 `wiki/操作日志.md`，记 Initialization 初始化条目
4. 写 `wiki/schema/知识库使用指南.md`，为所有进库的 AI 助手提供本地统一规范
5. 写根保留文件 `index.md` 与 `log.md`
6. 告知用户：可在 `sources/` 自由手写笔记。`wiki/` 保持干净，所有分类目录随笔记摄入按需动态创建

### ingest — 摄入来源

触发：用户在 `sources/` 放入手写笔记，或提供 URL、文档、粘贴内容。

1. **完整读**来源。从 `sources/` 读取用户手写笔记或外部材料。多文件先列清单，问用户是否全读还是先读一半
2. **先汇报再写**：告诉用户提取到什么关键实体、主要结论、会触及 `wiki/` 里的哪些既有页面
3. **写页面到 `wiki/`**：
   - 命中既有页面 → 整合进去，更新 `generated.at`，`sources` 追加
   - **来源是既有笔记的修改版时**：先比对变更（Git Diff / 新旧对比），仅演进受影响章节并更新 `generated.at`，保留旧上下文，日志动作用 `update`
   - 新主题 → 首次触及新领域时在 `wiki/` 动态创建对应分类目录（如 `wiki/01-Kotlin语言/`、`wiki/02-后端架构/`），按 §3 格式新建页面，slug 用中文文件名（与本库一致）
   - **发现矛盾必须显式标出**：`> ⚠️ 与 [[页面A]] 矛盾：A 说 X，本文说 Y，原因可能是…`。**严禁静默覆盖**
4. **更新 `wiki/索引.md`**：新页面入表，更新受影响页面的摘要与日期
5. **追加 `wiki/操作日志.md`**：格式 `[YYYY-MM-DD] ingest | 来源标题`（修改既有页记 `update | 来源标题`），列 `来源 / 页面影响 / 动作`
6. **报告**：更新 N 页，新建 M 页，列出文件名

单份来源通常触及 5–15 个页面。**不要跳过交叉引用**——链接密度是这个知识库的价值所在。

**摄入开发类资料时额外做**：识别出技术决策 → 考虑在 `wiki/` 对应分类落 ADR 决策记录；识别出项目相关 → 在 `wiki/` 建项目汇总页并链接。

### query — 查询知识库

1. 读 `wiki/索引.md`（唯一入口）
2. 挑 2–5 个最相关页面，读它们
3. 综合回答，**行内引用** `(→ [[页面名]])`
4. 追加 `wiki/操作日志.md`，记 `[YYYY-MM-DD] query | 问题摘要`
5. 结尾问：要不要存成新页面？**好答案该进知识库，不该烂在聊天记录里**

回答格式：用户没说就默认 markdown 表格或清单。

### lint — 体检

跑校验脚本（确定性，不靠 LLM 判断）：

```bash
# <skill_dir> 即本 skill 所在根目录
python <skill_dir>/scripts/okf_lint.py <bundle_root>
```

脚本检查：缺 `type`、frontmatter 不可解析、断链、孤儿页、过期内容、索引遗漏、type 拼写漂移、遗留 `timestamp`/`# Citations`（v0.1 字段）。

**先给优先级清单，再问用户改不改。批量修改一律先确认。**

优先级：
- P0 破损：frontmatter 不可解析、缺 `type`、断链
- P1 失真：索引遗漏、孤儿页、过期内容、type 漂移
- P2 优化：缺 description、缺 Related、sources 无 id

---

## 5. 与 Obsidian 协同

- **Obsidian 是 IDE，我是程序员，知识库是代码库**
- 改完直接落盘，用户在 Obsidian 里实时看到，不要写完再让用户手动复制
- `sources/09 资源/attachments/` 存手写笔记图片，用户在 设置 → 文件与链接 → 附件默认存放位置 指向它
- `sources/09 资源/templates/` 存笔记模板，用户在 设置 → 核心插件（或 Templater）→ 模板文件夹位置 指向它
- 社区插件已装：`dataview`（frontmatter 查询）、`obsidian-linter`（格式规范化）、`obsidian-git`（版本历史）、`karpathywiki`
- `obsidian-linter` 建议开启 YAML 标题、缩进、空行规范化，避免和手写格式打架
- **双链用 `[[文件名]]`**，不写路径（Obsidian 靠文件名解析，跨文件夹直接生效）
- frontmatter 里的 `type`/`tags` 可用 dataview 生成动态表格

---

## 6. Git

知识库是纯 markdown，版本历史免费。可选 `obsidian-git` 自动同步，或手动：

```bash
# vault 根 = bundle_root 的上一级（按 ~/.agent-wiki.json 的 wikiRoot 推导）
cd "<bundle_root 的父目录>"
git add -A && git commit -m "ingest: 来源标题"
```

**`sources/` 也要提交**（它是真相来源），但 ingest 提交信息要能追溯到 `操作日志.md` 的条目。

---

## 7. 铁律

1. **`sources/` 只读，`wiki/` 我维护**。用户在 `sources/` 自由手写，Agent 在 `wiki/` 编译。绝不原地篡改 `sources/`。
2. **矛盾显式标注，不静默覆盖**。两个来源打架比干净但错误的页面更有价值。
3. **索引先行**。每次查询从 `wiki/索引.md` 开始，每次摄入结束更新它。
4. **frontmatter 是硬要求**。缺 `type` 就是不合规。
5. **时间戳带时区**。
6. **actor 用约定前缀**，人写 `human:laoli`。
7. **不静默扩大范围**。发现该建新页面先说一声。
8. **批量改动先确认**。lint 只报告，动手前问。
9. **好答案要沉淀**。别让结论烂在对话里。
10. **改完立刻落盘**，并告诉用户改了哪些文件。

---

## 参考

- `references/知识库使用指南.md` — 内置的规范指南模板（初始化时复制生成到 `wiki/schema/`）
- `references/okf-spec-summary.md` — OKF v0.2 规范速查（字段全表、actor 约定、attested computation）
- `references/wiki-operations.md` — LLM-Wiki 四操作详解与页面模板
- 完整规范：`SPEC.md`（Google knowledge-catalog/okf，v0.2）
