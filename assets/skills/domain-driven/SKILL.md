---
name: domain-driven
description: DDD 后端编码规范（Kotlin + Spring + jMolecules + JPA + MyBatis）。在 apply 阶段生成或修改代码时必须读取。包含各层代码骨架、注解规范、转换函数链、测试要求。
---

# OSG DDD Coding

## 阶段与 Reference 对照

| 当前任务 | 必须读取 | 目的 |
|---------|---------|------|
| 写领域层代码 | references/domain-layer.md | 实体、值对象、Inputs、Repository、DomainService、Events、ErrorCode |
| 写 API 层代码 | references/api-layer.md | Vos、Dtos、Filters、Views |
| 写应用层代码 | references/application-layer.md | Commands、UseCase、CommandHandler、Queries、QueryCase、QueryHandler、Dao、AppAssembler |
| 写适配器层代码 | references/adapter-layer.md | Controller、RestAssembler、JpaRepositories、RepositoryAdapter、Mappers、XML、DaoAdapter |
| 写测试 | references/testing.md | TDD 格式、覆盖率要求、mock 模式、集成测试 |

> 设计阶段（propose / design.md / specs / tasks）的规范见 osg-ddd-patterns skill。

---

## 开发顺序（强制，依赖关系决定）

```
领域层（无外部依赖，最先创建）
  → API 层（纯数据类，依赖领域层值对象）
    → 应用层接口（Port，依赖领域层 + API 层）
      → 应用层实现（Handler，依赖 Port + 领域层）
        → 单元测试（mockk，依赖领域层 + 应用层）
          → 适配器层（依赖应用层 Port）
            → 集成测试（Testcontainers，依赖适配器层 + 数据库）
```

**单元测试在 Handler 写完后立即写（TDD：先写测试再写代码）。集成测试在适配器层写完后立即写（需要实体映射/SQL/路由已存在才能跑，但同一 PR 内完成，不延后）。**

---

## 探索期使用方式（统一模板，内容分两次填）

**模板永远统一，不分模块深度。** 四层目录结构、依赖方向、转换链形状、类名与文件命名铁律从第一次提交起就完全一致；探索期与稳定期的区别只在于**每一步填多少内容**，不在于用哪种架构。

> 理由：代码全部由 AI 生成。结构一致时，review 的注意力可以全部释放给业务正确性；结构分档时 AI 会在不同模块间摇摆，同一份需求两次生成不同形状。

| 层 | 第一次填（物理骨架） | 业务确认后填（业务逻辑） |
|---|---|---|
| **domain** | `ValueObjects.kt`（枚举 + ID）、`Entities.kt`（字段 + `create`/`modify`）、`ErrorCode.kt`、`Inputs.kt`（全可空 Attr） | `DomainService` 校验规则、Spec DSL、`Events.kt` |
| **api** | `Vos.kt` / `Dtos.kt` / `Filters.kt` / `Views.kt`（纯数据类，无业务逻辑，一次填完） | 无 |
| **app** | `UseCase.kt` / `QueryCase.kt` / `Commands.kt` / `Queries.kt` / `CommandHandler.kt` / `QueryHandler.kt`（骨架 + 空实现） | Handler 内填真实编排；`AppAssembler` 抽为独立文件 |
| **adapter** | `Controller.kt` / `RestAssembler.kt` / `JpaRepositories.kt` / `RepositoryAdapter.kt` / `Mappers.kt` / `XxxMapper.xml` / `DaoAdapter.kt` | `EventListener.kt`（跨聚合事件） |

**探索期允许的三处简写**（仅限探索期，业务稳定后必须补齐）：

| 简写 | 允许条件 | 补齐信号 |
|---|---|---|
| 不写 `DomainService.getXxx(id)` | 该模块无跨聚合校验，唯一性/状态校验都在聚合内 | 出现第 2 个聚合，或校验需要查询其他聚合时 |
| `Entity.toDto()` 写在 Handler 内 | 读模型字段尚未定型 | `Dtos.kt` 结构稳定后抽到 `AppAssembler.kt` |
| `Events.kt` 留空 | 业务事实尚未确定 | 状态流转确认后 |

**探索期禁止提前做的事**（写死必然返工）：
- ❌ Spec DSL：它是业务规则的可执行形式，业务没定就写死等于猜
- ❌ 状态机：状态划分是需求中最易变的部分
- ❌ 聚合内实体拆分：探索期一个聚合根 + 一张主表足够

**升档信号**（出现任一条即为稳定期，第二次填充全部业务逻辑）：
1. 同一张表出现第 2 个写入入口，校验逻辑在两处复制
2. 某业务规则改动需同时动 3 个以上文件
3. 单实体字段超过 20 个，开始争论「这个字段属于哪一块」
4. 代码里出现 `if (status == A || status == B || status == D)` 这类离散分支
5. 需求讨论从「这个功能怎么做」变成「这个概念到底指什么」

**读模型必须独立设计**：`Views.kt` 的字段清单来自查询需求，不是 `Entities.kt` 的字段复制。一旦发现自己在照抄实体字段，说明读模型没独立设计，此时 `QueryHandler` 不走领域的收益会大幅缩水。跨 3 个聚合拼装的报表需求若走领域层，会退化成 N+1 查询 + 大量对象转换。

---

## 核心原则（所有层都适用）

1. **没有 Service 层**：本架构不存在 `XxxService`，只有 `CommandHandler`、`QueryHandler`、`DomainService`
2. **读写严格分离**：写操作走 JPA + CommandHandler，读操作走 MyBatis + QueryHandler，两条链不交叉
3. **层间只通过 Port 接口依赖**：Controller → UseCase（接口），QueryHandler → Dao（接口），不跨层直接调用
4. **转换函数链固定**：`VO.toCommand()` → `Cmd.toAttr()` → `Attr.toEntity()` → `Entity.toDto()`
5. **领域层不依赖外层**：领域实体只接受 `Attr`，不接受 `Command` 或 `VO`
6. **文件名不带业务前缀**：固定使用 `Entities.kt`、`Repository.kt` 等规范名，严禁 `DictEntity.kt` 这类命名
7. **强制书写注释**：类级、方法级及复杂业务点必须添加中文注释

---

## 1. 领域层开发

> 领域层是核心，不依赖任何外层。**最先创建，所有其他层围绕领域层构建。**
> 代码模板：`references/domain-layer.md`。

### 1.1 ValueObjects.kt — 值对象 + 枚举 + 枚举转换器

| 类别 | 注解 | 关键约束 |
|------|------|----------|
| 嵌入值对象 | `@ValueObject` + `@Embeddable` | data class，`init` 块做校验 |
| 枚举值对象 | `@ValueObject` | enum class，提供 `fromCode(code)` + `@JsonCreator` |
| 枚举转换器 | `@Converter(autoApply = true)` | 继承 `AbstractEnumConverter`，注册为全局自动应用 |

**常见错误**：
- 把值对象、枚举、转换器分散到多个文件 → 一个聚合根的所有值对象集中在一个 `ValueObjects.kt`
- 枚举转换器忘记 `autoApply = true` → 每个实体字段都要手动加 `@Convert`
- 枚举值对象只定义 `fromCode()` 不加 `@JsonCreator` → JSON 反序列化失败

### 1.2 Entities.kt — 聚合根 + 聚合内实体

| 要素 | 注解/基类 | 说明 |
|------|-----------|------|
| 聚合根类 | `@AggregateRoot` `@Audited` `@Entity` `@DynamicInsert` `@DynamicUpdate` `@Table` | 继承 `AbstractAuditableJpaEntity` 或 `AbstractAuditableJpaTreeEntity`（树形） |
| 聚合内实体 | `@Audited` `@Entity` | 继承 `AbstractAuditableJpaEntity`，**不标注** `@AggregateRoot` |
| ID 类 | `@Embeddable` | 嵌套在实体内，`data class`，实现 `Identifier` + `Serializable`，默认值 `SnowflakeGeneratorHelper.generate()` |

**聚合根必须提供的方法**：
- `companion object { fun create(attr): Entity }` — 工厂方法，发布 `Created` 事件
- `fun modify(attr)` — 修改方法，发布 `Modified` 事件
- `fun changeStatus(newStatus)` — 状态变更，内部校验状态机转换合法性
- 每个领域方法内调用 `registerEvent()`

**常见错误**：
- 聚合根暴露 public constructor → 用 `create()` 工厂方法
- ID 类写在单独文件 → 嵌套在实体类内
- 聚合内实体标注 `@AggregateRoot` → 只有聚合根标注
- 领域方法直接写业务校验 → 跨字段校验放 `DomainService`
- 忘记 `@DynamicUpdate` → JPA 每次更新全字段
- 自定义 `_events` 列表 + `private fun registerEvent()` → 遮蔽父类 `AbstractAggregateRoot.registerEvent()`，事件永远无法被 Spring Data 发布。无需自己写事件管理代码，直接在领域方法中调用 `registerEvent(event)` 即可

### 1.3 Inputs.kt — Attr 数据类 + 转换扩展函数

- Attr 所有字段**可空**（`?= null`），支持部分更新
- Attr 不依赖 Command 或 VO，是领域层的纯净输入
- `toEntity()` — 新建时用，创建新实体实例并赋值
- `updateEntity(entity)` — 修改时用，只更新非 null 字段到已有实体

### 1.4 Events.kt — 领域事件

- 使用 sealed class 封装该聚合根所有事件
- 每个具体事件用 data class，标注 `@DomainEvent(namespace, name)`
- 事件只携带 `entityId`，不携带大量数据（消费方需要时可回查）
- 事件在聚合根领域方法中通过 `registerEvent()` 发布

### 1.5 ErrorCode.kt — 错误码枚举

- 每个错误码 = `code`（字符串编号）+ `msg`（支持 `{0}` 占位符）
- `code` 格式：`<PREFIX>_NNNN`（4 位数字，从 0001 开始）
- 必须覆盖的错误码：`XXX_NOT_FOUND`、`XXX_YYY_DUPLICATE`、`XXX_STATUS_NOT_ALLOWED`、`XXX_COUNT_LIMIT_EXCEEDED`
- 抛出方式：`BizException.of(ErrorCode.XXX_NOT_FOUND, args)`

### 1.6 Repository.kt — 领域仓储接口（出站端口）

- 注解：`@Repository`（DDD）+ `@SecondaryPort`（六边形）
- 继承 `IBaseDomainRepository<E, ID>`，获得 `save/delete/findByIdOrNull/existsById`
- 额外方法：`exists(Specification)` — 供 DomainService 做存在性检查
- **不放查询方法**：查询方法（findByXxx、listByXxx）一律走 Dao，不走 Repository

### 1.7 DomainService.kt — 领域服务 + Spec DSL

**领域服务三件事（只能做这三件）**：
1. **按 ID 查询聚合根**：`getXxx(id)` — 不存在抛 `XXX_NOT_FOUND`
   - **探索期可省略**：仅当该模块无跨聚合校验（唯一性/状态校验都在聚合内）时省略，出现第2 个聚合后必须补齐
2. **业务规则校验**：唯一性、数量上限、状态前置条件 — 使用 Spec DSL
   - **探索期可延后**：业务规则未确定时不写 Spec DSL，宁可先不加校验也不要猜错
3. **返回领域数据**：给 CommandHandler 提供聚合根实例

**领域服务三不碰**：
- 不调用任何持久化写操作 — `repository.save()` / `delete()` 等一律禁止
- 不调用 Dao / Mapper — 读操作走 Query 通道
- 不依赖 Command / VO / DTO — 只接受 Attr、值对象、基本类型

**Spec DSL 规范（强制）**：
- Spec object 必须定义在 DomainService.kt **同文件内**，命名 `<Entity>Spec`
- 所有 condition query 必须经过 Spec object，严禁在方法内直接拼 `Specification`
- 使用 `and()` / `or()` / `equal()` / `notEqual()` / `like()` / `between()` DSL

---

## 2. API 层开发

> API 层是纯数据类，**无业务逻辑**。所有字段使用可空类型。
> 代码模板：`references/api-layer.md`。

### 2.1 Vos.kt — 请求 VO
- **不继承任何基类**（请求 VO 只包含客户端提供的字段）
- `@Schema` 标注 Swagger 文档
- Jakarta Validation 注解（`@NotBlank`、`@NotNull`、`@Size`）
- 类名后缀用大写 `VO`（非 `Vo`）

### 2.2 Dtos.kt — 写操作响应 DTO
- 字段对应 Entity 返回给前端的字段（值对象展开为简单类型）
- 包含审计字段：`createTime`、`updateTime`（`var`，由 `AppAssembler.also {}` 赋值）
- 类名后缀用大写 `DTO`（非 `Dto`）

### 2.3 Filters.kt — 查询条件
- 所有字段可空（`?= null`），无条件时不筛选
- **不加校验注解**（Filter 是查询条件，不是入参）

### 2.4 Views.kt — 读操作响应 View
- 由 MyBatis 直接从 SQL 结果集映射
- 可包含描述性字段（如 `statusDesc`）
- 字段名必须与 MyBatis XML 中 `resultMap` 的 `column` 一致

---

## 3. 应用层开发

> 应用层负责编排，不含业务逻辑。
> 代码模板：`references/application-layer.md`。

### 3.1 UseCase.kt — 写操作入站端口
- 注解：`@PrimaryPort`
- 方法名统一用 `handle`，通过参数类型（`Cmd.Xxx`）区分操作
- 返回类型：创建/修改返回 `XxxDTO`，删除返回 `Unit`

### 3.2 QueryCase.kt — 读操作入站端口
- 注解：`@PrimaryPort`
- 方法名统一用 `handle`，参数类型为 `XxxQuery.Xxx`
- 返回类型：`XxxView?`、`List<XxxView>?`、`PageResult<XxxView>?`

### 3.3 Commands.kt — 命令定义 + toAttr() 扩展函数
- sealed class 标注 `@Command(namespace)`
- 每个命令一个 data class
- 每个命令在同文件定义 `toAttr()` 扩展函数

### 3.4 Queries.kt — 查询对象
- sealed class 封装所有查询
- `GetQuery(entityId)` — 单条查询
- `ListQuery(filter)` — 列表查询
- `PageQuery(filter, pageNum, pageSize)` — 分页查询

### 3.5 Dao.kt — 读操作出站端口
- 注解：`@SecondaryPort`
- 定义读操作方法，返回 View 类型
- 由 `DaoAdapter`（适配器层）实现

### 3.6 CommandHandler.kt — 命令处理器
- 注解：`@PrimaryAdapter` + `@Component` + `@Transactional(rollbackFor = [Exception::class])`
- 注入：`Repository` + `DomainService`（不注入 Dao）
- 调用顺序：domainService.validate → cmd.toAttr() → Entity.create/modify → repository.save

### 3.7 QueryHandler.kt — 查询处理器
- 注解：`@PrimaryAdapter` + `@Component`
- 注入：只注入 `Dao`（不注入 Repository）
- 无需 `@Transactional`（只读操作）
- 直通转发：`dao.findById(query.entityId)`，不加任何业务逻辑

### 3.8 AppAssembler.kt — Entity → DTO 转换
- 值对象字段展开为简单类型（如 `status.code` → `status`）
- 审计字段使用 `.also {}` 赋值
- 使用 Kotlin 扩展函数，**不用 MapStruct**

---

## 4. 适配器层开发

> 适配器层是六边形的边界，负责协议转换。
> 代码模板：`references/adapter-layer.md`。

### 4.1 JpaRepositories.kt — JPA 仓储接口
- 继承 `IBaseJpaRepository<E, ID>` + `RevisionRepository<E, ID, Long>`（支持 Envers 审计查询）
- 不写任何自定义方法（自定义方法放在领域层 `Repository.kt` 接口）

### 4.2 RepositoryAdapter.kt — 写出站适配器
- 注解：`@SecondaryAdapter` + `@Repository`
- 继承 `BaseJpaAdapter<E, ID, R>`（获得 `save/delete/findByIdOrNull/existsById`）
- 实现自定义方法（如 `exists(Specification)`，委托给 `repository.exists(spec)`）

### 4.3 Mappers.kt — MyBatis Mapper 接口
- 注解：`@Mapper`（MyBatis）
- 方法名与 XML 中 `<select id>` 一致
- 参数用 `@Param` 注解
- **一个聚合根只对应一个 Mapper 接口**

### 4.4 XxxMapper.xml — MyBatis SQL 映射文件
- 文件位置：`src/main/resources/mapper/XxxMapper.xml`
- `namespace` 与 Mapper 接口全限定名一致
- 使用 `<sql id="baseColumns">` 提取公共字段列表
- 使用 `<resultMap>` 映射 View 对象
- **一个聚合根只对应一个 XML 文件**

### 4.5 DaoAdapter.kt — 读出站适配器
- 注解：`@SecondaryAdapter` + `@Repository`
- 注入 `XxxReadMapper`
- 分页查询使用 `PageHelper.startPage<XxxView>(pageNum, pageSize).doSelectPage { mapper.selectListByFilter(filter) }.toPageResult()`

### 4.6 RestAssembler.kt — VO → Command 转换
- 定义在 `adapter/in/rest/` 包
- 每个 VO 对应一个 `toCommand()` 扩展函数

### 4.7 Controller.kt — REST 控制器
- 注解：`@Tag(name = "中文模块名")` + `@PrimaryAdapter` + `@RestController` + `@RequestMapping("/api/v1/<resources>")`
- **只注入** `UseCase` + `QueryCase`，不注入 Repository / DomainService / Dao
- 每个方法直接调用端口或 RestAssembler，**不含任何业务逻辑**

**Swagger 注解规范（强制）**：
- `@Tag` — 类级别，name 用中文业务名，description 一句话概括
- `@Operation(summary, description)` — 每个方法必须标注
- `@ApiResponses` — 列出所有可能的 HTTP 状态码及含义
- `@Parameter(description, required, example)` — `@PathVariable` 和 `@RequestParam` 必须标注

### 4.8 EventListener.kt — 跨模块事件监听
- 注解：`@PrimaryAdapter` + `@Component`
- 使用 `@ApplicationModuleListener`（Spring Modulith）异步监听
- 文件位置：`adapter/in/listener/internal/EventListener.kt`

---

## 5. 测试

> **Iron Law: NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.**
> 代码模板：`references/testing.md`。

### 5.1 TDD 适用范围判断

| 必须 TDD（RED-GREEN-REFACTOR） | 可跳过 TDD（直接实现） |
|--------------------------------|----------------------|
| `Entities.kt` — 领域实体，含业务规则 | `Vos.kt` / `Dtos.kt` / `Filters.kt` / `Views.kt` — 纯数据类 |
| `DomainService.kt` — 领域服务 | XML Mapper 文件 — 纯 SQL 映射 |
| `CommandHandler.kt` — 命令处理器 | `Controller.kt` — 薄适配器，仅转发 |
| `QueryHandler.kt` — 查询处理器 | `RestAssembler.kt` / `AppAssembler.kt` — 纯转换 |
| `ValueObjects.kt` — 含业务规则 | JPA Repository 接口 — 框架生成 |
| `Inputs.kt` — 含 `toEntity()` 转换逻辑 | `ErrorCode.kt` — 纯常量定义 |

### 5.2 测试覆盖率要求

| 测试类型 | 覆盖率 | Mock 策略 |
|----------|--------|----------|
| 领域实体测试 | ≥ 90% | 无 mock（纯领域对象） |
| 领域服务测试 | ≥ 80% | mock Repository |
| CommandHandler 测试 | ≥ 80% | mock Repository + DomainService |
| QueryHandler 测试 | ≥ 80% | mock Dao |
| 适配器层集成测试 | 与代码同 PR | Testcontainers + MySQL 8.0 |

### 5.3 不需要测试的内容

`Events.kt`、`ErrorCode.kt`、`Repository.kt`（接口）、`UseCase.kt`（接口）、`QueryCase.kt`（接口）、`Queries.kt`、`Dao.kt`（接口）、`Vos.kt`、`Dtos.kt`、`Views.kt`、`Filters.kt`

---

## 快速检查清单（apply 完成后逐项验证）

**领域层**
- [ ] 聚合根继承 `AbstractAuditableJpaEntity`（普通）或 `AbstractAuditableJpaTreeEntity`（树形），标注 `@Audited`
- [ ] 聚合根标注 `@AggregateRoot`，聚合内实体不标注
- [ ] ID 使用 `@Embeddable` data class + `SnowflakeGeneratorHelper.generate()`
- [ ] 领域事件继承 `AbstractDomainEvent`，使用 `@DomainEvent`，sealed class 封装（探索期可留空）
- [ ] Repository 接口继承 `IBaseDomainRepository`，标注 `@Repository` + `@SecondaryPort`
- [ ] DomainService 标注 `@Service`，Spec object 定义在同文件，不调 `save()`
- [ ] 领域方法不暴露 public constructor，使用 `create()` 工厂方法
- [ ] 若省略 `DomainService.getXxx`，已确认该模块无跨聚合校验

**API 层**
- [ ] 请求 VO 不继承基类（纯 data class），类名后缀大写 `VO`
- [ ] DTO 类名后缀大写 `DTO`，值对象字段已展开
- [ ] Filter 字段全部可空，不含校验注解
- [ ] View 字段与 MyBatis resultMap 一致

**应用层**
- [ ] UseCase / QueryCase 标注 `@PrimaryPort`，方法名统一 `handle`
- [ ] Commands 用 sealed class，标注 `@Command`，`toAttr()` 定义在同文件
- [ ] CommandHandler 实现 UseCase，标注 `@PrimaryAdapter` + `@Component` + `@Transactional`
- [ ] QueryHandler 实现 QueryCase，标注 `@PrimaryAdapter` + `@Component`，只注入 Dao
- [ ] Dao 接口标注 `@SecondaryPort`
- [ ] AppAssembler 使用 Kotlin 扩展函数，审计字段用 `.also {}` 赋值

**适配器层**
- [ ] JpaRepositories 继承 `IBaseJpaRepository` + `RevisionRepository`
- [ ] RepositoryAdapter 继承 `BaseJpaAdapter`，标注 `@SecondaryAdapter`
- [ ] Mappers 标注 `@Mapper`，一个聚合根一个 Mapper 接口
- [ ] Mapper XML 使用 `<sql>` 提取公共字段，`namespace` 与 Mapper 全限定名一致
- [ ] DaoAdapter 标注 `@SecondaryAdapter`，分页用 `PageHelper.startPage().doSelectPage().toPageResult()`
- [ ] Controller 标注 `@PrimaryAdapter` + `@RestController` + `@Tag`，只注入 UseCase / QueryCase
- [ ] Controller 每个方法标注 `@Operation` + `@ApiResponses`，参数标注 `@Parameter(description, example)`

**转换函数链**
- [ ] `VO.toCommand()` 定义在 `RestAssembler.kt`
- [ ] `Cmd.toAttr()` 定义在 `Commands.kt`
- [ ] `Attr.toEntity()` 定义在 `Inputs.kt`
- [ ] `Entity.toDto()` 定义在 `AppAssembler.kt`

**命名与代码规范**
- [ ] 类名后缀：大写 VO、大写 DTO（非 Vo、Dto）
- [ ] UseCase / QueryCase 方法名统一为 `handle`
- [ ] 所有新增或修改的代码，均已添加中文注释（类级、方法级、复杂业务点）
- [ ] 文件名不带业务前缀（`Entities.kt` 非 `DictEntity.kt`）

**测试**
- [ ] 领域实体测试覆盖率 ≥ 90%
- [ ] 领域服务测试覆盖率 ≥ 80%
- [ ] CommandHandler 测试覆盖率 ≥ 80%
- [ ] QueryHandler 测试覆盖率 ≥ 80%
- [ ] 使用 MockK、反引号命名风格
- [ ] 适配器层变更已编写对应的 `*IT.kt` 集成测试（JPA/MyBatis/REST 至少覆盖涉及层）
- [ ] Spec-测试覆盖检查通过：逐条对照 spec 场景，输出覆盖矩阵，确认无 MISSING
- [ ] `mvn verify` 通过（surefire 单元测试 + failsafe 集成测试全部通过）
