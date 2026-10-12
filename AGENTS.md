# 知识库与 Agent 基础设施引导手册 (AGENTS.md)

欢迎进入本知识库仓库（MY-NOTE）。本仓库采用 **OKF v0.2 + Karpathy LLM-Wiki** 架构，同时作为**个人 Agent 基础设施（Commands / Skills / Agents）的单一真理源（Single Source of Truth）与孵化中心**。

---

## 1. 核心架构与职责分工

整个仓库严格分为两大主体域，执行任何操作时**严禁越界或混淆职责**：

### 1.1 知识数据域
1. **`sources/`（原始输入层 / 人类与项目直出区）**：
   - 包含业务工程复盘原稿（`02-技术/`）、碎片速记（`06-随手记/YYYY/YYYY-MM/`）等。
   - **规则**：人类或命令直接写入，**豁免严格的 OKF 元数据校验**。保留原始代码切片与实战上下文。
2. **`wiki/`（知识编译层 / AI 图谱网络）**：
   - 包含原子概念（Concept）、架构决策（ADR）与专题总览。
   - **规则**：由 Agent 通过 `ingest` 动作编译维护，**严格执行 OKF v0.2 契约**（必须含标准 Frontmatter、`sources` 溯源与 `[[WikiLinks]]`）。

### 1.2 Agent 基础设施域 (`wiki/schema/`)
本仓库所有可复用的 AI 工具资产集中在 `wiki/schema/` 下，会随业务需求不断迭代：
- **`wiki/schema/commands/`**：斜杠命令定义（如 `extract-note.md`、`quick-note.md`）。供各 IDE/终端环境挂载使用。
- **`wiki/schema/skills/`**：独立技能包（如 `okf-wiki/`、`diagram-driven/`）。每个技能包含独立的 `SKILL.md`，可自选携带 `scripts/` 或 `references/`。
- **`wiki/schema/agents/`**：专有子 Agent 角色设定与系统 Prompt（如架构评审 Agent、代码审计 Agent）。
- **`wiki/schema/guides/`**：全局渲染与规范协议（如 `PlantUML绘图风格指南.md`、`Mermaid绘图风格指南.md`）。

---

## 2. 工具资产迭代契约（严禁破坏）

当用户要求**创建、修改或优化** `commands`、`skills` 或 `agents` 时，必须遵守以下铁律：

### 2.1 Slash Command 迭代规范 (`wiki/schema/commands/*.md`)
- 必须保持纯净的 Command 定义格式，顶部必须包含标准的 Frontmatter（包含 `description`）。
- **严禁**在 Command 文件内写入多余的人类使用教程或安装说明（使用与还原指南一律记录在 `sources/04 工具/` 中）。
- 任何路径参数（如 `wikiRoot`）必须从 `~/.agent-wiki.json` 动态获取，并兼顾 Windows 正反斜杠与带空格路径的处理。

### 2.2 Skill 技能包迭代规范 (`wiki/schema/skills/<skill-name>/`)
- 每个技能必须有且仅有一个根描述文件 `SKILL.md`，顶部包含合法 Frontmatter（`name`、`description`、`allowed-tools`）。
- **动静分离原则**：长篇理论和风格约定尽量抽离至 `wiki/schema/guides/` 或 `references/`，`SKILL.md` 主体必须精炼，聚焦于**输入前置条件校验、流程编排管道与质量验收清单**。
- 若技能包含可执行脚本（如 Python 校验器），必须放置在 `scripts/` 目录下。

### 2.3 变更同步与记录
- 无论修改了 `wiki/` 里的知识，还是重构了 `schema/` 里的技能/命令：
  - 必须检查是否影响到 `wiki/schema/知识库使用指南.md`，若有变动需同步修正。
  - 必须在 `wiki/操作日志.md` 中追加一条审计记录（格式：`[YYYY-MM-DD] tool-update | <工具名> | <变动描述>`）。

---

## 3. 常见任务执行流 (Playbooks)

### 场景 A：知识摄入与编译 (`ingest`)
1. 完整阅读用户指定的 `sources/...` 文件；
2. 规划拟提炼的原子概念或拟更新的页面，**先向用户汇报提取清单与影响面**；
3. 用户确认后落盘，补齐标准 OKF Frontmatter，编织 `[[双链]]`；
4. 刷新 `wiki/索引.md`，并在 `wiki/操作日志.md` 追加记录。

### 场景 B：新建或重构一个 Skill / Command
1. 确认该工具的定位：是轻量即席命令（放入 `commands/`）还是多步骤系统工具（放入 `skills/`）；
2. 遵循第 2 节的迭代契约输出代码与配置；
3. 如果工具引入了新的软链或安装步骤，同步更新 `sources/04 工具/` 下的备忘指引；
4. 提示用户重新软链或重新加载该技能进行验证。

### 场景 C：技术问答与知识检索
1. 优先检索 `wiki/索引.md` 与相关概念词条，基于本库沉淀的规约回答；
2. 作答时明确标注信息出自哪个 `wiki/` 词条或哪份原始实战复盘。