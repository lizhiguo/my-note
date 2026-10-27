# DDD 设计阶段规范

> 用于 **propose → design.md → specs/ → tasks.md** 阶段。
> apply 阶段的代码模板见 osg-ddd-coding skill 的 references/。

---

## 1. propose 阶段

### 1.1 必须明确的内容

**模块归属**：新功能属于哪个业务模块？
- 已有模块扩展（在现有模块下增加聚合/功能）
- 还是新建独立模块（`reke-modules/<new-module>/`）

**读写操作识别**：
- 哪些操作是写（Create / Modify / Delete / ChangeStatus）→ 走 Command + JPA
- 哪些操作是读（Get / List / Page）→ 走 Query + MyBatis

**跨模块依赖识别**：
- 是否需要监听其他模块的领域事件？
- 是否需要发布事件给其他模块？

**聚合设计初判**：
- 是否只有一个聚合根？还是聚合根 + 聚合内实体？
- 是否是树形结构？（影响基类选择）

### 1.2 Propose 禁止事项

- 不要在 propose 阶段定义具体字段名（由 design 阶段决定）
- 不要提出创建 `XxxService`（本架构没有 Service 层）
- 不要跳过 domain 层直接讨论 Controller 接口

---

## 2. design.md 阶段（最重要）

design.md 决定了整个实现方向。这里一旦走偏，tasks 和 apply 全错。

### 2.1 必须包含的章节

#### 2.1.1 模块与包名
```
模块：reke-modules/<module>
基础包：com.erke.biz.<module>
```

#### 2.1.2 聚合根设计

明确以下内容：
- 聚合根名称和对应的表名
- 聚合内实体（如有）
- 实体基类选择：

| 基类 | 适用场景 |
|------|----------|
| `AbstractAuditableJpaEntity` | 普通实体（含审计字段） |
| `AbstractAuditableJpaTreeEntity` | 树形结构（菜单、分类、组织） |

- 值对象设计（嵌入值对象 / 枚举值对象）
- 状态机（如有状态字段，列出允许的状态转换路径）

#### 2.1.3 领域服务设计（强制）

领域服务是聚合根的业务守门人。**每个聚合根必须有一个 DomainService**，集中管理所有跨字段/跨聚合的业务规则校验。

**设计 DomainService 时必须回答的三个问题**：
1. 哪些字段需要唯一性校验？→ 对应 Spec 方法：`uniqueCheck(field, excludeId)`
2. 有哪些数量/范围限制？→ 对应 Spec 方法：`byXxx()` + `count()`
3. 有哪些状态前置条件？→ 组合 Spec 条件

**必须包含的要素**：
- `getXxx(id)` — 按 ID 查询聚合根，不存在时抛出 `ErrorCode.XXX_NOT_FOUND`
- 每个业务校验一个独立方法，命名格式 `validate<校验项>`（如 `validateNameUniqueness`、`validateCountLimit`）
- **所有校验方法的查询条件必须委托给同文件内的 `<Entity>Spec` object**，严禁在方法体内直接拼接 `Specification`

**Spec object 设计清单**：
```
object <Entity>Spec {
    uniqueCheck(<field>, excludeId)   ← 唯一性校验专用
    byXxx(value)                       ← 单条件精确匹配
    byXxxAndYyy(a, b)                 ← 多条件 AND 组合
    ...
}
```

**典型 DomainService 调用链位置**（写操作中，位于 `toAttr()` 之前）：
```
CommandHandler
  → domainService.validateXxxUniqueness(...)   ← 业务校验（先）
  → domainService.getXxx(id)                   ← 获取聚合根（后，需要修改时）
  → cmd.toAttr()                               ← 命令转换
  → entity.create(attr) / entity.modify(attr)  ← 领域方法
  → repository.save(entity)                    ← 持久化
```

#### 2.1.4 写操作设计

每个写操作列出：

```
操作名：Create<Entity>
命令：<Entity>Cmd.Create
调用链：
  Controller.create(vo)
  → RestAssembler.VO.toCommand() → Cmd.Create
  → UseCase.handle(Cmd.Create)
  → CommandHandler
      → domainService.validateCodeUniqueness(cmd.code)  → Spec.uniqueCheck(code)
      → Attr = cmd.toAttr()
      → Entity.create(attr)
      → repository.save(entity)
  → entity.toDto()
领域方法：Entity.create(attr) - 工厂方法，发布 Created 事件
```

#### 2.1.5 读操作设计

每个读操作列出：

```
操作名：GetById
查询：<Entity>Query.GetQuery
调用链：
  Controller.get(id)
  → QueryCase.handle(GetQuery(id))
  → QueryHandler → Dao.findById(id)
  → DaoAdapter → Mapper.selectById(id)
  → 直接返回 View
返回类型：<Entity>View（MyBatis 直接映射）
```

#### 2.1.6 需要新建的文件清单

按六边形层级列出每个文件（design 阶段必须明确到文件粒度）：

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

#### 2.1.7 API 接口设计

```
POST   /api/v1/<resources>          # 创建
PUT    /api/v1/<resources>/{id}     # 修改
DELETE /api/v1/<resources>/{id}     # 删除
PATCH  /api/v1/<resources>/{id}/status  # 状态变更
GET    /api/v1/<resources>/{id}     # 单条查询
GET    /api/v1/<resources>          # 列表查询
GET    /api/v1/<resources>/page     # 分页查询
```

### 2.2 design.md 禁止事项

| 禁止 | 原因 |
|------|------|
| 设计 `XxxService` 类 | 本架构没有 Service 层，用 CommandHandler / QueryHandler / DomainService |
| 随意命名文件带实体前缀（如 `XxxEntity.kt`） | 文件名必须使用固定规范名称（如 `Entities.kt`, `Repository.kt`） |
| 在 Controller 中注入 Repository | 违反六边形分层 |
| 在 QueryHandler 中调用 Repository | 读写分离，QueryHandler 只用 Dao |
| DTO 直接从领域实体暴露 | 需经过 AppAssembler 扩展函数转换 |
| 使用 @Service 注解的业务类 | 用 @Component + @PrimaryAdapter 替代 |
| 让领域层依赖 Command 或 VO | 领域层只接受 Attr |
| DomainService 中直接拼接 Specification | 必须经过 Spec object 统一管理 |
| DomainService 调用任何持久化写操作（save / delete） | 保存和删除统一由 CommandHandler 负责 |
| DomainService 调用 Dao / Mapper | 读操作走 Query 通道，DomainService 只用 Repository |
| 跳过 DomainService 在 CommandHandler 中直接校验 | 跨字段业务规则必须放在 DomainService |

---

## 3. specs/ 阶段

### 3.1 场景描述要求

每个 spec 文件的场景（Scenario）必须与架构约定对齐：

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
- 业务校验失败（唯一性 / 数量上限 / 状态前置条件），需明确对应 `DomainService.validateXxx()` 和 `Spec.xxx()`
- 实体不存在的失败路径（`DomainService.getXxx()` → `XXX_NOT_FOUND`）
- 状态不允许操作的失败路径（如有状态机）

每个读操作至少覆盖：
- 查到数据的成功路径
- 查不到数据返回 null 或空列表
- 分页参数边界（如 pageSize 超限）

---

## 4. tasks.md 阶段

### 4.1 任务拆分顺序（必须按此顺序，依赖关系决定）

```
1. domain/model/ValueObjects.kt      # 枚举、值对象、转换器
2. domain/model/Entities.kt          # 聚合根 + 聚合内实体
3. domain/model/Inputs.kt            # Attr 数据类 + Attr→Entity 扩展函数
4. domain/event/Events.kt            # 领域事件
5. domain/exception/ErrorCode.kt     # 错误码枚举
6. domain/repo/Repository.kt         # 仓储接口 (@SecondaryPort)
7. domain/service/DomainService.kt   # 领域服务 + Spec DSL
8. api/model/Dtos.kt                 # 写操作响应 DTO
9. api/model/Views.kt                # 读操作响应 View
10. api/model/Filters.kt             # 查询条件
11. api/model/Vos.kt                 # 请求 VO
12. app/port/in/UseCase.kt           # 写操作入站端口 (@PrimaryPort)
13. app/port/in/QueryCase.kt         # 读操作入站端口 (@PrimaryPort)
14. app/command/Commands.kt          # 命令定义 + toAttr() 扩展函数
15. app/query/Queries.kt             # 查询对象定义
16. app/port/out/Dao.kt              # 读操作出站端口 (@SecondaryPort)
17. app/helper/AppAssembler.kt       # Entity.toDto() 扩展函数
18. app/command/CommandHandler.kt    # 命令处理器
19. app/query/QueryHandler.kt        # 查询处理器
20. adapter/out/write/jpa/JpaRepositories.kt   # JPA 接口
21. adapter/out/write/jpa/RepositoryAdapter.kt # 写出站适配器 (@SecondaryAdapter)
22. adapter/out/read/mybatis/Mappers.kt        # MyBatis Mapper 接口
23. resources/mapper/XxxMapper.xml             # SQL 映射文件 (一个聚合根仅限一个XML)
24. adapter/out/read/mybatis/DaoAdapter.kt     # 读出站适配器 (@SecondaryAdapter)
25. adapter/in/rest/RestAssembler.kt           # VO.toCommand() 扩展函数
26. adapter/in/rest/Controller.kt              # REST 控制器 (@PrimaryAdapter)
27. 单元测试：EntityTest                        # 领域实体核心方法
28. 单元测试：DomainServiceTest                 # 唯一性校验逻辑
29. 单元测试：CommandHandlerTest                # 命令处理流程
30. 单元测试：QueryHandlerTest                  # 查询处理流程
31. 集成测试（JPA / MyBatis / REST，至少覆盖涉及层）
```

### 4.2 任务粒度要求

- 每个任务对应**一个文件**，不要把多个层的文件合并成一个任务
- 任务描述格式：`创建 XxxYyy.kt - [职责一句话说明]`
- 不要出现 "创建所有模型文件" 这种粗粒度任务

### 4.3 Checkbox 格式

```markdown
## 1. 领域层

- [ ] 1.1 创建 ValueObjects.kt - 枚举、值对象、转换器
- [ ] 1.2 创建 Entities.kt - 聚合根（含聚合内实体）
- [ ] 1.3 创建 Inputs.kt - Attr 数据类 + toEntity()/updateEntity() 扩展函数
- [ ] 1.4 创建 Events.kt - 领域事件 sealed class
- [ ] 1.5 创建 ErrorCode.kt - 错误码枚举

## 2. 应用层接口

- [ ] 2.1 创建 Repository.kt - 仓储接口（@SecondaryPort）
- [ ] 2.2 创建 DomainService.kt - 唯一性校验 + Spec DSL
...
```

### 4.4 测试任务命名

```markdown
## N. 测试

- [ ] N.1 EntityTest - 领域实体单元测试（create/modify/changeStatus 覆盖率 ≥ 90%）
- [ ] N.2 DomainServiceTest - 领域服务单元测试（唯一性校验、实体不存在场景）
- [ ] N.3 CommandHandlerTest - 应用层 Handler 单元测试
- [ ] N.4 QueryHandlerTest - 查询处理器单元测试
```
