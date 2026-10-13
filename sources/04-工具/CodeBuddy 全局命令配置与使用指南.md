# CodeBuddy Commands 全局命令配置与使用指南

> 用途：在各业务工程与日常开发中触发，将代码片段、理论抽象、可复现实战 Runbook 以及碎片灵感无缝沉淀到全局知识库的 `sources/` 原始笔记层。

## 包含命令体系总览 (6 大核心命令)

| **命令** | **定位与用途** | **目标归档路径** | 
| **`/study-note`** | **理论与抽象模型**：剥离业务特化噪点，提炼设计模式、设计哲学与通用架构模型 | \`sources/01-学习笔记/前端 | 
| **`/tech-note`** | **工程实战手册 (Runbook)**：提炼依赖版本、配置初始化、调用示例、测试与避坑经验 | \`sources/02-技术/前端 | 
| **`/java-snippet`** | **Java 常用工具与代码库**：提炼现代 Java (17/21) 工具类、泛型规范及 JUnit 5 + AssertJ 测试 | `sources/02-技术/后端/Java高频实用工具与核心代码集.md` | 
| **`/kotlin-snippet`** | **Kotlin 扩展与惯用代码库**：提炼高阶扩展函数、`inline` 优化、空安全及 JUnit 5 测试 | `sources/02-技术/后端/Kotlin高频扩展与工具集.md` | 
| **`/ts-snippet`** | **TypeScript 工具与类型体操**：提炼类型守卫、泛型推导、纯函数及 Vitest 单元测试 | `sources/02-技术/前端/TypeScript高频工具与类型体操.md` | 
| **`/quick-note`** | **极速碎片捕获**：临时踩坑排错日志、零碎灵感或快速技术备忘 | `sources/06-随手记/YYYY/YYYY-MM/` 两层时序目录 | 

## 一、新设备还原指南（换电脑时配置步骤）

### 步骤 1：配置全局知识库基准路径

在当前系统的用户家目录下创建或修改 `~/.agent-wiki.json`（Windows 对应 `C:\Users\<你的用户名>\.agent-wiki.json`）：

```
{
  "wikiRoot": "D:/mywork/mydoc/obsidian-knowledge/my-note"
}

```

> **提示**：建议统一使用正斜杠 `/`，避免 Windows 反斜杠转义与路径混淆。

### 步骤 2：安装 Slash Commands

目标配置目录：`~/.codebuddy/commands/`（Windows 为 `C:\Users\<你的用户名>\.codebuddy\commands\`）

选择以下 **方式 A（软链接，笔记修改即时联动）** 或 **方式 B（免提权直接复制）**：

#### 方式 A：创建符号链接（推荐）

> **Windows 权限说明**：若未开启开发人员模式，请以**管理员身份运行 PowerShell** 执行；若已开启开发人员模式（设置 $\to$ 系统 $\to$ 针对开发人员 $\to$ 开启开发人员模式），普通 PowerShell 窗口即可直接运行。

* **Windows PowerShell**：

```
# 1. 确保目标目录存在
New-Item -ItemType Directory -Force -Path "$HOME\.codebuddy\commands"

# 2. 依次创建 6 大命令符号链接
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\study-note.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\study-note.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\tech-note.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\tech-note.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\java-snippet.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\java-snippet.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\kotlin-snippet.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\kotlin-snippet.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\ts-snippet.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\ts-snippet.md"
New-Item -ItemType SymbolicLink -Path "$HOME\.codebuddy\commands\quick-note.md" -Target "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\quick-note.md"

```

* **Windows CMD（管理员模式）**：

```
mkdir "%USERPROFILE%\.codebuddy\commands" 2>nul
mklink "%USERPROFILE%\.codebuddy\commands\study-note.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\study-note.md"
mklink "%USERPROFILE%\.codebuddy\commands\tech-note.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\tech-note.md"
mklink "%USERPROFILE%\.codebuddy\commands\java-snippet.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\java-snippet.md"
mklink "%USERPROFILE%\.codebuddy\commands\kotlin-snippet.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\kotlin-snippet.md"
mklink "%USERPROFILE%\.codebuddy\commands\ts-snippet.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\ts-snippet.md"
mklink "%USERPROFILE%\.codebuddy\commands\quick-note.md" "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\quick-note.md"

```

* **WSL / Linux / macOS**：

```
mkdir -p ~/.codebuddy/commands
SRC="/path/to/my-note/wiki/schema/commands"
ln -sf "$SRC/study-note.md" ~/.codebuddy/commands/study-note.md
ln -sf "$SRC/tech-note.md" ~/.codebuddy/commands/tech-note.md
ln -sf "$SRC/java-snippet.md" ~/.codebuddy/commands/java-snippet.md
ln -sf "$SRC/kotlin-snippet.md" ~/.codebuddy/commands/kotlin-snippet.md
ln -sf "$SRC/ts-snippet.md" ~/.codebuddy/commands/ts-snippet.md
ln -sf "$SRC/quick-note.md" ~/.codebuddy/commands/quick-note.md

```

#### 方式 B：批量复制文件（免管理员权限、跨分区通用）

在普通 PowerShell 执行单行命令拷贝全部定义文件：

```
New-Item -ItemType Directory -Force -Path "$HOME\.codebuddy\commands"
Copy-Item "D:\mywork\mydoc\obsidian-knowledge\my-note\wiki\schema\commands\*.md" "$HOME\.codebuddy\commands\" -Force

```

## 二、命令实战使用场景与验证

在任意工程打开 CodeBuddy 会话即可按需调用：

### 1. 理论与抽象架构提炼 (`/study-note`)

> **用途**：剥离业务噪点，沉淀设计模型与契约（支持前端、后端、通用架构及第三方库）。

```
/study-note 接口契约-统一响应信封模型设计
/study-note Arrow-Kotlin函数式体系

```

* **效果**：自动提炼设计哲学、抽象 Mermaid 图、泛型接口骨架与适用边界，落盘至 `sources/01-学习笔记/` 对应子目录。

### 2. 工程实战手册提炼 (`/tech-note`)

> **用途**：提炼具备生产可复现性的实战 Runbook（严禁将本地 Mock 参数当通用契约）。

```
/tech-note 登录鉴权与Token无感刷新

```

* **效果**：扫描当前代码，提炼依赖清单、配置项、核心拦截器代码、业务调用示例、时序图与踩坑经验，落盘至 `sources/02-技术/`。

### 3. 主力语言代码片段沉淀 (`/java-snippet` / `/kotlin-snippet` / `/ts-snippet`)

> **用途**：即拷即用，沉淀带测试用例的代码军火库。

* **Kotlin 片段**：

  ```
  /kotlin-snippet
  fun <R> String.notBlank(block: String.() -> R): R? {
      if (this.isNotBlank()) return block()
      return null
  }
  
  ```

* **Java 片段**：

  ```
  /java-snippet
  public static <T> List<T> safeList(List<T> list) {
      return list == null ? Collections.emptyList() : Collections.unmodifiableList(list);
  }
  
  ```

* **TypeScript 片段**：

  ```
  /ts-snippet
  export const isNonNullable = <T>(value: T): value is NonNullable<T> => value !== null && value !== undefined;
  
  ```

* **效果**：AI 自动进行工程加固（`inline`、防御性校验、强类型推导），补齐 Before/After 对比与单元测试（JUnit 5 / Vitest），自动作为二级标题追加至对应的代码集锦文件中。

### 4. 极速捕获与临时排错 (`/quick-note`)

> **用途**：零心智负担记录单条闪念或踩坑排错。

```
/quick-note Nuxt4 中 useCookie 必须显式传 maxAge，否则在 SSR 模式下偶发不同步

```

* **效果**：自动按当前日期创建两层目录，落盘如 `sources/06-随手记/2026/2026-10/2026-10-12-Nuxt4-useCookie踩坑.md`。

## 三、知识库编译闭环 (Ingest)

当你在业务工程沉淀的原稿需要上升为跨项目图谱与原子词条时，切回知识库根目录对 Agent 发起指令：

```
请对 sources/02-技术/前端/实战-优秀登录架构设计.md 执行 ingest
# 或
请对 sources/01-学习笔记/后端/接口契约-统一响应信封模型设计模型.md 执行 ingest

```

**执行流程**：

1. Agent（依托 `okf-wiki` 技能）解析原稿，拆解或更新 `wiki/` 目录下的原子概念；

2. 自动生成 OKF v0.2 标准元数据，编织 `[[双链]]`；

3. 同步更新 `wiki/索引.md`，并在 `wiki/操作日志.md` 追加流水记录。