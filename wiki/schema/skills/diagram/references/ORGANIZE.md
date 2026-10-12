# 组织图表指南 (Organizing Diagrams)

维护整洁规范的目录层级与标准化命名风格的实操指南。

## 目录结构体系

```
ai/diagrams/
├── README.md                    # 所有图表的总索引（必须维护）
├── features/                    # 针对具体功能的用户流程
│   ├── feature-checkout-payment-flow.md
│   ├── feature-notification-system.md
│   └── feature-search-functionality.md
├── architecture/                # 系统级架构拓扑
│   ├── arch-system-overview.md
│   ├── arch-microservices-architecture.md
│   └── arch-data-flow.md
├── journeys/                    # 用户端到端旅程时序
│   ├── sequence-authentication-journey.md
│   ├── sequence-onboarding-flow.md
│   └── sequence-purchase-completion.md
├── tests/                       # 测试策略与场景覆盖
│   ├── test-payment-security-coverage.md
│   └── test-e2e-critical-paths.md
└── refactoring/                 # 重构前后对比改进
    ├── feature-add-caching-layer.md
    └── feature-optimize-database-queries.md
```

## 文件命名规范

### 标准格式：`{type}-{descriptive-name}.md`

**类型前缀映射：**
- `feature-` → 对应 `features/`
- `sequence-` → 对应 `journeys/`
- `arch-` → 对应 `architecture/`
- `flow-` → 对应 `features/` 或 `journeys/`（根据实际上下文而定）
- `lane-` → 对应 `journeys/` 或 `features/`（跨部门业务泳道图，推荐 PlantUML）
- `er-` → 对应 `architecture/`（数据库实体关系图，推荐 PlantUML）
- `test-` → 对应 `tests/`

**描述性名称规则：**
- 全部字母使用小写
- 词与词之间使用中划线连字符（禁止使用下划线或空格）
- 意图明确，具体清晰
- 长度以 2-5 个单词为佳
- 直接体现用户价值或核心流程

### 良好命名示例

```
✅ feature-checkout-payment-flow.md
✅ sequence-user-authentication-journey.md
✅ arch-microservices-overview.md
✅ lane-refund-cross-department-flow.md
✅ er-trade-core-entities.md
✅ test-payment-security-coverage.md
✅ feature-real-time-notifications.md
```

### 违规命名反例

```
❌ checkout.md                    # 缺失类型前缀
❌ feature_checkout.md            # 错误使用了下划线而非中划线
❌ FeatureCheckout.md             # 大小写不规范
❌ diagram1.md                    # 缺乏描述性
❌ feature-checkout-payment-flow-diagram.md  # 包含冗余的 "diagram" 后缀
❌ sequence-user-auth.md          # 缩写过度，含义不明确
```

## 目录归类指引

### features/ (功能目录)
**适用场景：**
- 面向用户的具体业务功能
- 某项功能的流转链路
- 功能模块内部的组件交互
- 某个明确业务边界内的用户操作

**典型案例：**
- 结算支付流程
- 消息通知推送系统
- 站内检索功能
- 用户个人资料维护修改

### architecture/ (架构目录)
**适用场景：**
- 系统级别的组织拓扑
- 多服务与多组件之间的交互协同
- 高层全貌总览图
- 基础设施与部署拓扑图
- 技术栈选型全景图

**典型案例：**
- 微服务分布式架构
- 全系统技术拓扑总览
- 跨服务数据流转图
- 生产环境部署架构图

### journeys/ (旅程目录)
**适用场景：**
- 基于时间推进的用户旅程
- 跨越多个连续步骤的完整过程
- 串联多个功能的端到端链路
- 新手引导与入驻流
- 完整的用户故事

**典型案例：**
- 身份认证旅程（登录 → 2FA → 权限校验 → 页面重定向）
- 完整购物旅程（浏览商品 → 加入购物车 → 提交订单 → 支付确认）
- 新人入驻旅程（注册账号 → 邮箱激活 → 初始化配置）

### tests/ (测试目录)
**适用场景：**
- 测试场景覆盖度文档
- 测试策略全景图
- 测试用例与用户价值的映射关系
- 核心关键路径 (Critical Path) 测试覆盖
- 安全与合规专项测试

**典型案例：**
- 支付安全测试场景覆盖
- 端到端 (E2E) 核心关键路径测试
- 核心服务集成测试保障策略

### refactoring/ (重构目录)
**适用场景：**
- 重构前后 (Before/After) 方案对比
- 性能专项优化改造
- 底层技术架构演进
- 代码质量与技术债务消除
- 消除架构腐化

**典型案例：**
- 引入 Redis 缓存层重构
- 核心数据库复杂慢查询优化
- 单体系统向微服务架构迁移拆分
- 异常容灾与自愈能力升级

## README.md 索引文件规范

索引是理解整个系统的第一入口。请始终保持其条理清晰、实时更新。

### 索引文件模板

```markdown
# 统一影响图总索引 (Unified Impact Diagrams Index)

本目录集中管理项目的所有系统图表，严格遵循图驱动开发（DDD）方法论。

**最后更新日期:** YYYY-MM-DD

## 快速导航

- [系统架构总览](#架构总览)
- [用户核心旅程](#用户核心旅程)
- [业务功能图表](#业务功能图表)
- [测试场景覆盖](#测试场景覆盖)

## 架构总览

高层系统设计与组件间依赖关系。

- [系统架构总览](architecture/arch-system-overview.md) - 覆盖核心服务与数据流转的系统全貌
- [微服务架构拓扑](architecture/arch-microservices-architecture.md) - 微服务边界划分与服务间通信模式

## 用户核心旅程

跨越时间维度的多步骤端到端用户体验。

- [用户身份认证旅程](journeys/sequence-authentication-journey.md) - 聚焦高安全性的登录、2FA 与账号找回流程
- [完整购物闭环](journeys/sequence-purchase-completion.md) - 从商品浏览、加购结算到收据确认的全流程
- [新用户激活入驻](journeys/sequence-onboarding-flow.md) - 新用户注册配置与首日体验流

## 业务功能图表

针对具体功能模块的交互流向与用户价值。

- [结算与支付](features/feature-checkout-payment-flow.md) - 具备失败重试恢复机制的安全支付链路
- [实时通知推送](features/feature-notification-system.md) - 基于 WebSocket 的毫秒级长连接通知
- [站内搜索](features/feature-search-functionality.md) - 带有热词联想与本地缓存的秒级检索

## 测试场景覆盖

我们如何通过分层自动化测试守护用户价值。

- [支付安全测试覆盖](tests/test-payment-security-coverage.md) - 围绕支付安全的综合测试保障策略
- [E2E 端到端核心路径](tests/test-e2e-critical-paths.md) - 端到端测试守护的关键业务主链路

## 重构改进方案

重大技术演进方案及预期的用户收益。

- [引入 Redis 缓存层](refactoring/feature-add-caching-layer.md) - 将平均加载耗时从 2s 骤降至 <100ms
- [慢查询深度优化](refactoring/feature-optimize-database-queries.md) - 仪表盘统计耗时提升 5 倍

## 图表建设原则

所有图表均遵循图驱动开发 (DDD) 原则：
- 严格同时呈现前台（用户体验）与后台（技术实现）双层视角
- 包含清晰解释用户收益的影响标注
- 标明异常错误路径与用户挽救选项
- 明确建立技术决策到用户收益的映射

## 维护指引

新增或修改图表时：
1. 遵循 DDD 核心原则
2. 存入标准目录并使用合规的文件命名
3. 及时在本索引文件中同步更新条目
4. 在图表文档尾部记录变更历史
5. 刷新本索引文件顶部的“最后更新日期”

## 近期变更记录

- **2025-01-16:** 增加缓存层重构前后对比方案图
- **2025-01-15:** 在身份认证旅程图中补充 2FA 流程
- **2025-01-10:** 创建实时通知系统全流程图
```

### 索引维护最佳实践

1. **实时同步更新** - 任何图表发生增删改，必须立刻更新索引
2. **提供充足上下文** - 条目后附带一句话说明其交付的用户价值
3. **分门别类归纳** - 按业务属性聚合归类
4. **设置锚点链接** - 提供顶部快速导航栏，方便跳转
5. **记录近期动态** - 维护变更摘要，方便团队跟踪

## 图表目录重构流程

当现有目录混乱需要规范治理时：

### 1. 制定重构计划

```markdown
## 目录规范重构计划

**目标:** 将零散混乱的旧图表统一收纳至规范目录体系中

**整改项:**
1. 移动 `diagram1.md` → `features/feature-checkout-flow.md`
2. 重命名 `auth.md` → `journeys/sequence-authentication-journey.md`
3. 创建缺失的 `architecture/` 目录
4. 将系统拓扑图移入 `architecture/`
5. 全面排查并修复 README.md 索引中的所有链接
```

### 2. 系统化执行迁移

```bash
# 创建标准子目录体系
mkdir -p ai/diagrams/{features,architecture,journeys,tests,refactoring}

# 使用 git mv 迁移并规范重命名（保留提交历史）
git mv ai/diagrams/diagram1.md ai/diagrams/features/feature-checkout-flow.md
git mv ai/diagrams/auth.md ai/diagrams/journeys/sequence-authentication-journey.md

# 更新图表文件内部的“Related Files”相对路径
# 全面更新 README.md 索引文件
```

### 3. 重构后的复核验收

- [ ] 所有图表文件均已归位至规范子目录下
- [ ] 所有文件名均严格符合命名规范
- [ ] README.md 索引已刷新无遗漏
- [ ] 索引中的链接全部有效无死链
- [ ] 使用 `git mv` 完好保留了历史版本记录

## 常见组织混乱场景与整改方案

### 场景 1：图表全部堆砌在根目录下

**错误现状：**
```
ai/diagrams/
├── checkout.md
├── auth.md
├── system.md
└── README.md
```

**整改方案：**
```bash
# 规划子目录并规整移入
mkdir -p ai/diagrams/{features,architecture,journeys}
git mv ai/diagrams/checkout.md ai/diagrams/features/feature-checkout-flow.md
git mv ai/diagrams/auth.md ai/diagrams/journeys/sequence-authentication-journey.md
git mv ai/diagrams/system.md ai/diagrams/architecture/arch-system-overview.md
```

### 场景 2：命名风格参差不齐

**错误现状：**
```
features/
├── feature-checkout.md
├── checkout-flow.md
├── Checkout.md
└── feature_payment.md
```

**整改方案：**
```bash
# 统一规整命名
git mv feature-checkout.md feature-checkout-flow.md
git mv checkout-flow.md feature-checkout-alternate.md  # 或合并内容
git mv Checkout.md feature-checkout-main.md  # 或合并内容
git mv feature_payment.md feature-payment-processing.md
```

### 场景 3：分类目录放错

**错误现状：**
```
features/arch-system-overview.md    # 架构图误放入 features 目录
journeys/feature-search.md          # 功能图误放入 journeys 目录
```

**整改方案：**
```bash
# 纠正目录归类
git mv features/arch-system-overview.md architecture/
git mv journeys/feature-search.md features/
```

### 场景 4：内容重复的冗余图表

**错误现状：**
```
features/
├── feature-checkout-flow.md
├── feature-checkout-payment.md
└── feature-payment-checkout.md
```

**整改方案：**
1. 深入通读对比三张图表
2. 研判究竟属于同一功能的重复产物，还是各有侧重
3. 若属于重复：合并提炼为一张完备的图表，删除冗余旧图
4. 若各有侧重：重命名以精准区分各自边界
   - `feature-checkout-cart-management.md`（购物车管理）
   - `feature-checkout-payment-processing.md`（支付处理）
   - `feature-checkout-order-confirmation.md`（订单确认）

## 日常运维命令手册

### 按类型检索列出所有图表

```bash
# 功能流程图
find ai/diagrams/features -name "feature-*.md"

# 用户旅程时序图
find ai/diagrams/journeys -name "sequence-*.md"

# 系统架构图
find ai/diagrams/architecture -name "arch-*.md"
```

### 检查放错目录的文件

```bash
# 架构图放到了非 architecture 目录下
find ai/diagrams -name "arch-*.md" -not -path "*/architecture/*"

# 功能图放到了非 features 目录下
find ai/diagrams -name "feature-*.md" -not -path "*/features/*"

# 时序图放到了非 journeys 目录下
find ai/diagrams -name "sequence-*.md" -not -path "*/journeys/*"
```

### 校验文件名合规性

```bash
# 查找命名不符合规范的文件
find ai/diagrams -name "*.md" -not -name "README.md" | while read file; do
  basename "$file" | grep -vE '^(feature|sequence|arch|flow|test)-[a-z0-9-]+\.md$' && \
    echo "命名违规: $file"
done
```

### 检查索引死链

```bash
# 提取 README.md 中的所有相对链接并逐一测试物理文件是否存在
grep -oP '\]\(\K[^)]+' ai/diagrams/README.md | while read link; do
  if [ ! -f "ai/diagrams/$link" ]; then
    echo "检测到损坏死链: $link"
  fi
done
```

## 迁移执行自查清单

重构组织现有图表时，请按步骤核对：

- [ ] 备份当前分支状态（执行 git commit）
- [ ] 明确编制好重构迁移规划
- [ ] 提前创建好目标规范子目录
- [ ] 使用 `git mv` 执行文件迁移（保留历史提交记录）
- [ ] 按规范批量重命名文件
- [ ] 全量刷新 `README.md` 索引
- [ ] 更新图表内部引用的相对路径
- [ ] 执行死链脚本核对无误
- [ ] 提交规范清晰的 Git Commit
- [ ] 在团队沟通渠道同步目录结构变更

## 核心最佳实践

1. **必须使用 `git mv`** - 完整保留代码与图表的版本历史
2. **专目录专图** - 严禁混放不同类型的图表
3. **强制使用统一类型前缀** - 望文生义，提升工程可读性
4. **命名具备明确描述性** - 见名知意，直接体现业务价值
5. **实时保持 README 最新** - 图表变动后第一时间更新索引
6. **定期开展组织审计** - 建议每月自动排查一次目录规范
7. **完整记录结构变更** - 在 README 中清晰留下调整记录
8. **强化团队协同同步** - 目录演进及时通知团队相关成员
9. **绝不留无索引孤岛** - 确保每张图表都在 README 中有迹可循
10. **定期清理废弃死图** - 及时下线无效的老旧图表

## 快速速查指引

### 目录归类决策树

```
该图是否展示系统宏观架构或数据库模型？
├─ 是架构总览 → 放入 architecture/arch-{名称}.md
├─ 是数据ER模型 → 放入 architecture/er-{名称}.md (推荐 PlantUML)
└─ 否 → 是否涉及跨部门多角色协作业务流？
    ├─ 是 → 放入 journeys/lane-{名称}.md 或 features/lane-{名称}.md (推荐 PlantUML 泳道图)
    └─ 否 → 是否为基于时间推进的多步骤用户旅程？
        ├─ 是 → 放入 journeys/sequence-{名称}.md
        └─ 否 → 是否为某一具体功能业务流？
            ├─ 是 → 放入 features/feature-{名称}.md
            └─ 否 → 是否专门用于说明测试保障策略？
                ├─ 是 → 放入 tests/test-{名称}.md
                └─ 否 → 是否为重构前后方案对比？
                    ├─ 是 → 放入 refactoring/feature-{名称}.md
                    └─ 否 → 选取最贴近的目录归类
```

### 命名合规自检五问

1. 是否全为小写英文字母？ ✓
2. 是否包含合规的类型前缀（如 feature-、arch- 等）？ ✓
3. 是否纯使用中划线连接词语？ ✓
4. 词数是否精简在 2-5 个词之间且表意清晰？ ✓
5. 是否以 `.md` 结尾？ ✓

### 索引条目登记模板

```markdown
## [分类名称]

- [清晰标题](目录名/文件名.md) - 阐述用户核心价值的简明说明
```
