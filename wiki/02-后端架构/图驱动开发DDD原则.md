---
type: Concept
title: 图驱动开发DDD原则
description: 连接用户价值与技术实现的核心图表构建方法论，通过双舞台视角与影响标注保障架构图的业务对齐。
tags: [架构设计, DDD, 图表驱动开发, 规范]
status: stable
sources:
  - id: diagram-principles
    resource: wiki/schema/skills/diagram-driven/SKILL.md
    last_modified: 2026-10-12T16:30:00+08:00
generated: { by: human:king, at: 2026-10-12T16:35:00+08:00 }
---

# 图驱动开发（DDD）原则 (Diagram Driven Development Principles)

> 连接用户价值与技术实现的核心图表构建方法论。

---

## 概述

**传统图表说明代码“做了什么”。DDD 图表说明代码“为什么对用户重要”。**[^diagram-principles]

[^diagram-principles]: 提炼自 `diagram-driven` 技能原始规约沉淀。

每个图表都必须回答以下四个核心问题：
1. **这解决了什么用户需求？**
2. **底层技术实现如何交付这一价值？**
3. **当发生异常时会发生什么？**
4. **我们在哪里可以改善用户体验？**

---

## 两大核心舞台 (The Two Stages)

### 1. 前台 (Front-Stage，用户体验)
用户看到、感知和体验到的内容：
- 用户的操作与决策
- UI 状态与即时反馈
- 等待时间与延迟
- 错误提示与恢复选项
- 成功确认提示

### 2. 后台 (Back-Stage，技术实现)
技术底层如何支撑并交付这种体验：
- 服务与 API 接口
- 数据计算与处理
- 缓存机制与性能优化
- 异常错误处理
- 系统集成对接点

**关键要求**：每一个图表都必须同时展示这两个舞台，并清晰展现它们之间的连接。

---

## 影响标注规范 (Impact Annotations)

每个技术组件都必须附带一条标注，解释其对用户的价值影响。

### 标注符号规范
- `⚡` 速度 / 性能影响 (Speed/Performance)
- `💾` 存储 / 缓存收益 (Storage/Caching)
- `🛡️` 安全 / 稳定保障 (Security/Safety)
- `✅` 校验 / 正确性 (Validation/Correctness)
- `⏱️` 响应度 / 流畅体验 (Responsiveness/UX smoothness)
- `🔄` 可靠性 / 容灾恢复 (Reliability/Recovery)
- `📊` 数据准确性 / 完整性 (Data accuracy/integrity)
- `🎯` 功能使能 / 核心支持 (Feature enablement)

### 标注正反对比
- **正例**：`API Call [⚡ 耗时 <100ms 实现即时检索]`、`Caching Layer [💾 降低 80% 加载等待]`、`Validation [✅ 拦截错误输入避免无效提交]`
- **反例（脱离用户体验的纯技术实现）**：`API Call [REST endpoint using JWT]`、`Caching Layer [Redis with 1hr TTL]`

---

## 完备错误路径要求 (Error Path Requirements)

每个图表都必须展示：
1. **成功主路径 (Happy path)**：流程正常运行的链路；
2. **错误分支路径 (Error paths)**：发生失败时的流向；
3. **恢复选项 (Recovery options)**：用户如何进行补救与重试；
4. **降级兜底行为 (Fallback behavior)**：系统的优雅降级保障。

---

## 选型与设计契约

- **静态架构/模块归属**：选用 Mermaid Subgraph。
- **跨部门/跨系统动态时序流转**：必须选用 PlantUML 泳道图（时间线自上而下推进，严禁 Mermaid 跨子图反复交叉打结）。
- **数据实体与表结构关系**：选用 PlantUML ER 图。
- **配色约束**：保持原生默认配色，除重构对比图中改动点使用 `#90EE90` 高亮外，严禁随意使用彩虹色或自定义背景。

---

## 质量验证清单

- [ ] 前台与后台双舞台视角完整
- [ ] 包含明确的错误分支与用户自愈出口
- [ ] 所有后台组件附带标准化用户价值影响标注
- [ ] 流程以用户为起点和终点

---

## 相关

- [[索引]] — 全局知识库索引
- [[Mermaid绘图风格指南]] — Mermaid 语法模式与最佳实践
- [[PlantUML绘图风格指南]] — PlantUML 泳道与 ER 图规约
