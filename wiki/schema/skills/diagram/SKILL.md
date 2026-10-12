---
name: diagram
description: 遵循图驱动开发（DDD）方法论维护并同步统一影响图。创建、更新和管理连接用户价值与技术实现的图表。
allowed-tools: Bash, Glob, Read, Write, Edit
---

# 图驱动开发（DDD）技能 (Diagram Driven Development Skill)

将 `ai/diagrams` 目录维护为系统理解的唯一可信源。所有图表均遵循 DDD 原则，将前台（用户体验）与后台（技术实现）连接起来，并带有明确的影响标注。

## 技能能力

1. **创建图表 (Create Diagrams)** - 为功能、架构、用户旅程、测试和重构生成新图表
2. **更新图表 (Update Diagrams)** - 同步现有图表以反映代码变更
3. **审计图表 (Audit Diagrams)** - 识别过时、缺失或低质量的图表
4. **组织图表 (Organize Diagrams)** - 维护一致的目录结构和命名规范
5. **索引管理 (Index Management)** - 保持 README.md 图表总索引持续更新
6. **质量验证 (Quality Validation)** - 确保所有图表均符合 DDD 原则

## 快速参考

各类操作的详细说明请参考：
- [CREATE.md](references/CREATE.md) - 创建新图表
- [UPDATE.md](references/UPDATE.md) - 更新现有图表
- [AUDIT.md](references/AUDIT.md) - 审计图表质量与覆盖率
- [ORGANIZE.md](references/ORGANIZE.md) - 目录结构与命名规范
- [DDD_PRINCIPLES.md](references/DDD_PRINCIPLES.md) - 图驱动开发方法论
- [MERMAID_GUIDE.md](references/MERMAID_GUIDE.md) - Mermaid 语法模式
- [PLANTUML_GUIDE.md](references/PLANTUML_GUIDE.md) - PlantUML 泳道图与 ER 图模式

## 目录结构

```
ai/diagrams/
├── README.md                    # 所有图表的总索引
├── features/                    # 具体功能图表
├── architecture/                # 系统架构图表
├── journeys/                    # 用户旅程图表
├── tests/                       # 测试覆盖图表
└── refactoring/                 # 重构前后对比图表
```

## 常见工作流

### 初始设置工作流
1. 用户启动新项目，或在现有项目中引入 DDD
2. 创建 `ai/diagrams/` 目录结构
3. 生成初始系统架构图
4. 创建 README.md 索引文件
5. 记录核心用户旅程

### 新功能工作流
1. 用户提出新功能需求
2. 创建展示用户价值的功能图表
3. 连接前台（UX/用户体验）与后台（技术实现）
4. 记录相关的文件和组件
5. 更新 README.md 索引

### 代码变更工作流
1. 代码发生修改（新功能、重构等）
2. 识别受影响的图表
3. 更新图表以反映变更
4. 更新“最后更新 (Last Updated)”日期
5. 追加变更历史记录条目

### 审计工作流
1. 用户请求审计图表
2. 扫描 `ai/diagrams/` 中的所有图表
3. 检查过时的图表（对比 Git 提交历史与图表日期）
4. 识别缺失的图表（缺少图表的功能）
5. 验证 DDD 质量（前台/后台、影响标注）
6. 汇报审计结果与改进建议

### 重构文档工作流
1. 用户计划进行代码重构
2. 创建展示当前状态的“重构前 (Before)”图表
3. 创建展示改进状态的“重构后 (After)”图表（改动部分用 `#90EE90` 高亮显示）
4. 添加解释用户收益的影响标注
5. 存放至 `refactoring/` 目录下

## 关键指令

**必须遵守**：在执行任何图表操作之前，你必须使用 Read 工具加载相关的参考文件。这些参考文件中包含了核心 DDD 原则、质量标准和操作规程，未全部包含于本概览中。

当用户要求处理图表时：

1. **识别操作类型**（创建、更新、审计、组织）
2. **强制要求：在执行任何操作之前，先使用 Read 工具加载相关参考文件**：
   - 创建图表 → 先阅读 `references/CREATE.md` 与 `references/DDD_PRINCIPLES.md`
   - 更新图表 → 先阅读 `references/UPDATE.md` 与 `references/DDD_PRINCIPLES.md`
   - 审计图表 → 先阅读 `references/AUDIT.md`
   - 组织/重构目录 → 先阅读 `references/ORGANIZE.md`
   - 理解 DDD 理念 → 先阅读 `references/DDD_PRINCIPLES.md`
   - Mermaid 语法求助 → 先阅读 `references/MERMAID_GUIDE.md`
   - PlantUML 语法求助 → 先阅读 `references/PLANTUML_GUIDE.md`
3. **执行图表操作**，严格遵循参考文件中的模式与质量标准
4. **验证质量**，核对 DDD 原则检查清单
5. **更新索引**，在 README.md 中体现变更
6. **确认操作**，尽可能展示图表预览

**切勿在未阅读相关参考文档（尤其是 DDD_PRINCIPLES.md）的情况下尝试创建或修改图表。**

## DDD 核心原则（简述）

每个图表必须包含：
- ✅ **前台 (Front-Stage)**（用户体验）与 **后台 (Back-Stage)**（技术实现）
- ✅ **影响标注 (Impact Annotations)**，解释技术组件对用户的价值
- ✅ **用户操作** 作为入口点与退出点
- ✅ **错误路径** 与恢复选项
- ✅ **关联文件** 文档记录
- ❌ 禁止使用自定义填充颜色（重构前/后差异使用 `#90EE90` 的情况除外）
- ❌ 禁止脱离用户上下文绘制纯技术图表

## 命名规范

### 文件命名
- 全部使用小写字母，用连字符（-）分隔
- 包含图表类型前缀
- 格式：`{type}-{descriptive-name}.md`

**示例：**
- `feature-user-checkout-flow.md`
- `sequence-authentication-journey.md`
- `arch-system-overview.md`
- `lane-refund-cross-department-flow.md`
- `er-trade-core-entities.md`
- `flow-payment-processing.md`

### 类型前缀
- `feature-` - 功能特异性图表
- `sequence-` - 时序/旅程图表
- `arch-` - 架构图表
- `flow-` - 流程/过程图表
- `lane-` - 跨部门业务泳道图 (PlantUML)
- `er-` - 数据库实体关系图 (PlantUML)
- `test-` - 测试覆盖图表

## 图表文件结构

```markdown
# [图表标题]

**Type:** [Feature Diagram | Sequence Diagram | Architecture Diagram | etc.]
**Last Updated:** [YYYY-MM-DD]
**Related Files:**
- `path/to/implementation.ts`
- `path/to/component.tsx`

## Purpose

[用 1-2 句话说明此图表阐述了什么用户价值]

## Diagram

\`\`\`mermaid
[遵循 DDD 原则的 Mermaid 图表代码]
\`\`\`

## Key Insights

- [用户影响点 1]
- [用户影响点 2]
- [技术支撑点 1]

## Change History

- **YYYY-MM-DD:** [变更描述]
```

## 质量检查清单

在存储任何图表之前，请核对：
- [ ] 同时展示了前台 (Front-Stage)（用户体验）和后台 (Back-Stage)（技术实现）
- [ ] 影响标注清晰解释了用户价值
- [ ] 用户操作清晰可见
- [ ] 展示了错误路径
- [ ] 未使用自定义填充颜色（变更标注使用 #90EE90 除外）
- [ ] 记录了关联的代码文件
- [ ] “最后更新”日期为当前最新日期
- [ ] 核心洞察解释了用户影响
- [ ] Mermaid 或 PlantUML 语法合法无误

## 最佳实践

1. **保持图表同步** - 过时的图表比没有图表更糟糕
2. **遵循 DDD 原则** - 每个图表都将用户价值与实现相连
3. **使用子目录** - 按类型归类存放，防止混乱
4. **维护总索引** - README.md 是系统理解的入口
5. **记录变更历史** - 修改时务必更新变更记录
6. **验证图表质量** - 保存前核对 DDD 检查清单
7. **关联代码文件** - 将图表链接至具体实现代码
8. **呈现错误路径** - 不要只画成功路径
9. **保持命名一致** - 可预期的命名规范便于导航
10. **改动代码后及时更新** - 图表必须反映当前真实状态
11. **动态流转优先泳道** - 跨组件、跨部门或跨服务的动态流转，优先使用 PlantUML 泳道图，严禁在 Mermaid subgraph 间反复交叉连线

## 与其他技能的集成

- **review** - 在代码审查中引用图表以解释改动影响
- **github** - 在 Issue 描述中链接图表以补充上下文背景
- **chrome-devtools** - 依据图表规划端到端测试流程

## 示例

### 创建功能图
```
User: "Create a diagram for the new notification system"
Agent:
1. Reads references/CREATE.md and references/DDD_PRINCIPLES.md
2. Analyzes notification feature code
3. Creates feature-notification-system.md in features/
4. Includes user journey and technical implementation
5. Adds impact annotations
6. Updates README.md index
```

### 重构后更新
```
User: "We just refactored the auth flow, update the diagram"
Agent:
1. Reads references/UPDATE.md
2. Finds sequence-authentication-journey.md
3. Compares with new code
4. Updates diagram with changes
5. Updates "Last Updated" date
6. Adds change history entry
```

### 审计所有图表
```
User: "Audit our diagrams"
Agent:
1. Reads references/AUDIT.md and references/DDD_PRINCIPLES.md
2. Scans ai/diagrams/ directory
3. Checks each diagram against DDD checklist
4. Compares diagram dates with git history
5. Identifies missing diagrams
6. Reports findings with recommendations
```

## 核心刚性规则

1. **图表必须与代码保持严格同步** - 持续比对 Git 历史与图表日期
2. **每个图表必须遵循 DDD 原则** - 严禁纯技术图表
3. **组织结构至关重要** - 始终规范使用各子目录
4. **总索引必须持续维护** - README.md 必须反映所有图表现状
5. **文件命名必须保持一致** - 遵循“类型-名称”模式
6. **质量优于数量** - 宁可拥有 5 个优质图表，也不要 20 个劣质图表
7. **用户价值高于一切** - 每个技术细节都必须连接到用户影响
8. **始终优先加载参考文档** - DDD 原则不可协商

## 研发流程集成

本技能深度融入软件研发工作流：

1. **修改代码前** - 查阅现有图表以理解系统逻辑
2. **方案规划期** - 绘制提案图表展示计划中的改动
3. **编码实现期** - 参考图表以保持设计一致性
4. **实现完成后** - 同步更新图表以反映最新实现
5. **审查评估期** - 借助图表解释改动影响与上下文
6. **新人入职期** - 图表充当新团队成员的系统指引文档
