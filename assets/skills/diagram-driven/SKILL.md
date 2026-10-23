---
name: diagram-driven
description: "图驱动开发 (DDD) 技能：根据用户价值与技术实现维护统一影响图。支持生成、更新、审计和组织 ai/diagrams 目录下的架构图、时序图、泳道图与 ER 图。"
allowed-tools: Bash, Glob, Read, Write, Edit
---

# 图驱动开发技能 (Diagram Driven Development)

本技能将代码项目的 `ai/diagrams/` 维护为系统理解的唯一可信源。所有图表严格遵循 DDD 原则：连接前台（用户体验）与后台（技术实现），并带有明确的用户价值影响标注。

---

## 0. 规范加载（Pre-condition）

在生成、修改或审计任何图表前，**必须先解析规范源**：
1. 检查当前环境或 `~/.agent-wiki.json` 获取 `wikiRoot`（如 `D:/mywork/mydoc/obsidian-knowledge/king的知识库/我的知识库`）。
2. 根据当前任务类型，定向读取知识库中的最新规约（若无法访问全局知识库，则回退使用内置简要原则）：
   - **DDD 核心方法论**：`{wikiRoot}/wiki/02-后端架构/图驱动开发DDD原则.md`
   - **Mermaid 语法与模式**：`{wikiRoot}/wiki/schema/guides/Mermaid绘图风格指南.md`
   - **PlantUML 泳道与 ER 图规范**：`{wikiRoot}/wiki/schema/guides/PlantUML绘图风格指南.md`

---

## 1. 核心图表刚性原则速查

- ✅ **双舞台视角**：必须同时呈现 **前台 (Front-Stage)**（用户体验/操作）与 **后台 (Back-Stage)**（技术实现）。
- ✅ **影响标注**：所有后台组件必须标注用户收益符号（⚡性能、💾存储、🛡️安全、✅校验、⏱️流畅度、🔄容错恢复、📊准确性、🎯功能使能）。
- ✅ **完备分支**：必须包含带恢复自愈选项的**错误路径**，严禁只画正常路径。
- ✅ **动静选型契约**：
  - **静态架构/模块归属** $\to$ 选用 **Mermaid Subgraph**。
  - **跨部门/跨服务动态时序流转** $\to$ 必须首选 **PlantUML 泳道图**（时间线自上而下，严禁在 Mermaid 子图间交叉连线打结）。
  - **数据表结构/外键约束** $\to$ 必须选用 **PlantUML ER 图**。
- ❌ **配色禁忌**：严禁随意使用自定义填充色（除重构对比图中变更部分使用 `#90EE90` 高亮外，一律使用原生默认样式）。

---

## 2. 操作工作流

### 2.1 创建图表 (Create)
1. **明确价值**：回答“该图表解决了什么用户痛点？交付了什么收益？”
2. **选择载体与文件命名**（小写，连字符）：
   - 功能流程：`features/feature-{name}.md`
   - 用户时序/旅程：`journeys/sequence-{name}.md`
   - 跨部门业务泳道：`journeys/lane-{name}.md` 或 `features/lane-{name}.md` (PlantUML)
   - 系统架构拓扑：`architecture/arch-{name}.md`
   - 数据实体模型：`architecture/er-{name}.md` (PlantUML)
   - 测试场景覆盖：`tests/test-{name}.md`
   - 重构前后对比：`refactoring/feature-{name}.md` (含 Before/After)
3. **写入标准模板**：
   ```markdown
   # [清晰聚焦用户价值的标题]

   **Type:** [Feature | Sequence | Architecture | Swimlane | ER | Test]
   **Last Updated:** YYYY-MM-DD
   **Related Files:**
   - `path/to/code.ts`

   ## Purpose
   [1-2句话阐述用户价值，关注用户收益而非纯技术]

   ## Diagram
   ```mermaid (或 plantuml)
   [遵循规范的图表代码]
   ```

   ## Key Insights
   - **用户体验收益**: ...
   - **底层技术支撑**: ...

   ## Change History
   - **YYYY-MM-DD:** 初始创建
   ```
4. **刷新索引**：将新图表追加至 `ai/diagrams/README.md`。

### 2.2 更新图表 (Update)
1. 识别代码变更对用户流向、异常处理或性能指标产生的影响。
2. 同步调整图表代码、更新组件影响标注（如性能数据更新）。
3. 校验并更新 `Related Files` 关联文件路径与 `Last Updated` 日期。
4. 在 `Change History` 追加本次更新的条目。

### 2.3 审计图表 (Audit)
1. **质量检查**：核对图表是否包含前后台、影响标注、错误自愈出口。
2. **时效检查**：对比 Git 提交历史，识别代码变动晚于图表 `Last Updated` 的陈旧图表。
3. **覆盖率检查**：扫描 `src/` 核心功能，排查缺失图表保护的业务链路。
4. **输出清单**：分为高优先级（缺失错误路径/脱离用户）、中优先级（标注不准确）、低优先级（格式微调）。

### 2.4 组织管理 (Organize)
1. 确保目录分类规范，杜绝散落在根目录的裸图表。
2. 检查并修复 `ai/diagrams/README.md` 总索引中的死链。
