为你将随手记命令（`quick-note`）整合进现有的 `CodeBuddy-命令配置.md` 中。

整合后的文档统一归纳了两大核心命令（`extract-note` 深度复盘 + `quick-note` 随手碎片速记），并提供了批量一键软链/复制指引，你可以直接完整替换原文档内容：

---

```markdown
# CodeBuddy Commands 全局命令配置与迁移指南

> 用途：在业务工程中触发，让 Agent 自动分析代码或捕获碎片灵感，直接沉淀到本知识库的 `sources/` 原始笔记层。

---

## 包含命令概览

| 命令 | 用途 | 目标归档路径 |
| :--- | :--- | :--- |
| **`/extract-note`** | 深度提炼当前工程模块的架构、关键机制与代码切片（含架构图与对比表） | `sources/02-技术/前端/` 或 `后端/` |
| **`/quick-note`** | 极速捕获碎片灵感、临时踩坑排错日志或技术速记 | `sources/06-随手记/YYYY/YYYY-MM/` 两层时序目录 |

---

## 一、新设备还原指南（换电脑时配置步骤）

### 步骤 1：配置全局知识库路径
在用户家目录创建或修改 `~/.agent-wiki.json`（Windows 对应路径为 `C:\Users\<你的用户名>\.agent-wiki.json`）：

```json
{
  "wikiRoot": "D:/mywork/mydoc/obsidian-knowledge/my-note"
}

```

> **提示**：建议统一使用正斜杠 `/`，避免 Windows 路径反斜杠转义问题。

---

### 步骤 2：安装 Slash Commands

目标配置目录：`~/.codebuddy/commands/`

你可以选择 **方式 A（软链接，随笔记自动同步）** 或 **方式 B（直接复制，免管理员权限）**：

#### 方式 A：创建符号链接（推荐，改笔记即生效）

* **Windows 环境（PowerShell 管理员模式）**：
```powershell
# 确保目录存在
New-Item -ItemType Directory -Force -Path "$HOME\.codebuddy\commands"

# 1. 链接 extract-note 命令
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\extract-note.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\extract-note.md"

# 2. 链接 quick-note 随手记命令
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\quick-note.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\quick-note.md"

```


* **Windows CMD（管理员模式）**：
```cmd
mkdir "%USERPROFILE%\.codebuddy\commands" 2>nul
mklink "%USERPROFILE%\.codebuddy\commands\extract-note.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\extract-note.md"
mklink "%USERPROFILE%\.codebuddy\commands\quick-note.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\quick-note.md"

```


* **WSL / Linux / macOS 环境**：
```bash
mkdir -p ~/.codebuddy/commands
ln -sf "/path/to/wiki/schema/commands/extract-note.md" ~/.codebuddy/commands/extract-note.md
ln -sf "/path/to/wiki/schema/commands/quick-note.md" ~/.codebuddy/commands/quick-note.md

```



#### 方式 B：直接复制文件（无需管理员权限）

如果不想以管理员身份启动命令行，直接将知识库中的定义文件复制到该目录即可：

* 源文件 1：`wiki/schema/commands/extract-note.md`
* 源文件 2：`wiki/schema/commands/quick-note.md`
* 目标目录：`C:\Users\<你的用户名>\.codebuddy\commands\`

---

## 二、命令验证与日常使用

在任意代码工程中打开 CodeBuddy 会话即可触发：

### 1. 深度提炼工程设计 (`/extract-note`)

```text
/extract-note 登录鉴权与Token无感刷新

```

* **预期效果**：自动扫描工程相关代码，提炼架构全景图、时序图、边界防御表与踩坑经验，写入 `sources/02-技术/`。

### 2. 随手捕获灵感与排错 (`/quick-note`)

```text
/quick-note Nuxt4 中 useCookie 必须显式传 maxAge，否则在 SSR 模式下偶发不同步

```

* **预期效果**：自动计算当前日期，在 `sources/06-随手记/YYYY/YYYY-MM/` 创建两层目录并落盘文件（如 `2026-10-12-Nuxt4-useCookie踩坑.md`）。

---

## 三、知识库编译闭环 (Ingest)

无论是深度复盘还是随手记，当你在知识库中需要沉淀为通用词条时，只需在知识库 Agent 中触发：

```text
请对 sources/02-技术/前端/实战-xxx设计.md 执行 ingest
# 或
请对 sources/06-随手记/2026/2026-10/2026-10-12-xxx.md 执行 ingest

```

`okf-wiki` 技能会自动提取原子概念更新至 `wiki/` 并更新索引与操作日志。

```

```