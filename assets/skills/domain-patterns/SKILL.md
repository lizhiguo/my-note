---
name: domain-patterns
description: DDD 战术模式 + CQRS + 六边形架构设计规范。在 propose、design、specs、tasks 阶段涉及新建或修改领域模块时必须读取。包含架构分层、调用链、聚合设计原则、文件命名约束、任务拆分顺序、领域建模方法论。
---

# OSG DDD Patterns

## 阶段与 Reference 对照

| 当前阶段 | 必须读取 | 目的 |
|----------|---------|------|
| **propose** | references/architecture.md | 了解模块边界、调用链方向、分层禁止事项 |
| **propose** | references/biz-analysis.md | 领域词汇表、角色定义、聚合边界初判 |
| **design.md** | references/architecture.md + references/design-guide.md | 确定聚合设计、文件清单、调用链、API 接口 |
| **specs/** | references/design-guide.md | 场景描述与架构约定对齐 |
| **tasks.md** | references/design-guide.md | 按正确顺序拆分任务（domain → app → adapter → api） |
| **apply** | 切换到 osg-ddd-coding（详见该 skill 的 references/） | 代码模板和检查清单 |

---

## 核心原则（所有设计阶段都适用）

1. **没有 Service 层**：本架构不存在 `XxxService`，只有 `CommandHandler`、`QueryHandler`、`DomainService`
2. **读写严格分离（CQRS）**：写操作走 JPA + CommandHandler + Aggregate + Repository，读操作走 MyBatis + QueryHandler + ReadModel，两条链不交叉
3. **层间只通过 Port 接口依赖**：Controller → UseCase（@PrimaryPort），QueryHandler → Dao（@SecondaryPort），不跨层直接调用
4. **转换函数链固定**：`VO.toCommand()` → `Cmd.toAttr()` → `Attr.toEntity()` → `Entity.toDto()`
5. **领域层不依赖外层**：领域实体只接受 `Attr`，不接受 `Command` 或 `VO`
6. **禁止带前缀命名**：文件名使用固定规范名称（`Entities.kt`、`Repository.kt`），严禁加业务模块前缀（如 `DictEntity.kt`）
7. **聚合优先**：所有业务入口来自聚合根，不直接操作聚合内实体。聚合间通过 ID 引用
8. **小聚合优先**：聚合越小并发冲突越少，按不变性约束拆分，不追求一个模块一个聚合

---

## 1. propose 阶段

### 1.1 必须明确的内容

**模块归属**：新功能属于哪个业务模块？
- 已有模块扩展（在现有模块下增加聚合/功能）
- 还是新建独立模块

**读写操作识别**：
- 写操作（Create / Modify / Delete / ChangeStatus）→ Command + Aggregate + Repository
- 读操作（Get / List / Page）→ Query + ReadModel

**聚合设计初判**：
- 是否只有一个聚合根？还是聚合根 + 聚合内实体？
- 是否是树形结构？（影响基类选择：`AbstractAuditableJpaEntity` vs `AbstractAuditableJpaTreeEntity`）
- 是否需要领域事件解耦聚合间通信？

**跨模块依赖**：
- 是否需要监听其他模块的领域事件？
- 是否需要发布事件给其他模块？

### 1.2 禁止事项

- 不定义具体字段名（由 design 阶段决定）
- 不提出创建 `XxxService`（本架构没有 Service 层）
- 不跳过 domain 层直接讨论 Controller 接口

---

## 2. design.md 阶段（最重要）

design.md 决定了整个实现方向。必须包含以下章节：

### 2.1 模块与包名

```
模块：reke-modules/<module>
基础包：com.erke.biz.<module>
```

### 2.2 聚合根设计

明确以下内容：
- 聚合根名称和对应的表名
- 聚合内实体（如有）
- 实体基类选择（`AbstractAuditableJpaEntity` vs `AbstractAuditableJpaTreeEntity`）
- 值对象设计（嵌入值对象 / 枚举值对象）
- 状态机（如有状态字段，列出允许的状态转换路径）

### 2.3 DomainService 设计（强制）

每个聚合根必须有一个 DomainService，集中管理所有跨字段/跨聚合的业务规则校验。

**必须包含的要素**：
- `getXxx(id)` — 按 ID 查询聚合根，不存在时抛业务异常
  - **探索期可省略**：design.md 需注明「本模块无跨聚合校验，getXxx 暂缺」，出现第 2 个聚合后补齐
- 每个业务校验一个独立方法，命名格式 `validate<校验项>`
  - **探索期可延后**：业务规则未确定时只写方法签名与 TODO，不猜校验条件；Spec DSL 同理（无实际校验就不建 Spec object）
- **所有校验方法的查询条件必须委托给同文件内的 `<Entity>Spec` object**

**Spec object 设计清单**：
```
uniqueCheck(<field>, excludeId)   ← 唯一性校验专用
byXxx(value)                       ← 单条件精确匹配
byXxxAndYyy(a, b)                 ← 多条件 AND 组合
```

### 2.4 写操作设计（每个操作）

```
操作名：CreateXxx
调用链：Controller → RestAssembler(vo→cmd) → UseCase(cmd) → CommandHandler
         → DomainService.validateXxx() → cmd→attr → Aggregate.create(attr)
         → repository.save → 发布事件 → entity→dto
```

### 2.5 读操作设计（每个操作）

```
操作名：GetById
调用链：Controller → QueryCase(query) → QueryHandler → Dao → 返回 View
```

### 2.6 需要新建的文件清单

按六边形层级列出每个文件（必须明确到文件粒度）：

```
domain/model/
  - Entities.kt      # 聚合根 + 聚合内实体
  - ValueObjects.kt  # 值对象 + 枚举 + 枚举转换器
  - Inputs.kt        # Attr 数据类 + toEntity() 扩展函数

domain/repo/
  - Repository.kt    # 仓储接口 (@SecondaryPort)

domain/service/
  - DomainService.kt # 领域服务 + Spec DSL

domain/event/
  - Events.kt        # 领域事件 sealed class

domain/exception/
  - ErrorCode.kt     # 错误码枚举

app/port/in/
  - UseCase.kt       # 写操作入站端口 (@PrimaryPort)
  - QueryCase.kt     # 读操作入站端口 (@PrimaryPort)

app/port/out/
  - Dao.kt           # 读操作出站端口 (@SecondaryPort)

app/command/
  - Commands.kt      # 命令定义 + toAttr() 扩展函数
  - CommandHandler.kt

app/query/
  - Queries.kt       # 查询对象
  - QueryHandler.kt

app/helper/
  - AppAssembler.kt  # Entity.toDto() 扩展函数

adapter/in/rest/
  - Controller.kt
  - RestAssembler.kt # VO.toCommand() 扩展函数

adapter/out/write/jpa/
  - JpaRepositories.kt
  - RepositoryAdapter.kt

adapter/out/read/mybatis/
  - Mappers.kt
  - DaoAdapter.kt

api/model/
  - Vos.kt    # 请求 VO
  - Dtos.kt   # 写操作响应 DTO
  - Filters.kt # 查询条件
  - Views.kt  # 读操作响应 View

resources/mapper/
  - XxxMapper.xml    # 一个聚合根只对应一个 XML
```

**文件命名铁律**：禁止业务前缀命名。同一个包下的同类文件会被合并，物理文件名固定：

| 正确 | 错误 |
|------|------|
| Entities.kt | DictEntity.kt, UserEntity.kt |
| ValueObjects.kt | DictValueObjects.kt |
| Repository.kt | DictRepository.kt |
| CommandHandler.kt | DictCommandHandler.kt |
| Controller.kt | DictController.kt |

### 2.7 API 接口设计

```
POST   /api/v1/<resources>              # 创建
PUT    /api/v1/<resources>/{id}         # 修改
DELETE /api/v1/<resources>/{id}         # 删除
PATCH  /api/v1/<resources>/{id}/status  # 状态变更
GET    /api/v1/<resources>/{id}         # 单条查询
GET    /api/v1/<resources>              # 列表查询
GET    /api/v1/<resources>/page         # 分页查询
```

### 2.8 禁止事项

| 禁止 | 原因 |
|------|------|
| 设计 `XxxService` 类 | 没有 Service 层 |
| 文件名带业务前缀 | 固定规范名 |
| Controller 中注入 Repository | 违反六边形分层 |
| QueryHandler 中调用 Repository | 读写分离 |
| DTO 直接从领域实体暴露 | 需经过 AppAssembler |
| 领域层依赖 Command 或 VO | 领域层只接受 Attr |
| DomainService 中直接拼 Specification | 必须经过 Spec object |
| DomainService 调用持久化写操作 | 保存和删除由 CommandHandler 负责 |
| DomainService 调用 Dao / Mapper | 读操作走 Query 通道 |

---

## 3. specs/ 阶段

### 3.1 场景描述要求

每个 spec 文件的场景必须与架构约定对齐：

```markdown
#### 场景: 创建成功
- **当** 请求中包含有效的字段
- **那么** 返回创建后的 DTO（含 id、审计字段）
- **且** 聚合根状态为 DRAFT
- **且** 发布领域事件

#### 场景: 字段重复时创建失败
- **当** 数据库中已存在相同字段值
- **那么** 返回业务异常，错误码为 XXX_DUPLICATE
```

### 3.2 场景覆盖要求

每个写操作至少覆盖：
- 正常成功路径
- 业务校验失败（唯一性 / 数量上限 / 状态前置条件）
- 实体不存在的失败路径
- 状态不允许操作的失败路径（如有状态机）

每个读操作至少覆盖：
- 查到数据的成功路径
- 查不到数据返回 null 或空列表
- 分页参数边界

---

## 4. tasks.md 阶段

### 4.1 任务拆分顺序（强制，依赖关系决定）

```
1. domain/model/ValueObjects.kt      # 枚举、值对象、转换器
2. domain/model/Entities.kt          # 聚合根 + 聚合内实体
3. domain/model/Inputs.kt            # Attr 数据类 + 扩展函数
4. domain/event/Events.kt            # 领域事件
5. domain/exception/ErrorCode.kt     # 错误码枚举
6. domain/repo/Repository.kt         # 仓储接口
7. domain/service/DomainService.kt   # 领域服务 + Spec DSL
8. api/model/Dtos.kt                 # 写操作响应 DTO
9. api/model/Views.kt                # 读操作响应 View
10. api/model/Filters.kt             # 查询条件
11. api/model/Vos.kt                 # 请求 VO
12. app/port/in/UseCase.kt           # 写操作入站端口
13. app/port/in/QueryCase.kt         # 读操作入站端口
14. app/command/Commands.kt          # 命令定义
15. app/query/Queries.kt             # 查询对象
16. app/port/out/Dao.kt              # 读操作出站端口
17. app/helper/AppAssembler.kt       # Entity.toDto()
18. app/command/CommandHandler.kt    # 命令处理器
19. app/query/QueryHandler.kt        # 查询处理器
20. adapter/out/write/jpa/JpaRepositories.kt
21. adapter/out/write/jpa/RepositoryAdapter.kt
22. adapter/out/read/mybatis/Mappers.kt
23. resources/mapper/XxxMapper.xml
24. adapter/out/read/mybatis/DaoAdapter.kt
25. adapter/in/rest/RestAssembler.kt
26. adapter/in/rest/Controller.kt
27. 单元测试：EntityTest
28. 单元测试：DomainServiceTest
29. 单元测试：CommandHandlerTest
30. 单元测试：QueryHandlerTest
31. 集成测试（JPA / MyBatis / REST，至少覆盖涉及层）
```

### 4.2 任务粒度要求

- 每个任务对应**一个文件**
- 任务描述格式：`创建 XxxYyy.kt - [职责一句话说明]`
- 不要出现"创建所有模型文件"这种粗粒度任务

### 4.3 子代理分配

| 子代理 | 负责层 | 依赖 |
|--------|--------|------|
| Agent-A | domain 层 | 无 |
| Agent-B | app 层 | Agent-A |
| Agent-C | adapter + api 层 | Agent-B |

---

## 常见错误

| 错误 | 修复 |
|------|------|
| 创建 XxxService | 没有 Service 层，用 CommandHandler / DomainService |
| 读写操作混在一个类 | CQRS 严格分离，写走 Command 链，读走 Query 链 |
| 文件名带业务前缀 | 禁止 UserEntity.kt，用 Entities.kt |
| 跨层直接调用 | 必须通过 Port 接口（UseCase / Repository） |
| 聚合过大 | 按不变性约束拆分，小聚合优先 |
| 读操作走 JPA | 读操作走专用查询引擎（MyBatis / raw SQL / projection） |
| DomainService 中直接拼 Specification | 必须经过 Spec object 统一管理 |
| DomainService 调用 save/delete | 保存和删除统一由 CommandHandler 负责 |
