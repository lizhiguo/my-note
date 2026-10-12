---
okf_version: "0.2"
---

# my-note

> 个人 Obsidian 知识库 bundle，OKF v0.2 + Karpathy LLM-Wiki 双规范。

## 目录

- `sources/` 不可变原始资料层（用户手写区，Agent 只读）
  - `sources/01 学习笔记/` — 学习笔记
  - `sources/02 技术/` — 技术笔记（后端 / 前端）
  - `sources/03 运维/` — 运维与部署
  - `sources/04 工具/` — 工具与平台
  - `sources/05 项目/` — 项目记录
  - `sources/06 随手记/` — 灵感与未分类碎片
  - `sources/09 资源/attachments/` — 图片与文件附件
  - `sources/09 资源/templates/` — 笔记模板
- `wiki/` 编译产物层（Agent 维护，用户只读）
  - `wiki/索引.md` — 总目录，每次查询/摄入的入口
  - `wiki/操作日志.md` — 操作流水，只追加
  - `wiki/schema/知识库使用指南.md` — 规范与使用说明
  - 分类子目录随内容摄入按需动态创建

## 保留文件

- `index.md` — 本文件，bundle 目录清单
- `log.md` — bundle 级更新履历