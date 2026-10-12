# 审计图表指南 (Auditing Diagrams)

针对图表质量、覆盖率与代码同步状态进行全方位审计的综合实操手册。

## 审计分类

### 1. 质量审计 (Quality Audit)
检查图表是否符合 DDD 核心原则。

### 2. 覆盖率审计 (Coverage Audit)
排查哪些核心功能或用户流程尚未绘制图表。

### 3. 同步审计 (Synchronization Audit)
找出图表内容陈旧、未能跟上实际代码演进的图表。

### 4. 组织结构审计 (Organization Audit)
确保目录划分规范、文件命名合规以及总索引无死链。

## 质量审计标准流程

### 步骤 1：列出所有图表文件

```bash
# 列出所有图表文件（排除根目录 README.md）
find ai/diagrams -name "*.md" -not -name "README.md"

# 按图表类型统计数量
find ai/diagrams -name "feature-*.md" | wc -l
find ai/diagrams -name "sequence-*.md" | wc -l
find ai/diagrams -name "arch-*.md" | wc -l
```

### 步骤 2：依照 DDD 原则逐一核查

针对每一个图表文件，审查以下要点：

#### 结构完整性核查
- [ ] 顶部包含规范元数据（Type, Last Updated, Related Files）
- [ ] 包含 Purpose（目的）段落
- [ ] 包含 Mermaid 代码块
- [ ] 包含 Key Insights（核心洞察）段落
- [ ] 包含 Change History（变更历史）段落

#### DDD 合规性核查
- [ ] 展示了前台 (Front-Stage)（用户体验）
- [ ] 展示了后台 (Back-Stage)（技术实现）
- [ ] 用户作为起点入口或主要参与者
- [ ] 后台技术组件均附带了明确的影响标注
- [ ] 展示了异常分支与错误路径
- [ ] 包含了用户挽救恢复的操作选项
- [ ] 未使用任何自定义颜色（重构对比图使用 #90EE90 除外）

#### 内容质量核查
- [ ] Purpose 聚焦于用户价值，而非死板罗列技术实现
- [ ] 影响标注规范使用了对应符号（⚡💾🛡️✅⏱️🔄📊🎯）
- [ ] 影响标注准确解释了对用户的实际收益
- [ ] Key Insights 将底层技术与用户价值有效关联
- [ ] Mermaid 语法完全合法
- [ ] 图表结构可读性良好，未出现过度臃肿

#### 元数据准确性核查
- [ ] "Last Updated" 处于合理的时间范围内
- [ ] "Related Files" 所指的代码路径真实存在
- [ ] 文件被存放在正确的分类子目录中
- [ ] 文件命名严格符合命名规范

### 步骤 3：输出质量审计报告

```markdown
# 图表质量审计报告 (Diagram Quality Audit Report)

**审计日期:** YYYY-MM-DD
**图表总数:** X

## 质量概览

- ✅ **优秀 (Excellent)**（完全符合所有标准）: X 个
- ⚠️ **待改进 (Needs Improvement)**（存在次要问题）: X 个
- ❌ **质量不合格 (Poor Quality)**（存在重大缺陷）: X 个

## 发现的具体问题

### 高优先级 (严重影响对系统的理解)

1. **feature-checkout-flow.md**
   - ❌ 缺失异常错误分支
   - ❌ 缺少影响标注
   - 整改建议: 补齐错误处理逻辑并对组件添加用户收益标注

2. **sequence-auth-journey.md**
   - ❌ 未区分前台与后台
   - ❌ 缺少用户失败自愈选项
   - 整改建议: 使用子图划分前后台，增加恢复链路

### 中优先级 (降低了文档清晰度)

1. **arch-system-overview.md**
   - ⚠️ 影响标注过于偏向底层技术实现
   - ⚠️ 关联代码文件为空
   - 整改建议: 站在用户视角重写标注，补齐源码文件路径

2. **feature-search.md**
   - ⚠️ 单图过于庞杂臃肿（应做拆分）
   - 整改建议: 拆分为总览图与二级详情图

### 低优先级 (轻微优化项)

1. **flow-payment-processing.md**
   - ⚠️ Purpose 描述可进一步强化用户视角
   - ⚠️ Key Insights 总结不够充实
   - 整改建议: 重写 Purpose，扩充核心收益条目

## 整改建议

1. 排期专项修复高优先级严重问题
2. 为团队沉淀规范模版与自查清单
3. 接入 Git 提交前检查 (Pre-commit) 自动化脚本
4. 组织 DDD 核心理念与作图规范培训
```

## 覆盖率审计标准流程

### 步骤 1：排查系统核心模块与业务链路

```bash
# 扫描核心功能模块目录
find src/features -type d

# 扫描面向用户的关键页面视图
find src/components -name "*Page.tsx" -o -name "*View.tsx"

# 扫描 API 路由入口
find src/api -name "*.ts" -o -name "routes.ts"

# 扫描底层核心服务模块
find src/services -name "*.ts"
```

### 步骤 2：核实图表覆盖情况

针对每个核心功能：
- 检索关联图表：`grep -r "feature-name" ai/diagrams/`
- 核查 `ai/diagrams/README.md` 索引
- 确认现有图表是否真正覆盖了该功能的完整业务链

### 步骤 3：输出覆盖率审计报告

```markdown
# 图表覆盖率审计报告 (Diagram Coverage Audit Report)

**审计日期:** YYYY-MM-DD

## 已覆盖完备的功能清单 ✅

1. **用户身份认证 (User Authentication)**
   - sequence-authentication-journey.md
   - feature-login-flow.md

2. **电商下单结算 (E-commerce Checkout)**
   - feature-checkout-payment-flow.md
   - sequence-payment-processing.md

## 缺失图表的关键功能 ❌

1. **密码重置找回流程 (Password Reset Flow)**
   - 优先级: 高（安全敏感核心链路）
   - 涉及代码: `src/features/auth/PasswordReset.tsx`
   - 整改行动: 创建时序图

2. **实时通知推送系统 (Real-time Notifications)**
   - 优先级: 高（复杂用户交互流）
   - 涉及代码: `src/services/websocket/notificationService.ts`
   - 整改行动: 创建功能流程图

3. **搜索框输入实时联想补全 (Search Autocomplete)**
   - 优先级: 中（性能敏感体验）
   - 涉及代码: `src/features/search/SearchInput.tsx`
   - 整改行动: 创建功能流程图

4. **个人资料修改 (User Profile Editing)**
   - 优先级: 低（常规 CRUD 交互）
   - 涉及代码: `src/features/profile/ProfileEdit.tsx`
   - 整改行动: 评估是否有必要专门配图

## 覆盖不完整的功能

1. **结账流程 (Checkout Flow)** - 已有支付图，但缺失购物车校验与物流选择流程
2. **认证流程 (Authentication)** - 缺失 2FA 与第三方 OAuth 授权流程

## 推进建议

1. 优先为【高】优先级的缺失功能补全图表
2. 补全覆盖不完整模块的缺失分支
3. 重新评估【低】优先级功能是否真的需要制图
```

## 同步审计标准流程 (代码一致性)

### 步骤 1：检索近期变动的代码文件

```bash
# 收集过去 30 天内发生变更的文件列表
git log --since="30 days ago" --name-only --pretty=format: | sort | uniq > /tmp/recent-changes.txt

# 或者指定精确的时间窗口
git log --since="2025-01-01" --until="2025-01-31" --name-only --pretty=format: | sort | uniq
```

### 步骤 2：定位引用了变更代码的图表

```bash
# 逐一遍历变更文件，查找引用它的图表
while read file; do
  echo "Checking: $file"
  grep -l "$file" ai/diagrams/**/*.md
done < /tmp/recent-changes.txt
```

### 步骤 3：对比图表修改时间与代码修改时间

针对找到的每张图表：
- 读取图表中的“Last Updated”日期
- 使用 Git 查看关联代码文件的最后提交时间
- 若代码更新时间晚于图表更新时间 → 标记为【过时 (OUTDATED)】

```bash
# 获取关联文件的最后修改时间
git log -1 --format="%ai" -- path/to/file.ts

# 若代码变更时间晚于图表的 Last Updated，则说明图表已过时
```

### 步骤 4：人工核查是否影响业务逻辑

并非所有代码变动都需要更新图表。请重点研判：
- 用户交互流程是否发生变化？
- 异常错误处理机制是否调整？
- 是否引入了新特性？
- 性能指标是否有大幅变化？
- 影响标注是否依然准确客观？

### 步骤 5：输出同步审计报告

```markdown
# 图表同步审计报告 (Diagram Synchronization Audit Report)

**审计日期:** YYYY-MM-DD

## 状态完好同步的图表 ✅

1. **feature-checkout-payment-flow.md**
   - 图表最后更新: 2025-01-15
   - 关联代码最后变更: 2025-01-10
   - 状态: 最新 (UP TO DATE)

## 已明确过时的图表 ⚠️

1. **feature-user-authentication.md**
   - 图表最后更新: 2025-01-01
   - 关联代码最后变更: 2025-01-15（接入了 2FA）
   - 影响度: 缺失双因素认证全部分支
   - 整改行动: 在图中接入 2FA 流程

2. **sequence-search-journey.md**
   - 图表最后更新: 2024-12-20
   - 关联代码最后变更: 2025-01-10（引入了 Redis 缓存）
   - 影响度: 性能标注与数据流向失真
   - 整改行动: 增加缓存层并刷新响应耗时指标

3. **arch-system-overview.md**
   - 图表最后更新: 2024-11-15
   - 关联代码最后变更: 2025-01-05（完成了微服务拆分）
   - 影响度: 系统拓扑与实际运行架构严重脱节
   - 整改行动: 重新绘制微服务架构拓扑

## 疑似过时 (需人工深入核对) 🔍

1. **feature-notification-system.md**
   - 图表最后更新: 2025-01-05
   - 关联代码最后变更: 2025-01-12（内部小幅重构）
   - 整改行动: 审查改动是否对用户链路产生了影响

## 推进建议

1. 立即组织更新严重脱节的高影响图表
2. 人工核对疑似过时图表
3. 考虑配置自动化时效性检测钩子
4. 建立同步更新规范（代码发布 1 周内必须同步完成图表刷新）
```

## 组织结构审计流程

### 步骤 1：检查目录规划

```bash
# 检查目录完整性
ls -la ai/diagrams/

# 预期包含的目录结构：
# - features/
# - architecture/
# - journeys/
# - tests/
# - refactoring/
# - README.md
```

### 步骤 2：检查文件命名合规性

```bash
# 筛查命名不符合规范的文件
find ai/diagrams -name "*.md" -not -name "README.md" | while read file; do
  basename "$file" | grep -vE '^(feature|sequence|arch|flow|test)-[a-z0-9-]+\.md$' && echo "命名不合规: $file"
done

# 筛查存放目录错误的文件
find ai/diagrams/features -name "*.md" | while read file; do
  basename "$file" | grep -vE '^feature-' && echo "目录存放错误: $file"
done
```

### 步骤 3：检查总索引完整度与死链

对比磁盘实际文件与 `README.md` 中的链接：

```bash
# 整理磁盘中所有图表文件清单
find ai/diagrams -name "*.md" -not -name "README.md" | sort > /tmp/all-diagrams.txt

# 提取 README.md 中已收录的链接
grep -oP '\[.*?\]\(\K[^)]+' ai/diagrams/README.md | sort > /tmp/indexed-diagrams.txt

# 找出遗漏未收录至索引的图表
comm -23 /tmp/all-diagrams.txt /tmp/indexed-diagrams.txt
```

### 步骤 4：输出组织结构审计报告

```markdown
# 图表组织结构审计报告 (Diagram Organization Audit Report)

**审计日期:** YYYY-MM-DD

## 目录结构
- ✅ 所有核心子目录完备
- ⚠️ 发现非规范废弃目录: `ai/diagrams/old/`
  - 整改行动: 迁移有效文件并删除废弃目录

## 文件命名问题

1. ❌ `ai/diagrams/features/checkout.md`
   - 问题: 缺失类型前缀
   - 应修改为: `feature-checkout-flow.md`

2. ❌ `ai/diagrams/journeys/UserAuthenticationFlow.md`
   - 问题: 大小写不规范
   - 应修改为: `sequence-user-authentication-journey.md`

3. ❌ `ai/diagrams/arch-microservices.md`
   - 问题: 散落在根目录
   - 应移动至: `ai/diagrams/architecture/arch-microservices.md`

## 索引收录完整性

### 遗漏未登记至索引的图表
1. `features/feature-notification-system.md`
2. `refactoring/feature-add-caching-layer.md`

### 索引中存在的损坏死链
1. `[用户认证](journeys/auth-flow.md)` → 对应物理文件不存在

## 整改建议
1. 批量重命名违规文件
2. 移动散落文件至规范目录
3. 刷新 `README.md` 索引
4. 清理无效废弃目录
5. 修复死链
```

## 自动化审计脚本示例

```bash
#!/bin/bash
# audit-diagrams.sh

echo "=== 开始图表全面自动化审计 ==="
echo ""

# 1. 结构与语法质量核查
echo "## 质量合规检查"
echo ""
for file in ai/diagrams/**/*.md; do
  if [ "$file" = "ai/diagrams/README.md" ]; then continue; fi

  echo "正在检查文件: $file"

  # 必填段落检查
  grep -q "^## Purpose" "$file" || echo "  ❌ 缺少 Purpose 段落"
  grep -q "^## Diagram" "$file" || echo "  ❌ 缺少 Diagram 段落"
  grep -q "^## Key Insights" "$file" || echo "  ❌ 缺少 Key Insights 段落"
  grep -q "^## Change History" "$file" || echo "  ❌ 缺少 Change History 段落"

  # 前后台划分检查
  grep -q "Front-Stage" "$file" || echo "  ⚠️ 未标注 Front-Stage（前台）"
  grep -q "Back-Stage" "$file" || echo "  ⚠️ 未标注 Back-Stage（后台）"

  # 影响标注符号检查
  grep -q "[⚡💾🛡️✅⏱️🔄📊🎯]" "$file" || echo "  ⚠️ 未检测到标准影响标注符号"

  echo ""
done

# 2. 核心功能覆盖率核查
echo "## 功能覆盖检查"
echo ""
find src/features -type d -depth 1 | while read dir; do
  feature=$(basename "$dir")
  if ! grep -q "$feature" ai/diagrams/**/*.md; then
    echo "  ❌ 核心模块尚未建立图表: $feature"
  fi
done

# 3. 时效性同步核查
echo "## 时效性同步检查"
echo ""
find ai/diagrams -name "*.md" -not -name "README.md" | while read file; do
  date=$(grep -oP '^\*\*Last Updated:\*\* \K[0-9-]+' "$file")

  if [ -z "$date" ]; then
    echo "  ❌ $file: 未注明最后修改日期"
    continue
  fi

  # 检查是否超过 90 天未更新
  date_seconds=$(date -d "$date" +%s)
  now_seconds=$(date +%s)
  age_days=$(( ($now_seconds - $date_seconds) / 86400 ))

  if [ $age_days -gt 90 ]; then
    echo "  ⚠️ $file: 已有 $age_days 天未发生更新维护"
  fi
done

echo ""
echo "=== 自动化审计完成 ==="
```

## 审计最佳实践

1. **坚持周期性审计** - 活跃项目建议每月执行一次
2. **充分利用自动化** - 借助脚本快速筛查低级问题
3. **分层分批整改** - 优先修复影响业务理解的高危图表
4. **度量改进成效** - 跟踪长期质量健康度指标
5. **融入研发节奏** - 在迭代回顾会 (Sprint Review) 中定期回顾
6. **产出明确结论** - 每次审计形成可落实的改进行动项
7. **设立验收基线** - 明确团队图表质量的合格线
8. **持续改进演进** - 根据审计暴露的问题持续优化标准

## 建议审计频次

### 每周
- 快速同步检查（近期提交的代码是否已在图表中体现）
- 检查 README.md 索引是否出现断链

### 每月
- 开展完整的质量审计
- 审查新功能模块的图表覆盖度
- 检查文件组织与命名规范

### 每季度
- 对全体图表执行全面大检修
- 评估并修订 DDD 规范标准
- 复盘指标趋势与文档健康度

## 长期跟踪的关键指标

建议在项目中持续监控：
- 图表总量
- 符合 DDD 原则标准的图表占比 (%)
- 图表平均存续天数
- 核心功能图表覆盖率 (%)
- 从代码变更到图表同步更新的平均时延
- 损坏死链数量
- 命名不规范文件数量

指标看板示例：

```markdown
# 图表健康度看板 (Diagram Health Metrics)

**统计周期:** 2025年第一季度 (Q1 2025)

| 核心指标 | 当前数值 | 趋势表现 |
| :--- | :--- | :--- |
| 图表总数量 | 42 | +8 ↗️ |
| DDD 规范达标率 | 85% | +5% ↗️ |
| 图表平均存续天数 | 30 | -10 ↗️ |
| 核心功能覆盖率 | 78% | +12% ↗️ |
| 陈旧脱节图表数 | 3 | -2 ↗️ |
| 损坏死链数 | 0 | -1 ↗️ |

**综合健康度评估:** 🟢 优秀 (GOOD)
```

## 审计后的闭环步骤

1. 将审计发现整理为具体的**整改任务清单**
2. 依据影响度完成**优先级排序**
3. 为各项图表整改**明确负责人**
4. 为关键图表设定**整改截止时限**
5. 持续**跟踪整改进度**
6. 安排**复审验证**确保整改达标
7. 优化研发流程防范类似脱节问题重现
